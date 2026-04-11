import pygame
import os
from pathlib import Path

from ...world.map import GameMap
from ...core.camera import Camera
from ...entities.nexus import Nexus
from ...entities.projectile import Projectile
from ...entities.minions import Minion
from ...entities.enemy import Enemy
from ...ui.end_screen import EndScreen
from protocols import Protocols


# ---------------------------------------------------------------------------
# Représentation locale du joueur adverse (léger, pas de logique de combat)
# ---------------------------------------------------------------------------

class RemotePlayer(pygame.sprite.Sprite):
    """
    Sprite minimaliste représentant l'adversaire réseau.
    Sa position est mise à jour depuis les paquets OPPONENT_UPDATE.
    Les dégâts ne sont jamais appliqués ici : ils sont résolus chez l'adversaire.
    """
    WIDTH  = 32
    HEIGHT = 48

    def __init__(self, x, y):
        super().__init__()
        # Corps simple coloré pour distinguer l'adversaire
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (220, 60, 60),
                         (0, 10, self.WIDTH, self.HEIGHT - 10), border_radius=4)
        pygame.draw.circle(self.image, (255, 190, 190), (self.WIDTH // 2, 8), 9)
        # Petit indicateur "ennemi"
        pygame.draw.rect(self.image, (255, 50, 50), (8, 0, 16, 4))

        self.rect  = self.image.get_rect(topleft=(x, y))
        self.alive = True

    def update_position(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def get_rect(self):
        return self.rect

    def draw(self, screen, camera):
        screen.blit(self.image, camera.apply(self.rect))

    def update(self, *args, **kwargs):
        pass  # le mouvement est piloté par le réseau uniquement

    def take_damage(self, amount):
        pass  # géré chez l'adversaire


# ---------------------------------------------------------------------------
# Classe de jeu principale (supporte le solo ET le multijoueur)
# ---------------------------------------------------------------------------

class Game:
    # Points de spawn par équipe
    SPAWN_BLUE = (253, 1240)
    SPAWN_RED  = (1232, 220)

    def __init__(self, screen, clock, client=None, player_id=1):
        """
        Parameters
        ----------
        screen    : pygame.Surface
        clock     : pygame.time.Clock
        client    : Client | None
            Instance de Client (client.py). Si None → mode solo.
        player_id : int (1 ou 2)
            1 = équipe bleue (bas de carte), attaque le nexus rouge.
            2 = équipe rouge (haut de carte), attaque le nexus bleu.
        """
        self.screen    = screen
        self.clock     = clock
        self.client    = client
        self.player_id = player_id
        self.running   = True

        # Groupes de sprites
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemies     = pygame.sprite.Group()
        self.nexuses     = pygame.sprite.Group()

        # Carte & caméra
        project_root = Path(__file__).parent.parent.parent
        map_path = os.path.join(project_root, "MAP", "MAP_1v1.tmx")
        self.game_map = GameMap(map_path)
        self.camera   = Camera(screen.get_width(), screen.get_height(),
                               self.game_map.map_width, self.game_map.map_height)
        self.collisions_rects = self.game_map.get_collision_rects()

        # Nexus
        self.nexus_r = Nexus(253, 1240, 100, 100, "sprite/nexus_r.png", hp=1000)
        self.nexus_r.team = "blue"
        self.nexus_v = Nexus(1232, 220, 128, 128, "sprite/nexus_v.png", hp=1000)
        self.nexus_v.team = "red"
        self.add_entity(self.nexus_r, [self.nexuses])
        self.add_entity(self.nexus_v, [self.nexuses])

        # Joueurs
        self.player        = None   # défini depuis l'extérieur avant run()
        self.remote_player = None   # créé dans run() si mode multijoueur

        self.dt = 0

        # Vagues de sbires
        self.spawn_timer             = 0
        self.wave_timer              = 0
        self.minions_spawned_in_wave = 0
        self.wave_size               = 4
        self.is_wave_active          = True
        self.blue_minion_img = pygame.image.load("sprite/test_sbire_blue.png").convert_alpha()
        self.red_minion_img  = pygame.image.load("sprite/test_sbire_red.png").convert_alpha()

        # Réseau
        self.network_update_timer    = 0
        self.NETWORK_UPDATE_INTERVAL = 50  # ms entre deux envois de position

    # ------------------------------------------------------------------
    # Helpers internes
    # ------------------------------------------------------------------

    def add_entity(self, entity, groups=None):
        if groups is None:
            groups = []
        if isinstance(entity, pygame.sprite.Sprite):
            self.all_sprites.add(entity)
            for group in groups:
                group.add(entity)
        else:
            print(f"Attention : {type(entity)} n'est pas un Sprite Pygame !")

    def _enemy_nexus(self):
        """Nexus que le joueur local doit attaquer."""
        return self.nexus_v if self.player_id == 1 else self.nexus_r

    def _friendly_nexus(self):
        """Nexus que le joueur local doit défendre."""
        return self.nexus_r if self.player_id == 1 else self.nexus_v

    # ------------------------------------------------------------------
    # Couche réseau
    # ------------------------------------------------------------------

    def _send_player_update(self):
        """Envoie la position du joueur local au serveur."""
        if not self.client or not self.player:
            return
        self.client.send(Protocols.Request.PLAYER_UPDATE, {
            "x":     self.player.rect.x,
            "y":     self.player.rect.y,
            "alive": bool(self.player.alive),
        })

    def _send_projectile(self, proj):
        """Notifie le serveur qu'un projectile a été tiré."""
        if not self.client:
            return
        self.client.send(Protocols.Request.PROJECTILE_FIRED, {
            "x":      proj.rect.x,
            "y":      proj.rect.y,
            "dx":     getattr(proj, "dx", 0),
            "dy":     getattr(proj, "dy", 0),
            "damage": getattr(proj, "damage", 10),
        })

    def _send_nexus_hit(self, nexus_team, damage):
        """Informe le serveur (et donc l'adversaire) d'un dégât sur un nexus."""
        if not self.client:
            return
        self.client.send(Protocols.Request.NEXUS_HIT, {
            "nexus":  nexus_team,
            "damage": damage,
        })

    def _handle_network_messages(self):
        """Consomme la file de messages réseau et applique les mises à jour."""
        if not self.client:
            return

        for msg in self.client.get_messages():
            r_type = msg.get("type")
            data   = msg.get("data", {})

            # --- Mise à jour position adversaire ---
            if r_type == Protocols.Response.OPPONENT_UPDATE:
                if self.remote_player:
                    self.remote_player.update_position(data["x"], data["y"])

            # --- Projectile tiré par l'adversaire ---
            elif r_type == Protocols.Response.OPPONENT_PROJECTILE:
                try:
                    proj = Projectile(
                        data["x"], data["y"],
                        data.get("dx", 0), data.get("dy", 0),
                        damage=data.get("damage", 10),
                    )
                    self.add_entity(proj, [self.projectiles])
                except Exception as e:
                    print(f"[Network] Erreur création projectile adverse : {e}")

            # --- Dégâts sur un nexus (appliqués localement pour la sync) ---
            elif r_type == Protocols.Response.NEXUS_DAMAGE:
                nexus_team = data.get("nexus")
                damage     = data.get("damage", 0)
                if nexus_team == "red":
                    self.nexus_v.take_damage(damage)
                elif nexus_team == "blue":
                    self.nexus_r.take_damage(damage)

    # ------------------------------------------------------------------
    # Boucle de jeu
    # ------------------------------------------------------------------

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_a:
                    proj_data = self.player.attack(self.camera)
                    if proj_data:
                        self.add_entity(proj_data, [self.projectiles])
                        # --- MULTIJOUEUR : informer l'adversaire du tir ---
                        self._send_projectile(proj_data)

    def update(self):
        self.dt = self.clock.tick(60) / 1000.0

        # ---- Vagues de sbires ----------------------------------------
        self.spawn_timer += self.dt * 1000
        if self.is_wave_active and self.minions_spawned_in_wave < self.wave_size:
            if self.spawn_timer > 800:
                blue_minion = Minion(253, 1240, 32, 32, self.blue_minion_img, "blue")
                self.add_entity(blue_minion, [self.enemies])
                red_minion  = Minion(1232, 220, 32, 32, self.red_minion_img,  "red")
                self.add_entity(red_minion, [self.enemies])
                self.minions_spawned_in_wave += 1
                self.spawn_timer = 0
        elif self.minions_spawned_in_wave >= self.wave_size:
            self.is_wave_active = False
            self.wave_timer += self.dt
            if self.wave_timer > 30:  # 30 secondes entre les vagues
                self.wave_timer              = 0
                self.minions_spawned_in_wave = 0
                self.is_wave_active          = True

        # ---- Mise à jour des sprites ----------------------------------
        obstacles = self.collisions_rects + [n.get_rect() for n in self.nexuses]
        self.all_sprites.update(None, obstacles, list(self.all_sprites))

        # ---- Collisions projectiles ----------------------------------
        enemy_nexus = self._enemy_nexus()
        for proj in list(self.projectiles):
            # Touche un ennemi
            for enemy in pygame.sprite.spritecollide(proj, self.enemies, False):
                enemy.take_damage(proj.damage)
                proj.alive = False

            # Touche le nexus ennemi local
            if proj.rect.colliderect(enemy_nexus.rect):
                enemy_nexus.take_damage(proj.damage)
                # --- MULTIJOUEUR : synchroniser les HP chez l'adversaire ---
                self._send_nexus_hit(enemy_nexus.team, proj.damage)
                proj.alive = False

        # ---- Dégâts du joueur au contact des ennemis -----------------
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.player.take_damage(10)

        # ---- Suppression des entités mortes --------------------------
        for entity in list(self.all_sprites):
            if hasattr(entity, "alive") and not entity.alive:
                entity.kill()

        # ---- Caméra --------------------------------------------------
        self.camera.follow(self.player.get_rect())

        # ---- Condition de fin ----------------------------------------
        if not self.nexus_v.alive or not self.nexus_r.alive or not self.player.alive:
            self.running = False

        # ---- Réseau (envoi position + réception messages) -----------
        if self.client:
            self.network_update_timer += self.dt * 1000
            if self.network_update_timer >= self.NETWORK_UPDATE_INTERVAL:
                self._send_player_update()
                self.network_update_timer = 0
            self._handle_network_messages()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera)
        for entity in self.all_sprites:
            entity.draw(self.screen, self.camera)
        # Le joueur adverse est affiché par-dessus (non inclus dans all_sprites
        # pour éviter les collisions locales indésirables)
        if self.remote_player:
            self.remote_player.draw(self.screen, self.camera)
        pygame.display.flip()

    def run(self):
        # En mode multijoueur : créer le RemotePlayer au spawn adverse
        if self.client and self.remote_player is None:
            remote_spawn = self.SPAWN_RED if self.player_id == 1 else self.SPAWN_BLUE
            self.remote_player = RemotePlayer(*remote_spawn)

        while self.running:
            self.handle_events()
            self.update()
            self.draw()

            # Vérifier la fin de partie après l'update
            if not self.nexus_v.alive or not self.nexus_r.alive:
                enemy_nexus = self._enemy_nexus()
                winner = "VICTORY" if not enemy_nexus.alive else "DEFEAT"
                end    = EndScreen(self.screen, winner)
                end.draw()
                return end.run()

        return "QUIT"
