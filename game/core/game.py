import pygame
import os
from pathlib import Path    
from typing import List, Optional, Any

from game.world.map import GameMap
from game.core.camera import Camera
from game.entities.nexus import Nexus
from game.entities.tower import Tower
from game.entities.projectile import Projectile
from game.entities.minions import Minion
from game.entities.champion import Champion
from game.entities.entity import Entity
from game.ui.end_screen import EndScreen
from game.reseau.network import Network

class Game:
    """
    Manages the primary core orchestration logic for the MOBA game lifecycle.
    
    Coordinates client-side inputs, transmits authoritative states via the Network framework,
    spawns structural lane minion waves, processes collision bounds intersection,
    and drives the rendering viewport pipeline.
    """
    
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, sprite_prefix: str = "Vagabon", server_ip: str = "127.0.0.1"):
        """
        Initializes a new Game management sequence.

        Args:
            screen (pygame.Surface): Main window display workspace.
            clock (pygame.time.Clock): Game runtime tracking engine for framerate capping.
            sprite_prefix (str): Champion sprite prefix sent to the server during handshake.
        """
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.running: bool = True

        # Network Engine — sprite_prefix transmis pour le handshake complet
        self.net: Network = Network(sprite_prefix=sprite_prefix, server_ip=server_ip)
        self.my_id: Any = self.net.player_id

        # Entity Pipeline Containers
        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.remote_players: pygame.sprite.Group = pygame.sprite.Group()
        self.nexuses: pygame.sprite.Group = pygame.sprite.Group()

        # Map Layout and Collision Processing
        project_root = Path(__file__).parent.parent.parent
        map_path = os.path.join(project_root, "MAP", "MAP_1v1.tmx")
        self.game_map: GameMap = GameMap(map_path)

        # Viewport Camera
        self.camera: Camera = Camera(
            screen.get_width(), screen.get_height(),
            self.game_map.map_width, self.game_map.map_height
        )
        self.collisions_rects: List[pygame.Rect] = self.game_map.get_collision_rects()

        # Nexuses
        nexus_r_i = pygame.image.load("sprite/nexus_r.png")
        nexus_v_i = pygame.image.load("sprite/nexus_v.png")
        self.nexus_r = Nexus(253, 1240, 100, 100, nexus_r_i, "blue", hp=1000)
        self.nexus_v = Nexus(1220, 239, 140, 140, nexus_v_i, "red", hp=1000)
        self.add_entity(self.nexus_r, [self.nexuses])
        self.add_entity(self.nexus_v, [self.nexuses])
        # Towers
        self.towers = pygame.sprite.Group()
        self.tower_img = pygame.image.load("sprite/tourelle_bleue.png").convert_alpha()
        blue_tower = Tower(450, 1050, self.tower_img, "blue", hp= 500)
        self.add_entity(blue_tower, [self.towers])
        red_tower = Tower(1000, 400, self.tower_img, "red", hp=500)
        self.add_entity(red_tower, [self.towers])

        # Player is injected directly in game.py from main.py
        self.player: Optional[Champion] = None
        self.dt: float = 0.0
        self.dt_ms: float = 0.0

        # Minion Wave Spawner
        self.spawn_timer: float = 0.0
        self.wave_timer: float = 0.0
        self.minions_spawned_in_wave: int = 0
        self.wave_size: int = 4
        self.is_wave_active: bool = True

        # Graphic Assets
        self.blue_minion_img: pygame.Surface = pygame.image.load("sprite/test_sbire_blue.png").convert_alpha()
        self.red_minion_img: pygame.Surface = pygame.image.load("sprite/test_sbire_red.png").convert_alpha()
    
    def add_entity(self, entity: pygame.sprite.Sprite, groups: List[pygame.sprite.Group] = []) -> None:
        """
        Safely registers a game entity into the central rendering and processing groups.

        Args:
            entity (pygame.sprite.Sprite): The element instance to inject.
            groups (List[pygame.sprite.Group], optional): Auxiliary filters. Defaults to [].
        """
        if isinstance(entity, pygame.sprite.Sprite):
            self.all_sprites.add(entity)
            for group in groups:
                group.add(entity)
        else:
            print(f"Warning: {type(entity)} is not a supported Pygame Sprite component subclass!")
    
    def handle_event(self) -> None:
        """
        Captures hardware device events and translates them into network or application triggers.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_a
                    and self.player is not None
                    and self.player.alive):
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x / self.camera.zoom + self.camera.x
                world_mouse_y = mouse_y / self.camera.zoom + self.camera.y
                new_proj = self.player.process_attack_intent(world_mouse_x, world_mouse_y)
                if new_proj:
                    self.add_entity(new_proj, [self.projectiles])
    
    def _update_minion_spawning(self) -> None:
        """
        Calculates delta steps to execute procedural lane minion wave deployments.
        """
        self.spawn_timer += self.dt_ms
        if self.is_wave_active and self.minions_spawned_in_wave < self.wave_size:
            if self.spawn_timer > 800:
                blue_minion = Minion(253, 1240, 32, 32, self.blue_minion_img, "blue")
                self.add_entity(blue_minion, [self.enemies])
                red_minion = Minion(1232, 220, 32, 32, self.red_minion_img, "red")
                self.add_entity(red_minion, [self.enemies])
                self.minions_spawned_in_wave += 1
                self.spawn_timer = 0
        elif self.minions_spawned_in_wave >= self.wave_size:
            self.is_wave_active = False
            self.wave_timer += self.dt
            if self.wave_timer > 30.0:
                self.wave_timer = 0.0
                self.minions_spawned_in_wave = 0
                self.is_wave_active = True
    
    def update(self) -> None:
        """
        Executes real-time physics tracking, boundary constraint evaluations,
        and entity death cleanup sweeps.
        """
        # --- 1. Collecting locals inputs ---
        keys = pygame.key.get_pressed()
        inputs = {
            "z": keys[pygame.K_z],
            "q": keys[pygame.K_q],
            "s": keys[pygame.K_s],
            "d": keys[pygame.K_d],
            "b": keys[pygame.K_b]
        }

        # --- 2. Player movements with collisions ---
        # update_server_state() calcule le déplacement AABB et retourne dx/dy pour l'animation
        dx, dy = 0.0, 0.0
        if self.player is not None and self.player.alive:
            dx, dy = self.player.update_server_state(inputs, self.collisions_rects)
            self.player.update_client_animation(dx, dy)

        # --- 3. Synchronisation réseau : envoi inputs, réception positions adversaire ---
        server_state = self.net.send(inputs)
        if server_state:
            for player_key, player_data in server_state.items():
                if not player_key.startswith("player_"):
                    continue
                pid = int(player_key.split("_")[1])
                # Ne pas resynchroniser sa propre position — le client est autoritaire sur soi-même
                if pid == self.my_id:
                    continue
                # Chercher le champion adverse déjà spawné dans remote_players
                found = None
                for rp in self.remote_players:
                    if getattr(rp, "player_id", None) == pid:
                        found = rp
                        break
                if found:
                    # Calculer le déplacement pour animer le sprite dans la bonne direction
                    old_x, old_y = found.x, found.y
                    found.x = player_data["x"]
                    found.y = player_data["y"]
                    found.rect.x = int(found.x)
                    found.rect.y = int(found.y)
                    rdx = found.x - old_x
                    rdy = found.y - old_y
                    found.update_client_animation(rdx, rdy)
                else:
                    # Premier frame : spawn du champion adverse comme Champion
                    opp_prefix = player_data.get("sprite_prefix") or "Vagabon"
                    opponent = Champion(player_data["x"], player_data["y"], 5, "sprite", opp_prefix, 100)
                    opponent.player_id = pid
                    self.remote_players.add(opponent)
                    self.all_sprites.add(opponent)

        # --- 4. Spawn des vagues de minions ---
        self._update_minion_spawning()

        # --- 5. Mise à jour des minions : IA, pathfinding, attaques, collisions ---
        # all_entities_list sert au ciblage des minions (ils cherchent des ennemis dedans)
        all_entities_list = list(self.all_sprites) + list(self.nexuses)
        for entity in list(self.all_sprites):
            if isinstance(entity, Minion):
                entity.update_server_state(self.collisions_rects, all_entities_list)

        # --- 6. Mise à jour des projectiles : déplacement + collisions terrain + impacts ---
        # update_server_state() fait avancer le projectile et vérifie les murs
        for proj in list(self.projectiles):
            if not proj.alive:
                continue
            proj.update_server_state(self.collisions_rects)
            if not proj.alive:
                continue
            # Collision projectile → minions ennemis
            for enemy in list(self.enemies):
                if proj.rect.colliderect(enemy.rect):
                    enemy.take_damage(proj.damage)
                    proj.alive = False
                    break
            # Collision projectile → champion adverse
            if proj.alive:
                for rp in list(self.remote_players):
                    if proj.rect.colliderect(rp.rect):
                        rp.take_damage(proj.damage)
                        proj.alive = False
                        break
            # Collision projectile → nexus rouge (cible du joueur bleu)
            if proj.alive and proj.rect.colliderect(self.nexus_v.rect):
                self.nexus_v.take_damage(proj.damage)
                proj.alive = False

        # --- 7. Dégâts de contact : ennemis qui touchent le joueur ---
        if self.player is not None and self.player.alive:
            if pygame.sprite.spritecollide(self.player, self.enemies, False):
                self.player.take_damage(10)

        # --- 8. Nettoyage des entités mortes ---
        for entity in list(self.all_sprites):
            if hasattr(entity, "alive") and not entity.alive:
                entity.kill()

        # --- 9. Caméra : suivre le joueur ---
        if self.player is not None:
            self.camera.follow(self.player.get_rect())

        # --- 10. Conditions de fin de partie ---
        if (not self.nexus_v.alive
                or not self.nexus_r.alive
                or (self.player is not None and not self.player.alive)):
            self.running = False
    
    def draw(self) -> None:
        """
        Clears the workspace view matrix and blits active scene elements onto the frame layout.
        """
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera)
        for entity in self.all_sprites:
            entity.draw(self.screen, self.camera)
        pygame.display.flip()
    
    def _wait_for_players(self) -> bool:
        BG          = (8,   8,  20)
        CYAN        = (80, 220, 255)
        PURPLE      = (180,  80, 255)
        TEXT        = (220, 220, 255)
        SLOT_COLOR  = (40,  40,  80)
        SLOT_ACTIVE = (30,  60, 100)
        DIM         = (80,  80, 100)

        font_path = str(Path(__file__).parent.parent / "assets" / "font" / "Orbitron-Bold.ttf")
        try:
            f_title  = pygame.font.Font(font_path, 46)
            f_label  = pygame.font.Font(font_path, 22)
            f_champ  = pygame.font.Font(font_path, 28)
            f_hint   = pygame.font.Font(font_path, 20)
        except (FileNotFoundError, OSError):
            f_title  = pygame.font.SysFont("sans-serif", 46, bold=True)
            f_label  = pygame.font.SysFont("sans-serif", 22, bold=True)
            f_champ  = pygame.font.SysFont("sans-serif", 28, bold=True)
            f_hint   = pygame.font.SysFont("sans-serif", 20)

        dot_count = 0
        dot_timer = 0
        dummy_inputs = {"z": False, "q": False, "s": False, "d": False, "b": False}
        sw, sh = self.screen.get_width(), self.screen.get_height()

        while True:
            dt_ms = self.clock.tick(15)
            dot_timer += dt_ms
            if dot_timer >= 500:
                dot_count = (dot_count + 1) % 4
                dot_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False

            state = self.net.send(dummy_inputs)
            if state and state.get("ready"):
                return True

            # --- Draw ---
            self.screen.fill(BG)

            # Title
            title_surf = f_title.render("EN ATTENTE...", True, PURPLE)
            self.screen.blit(title_surf, title_surf.get_rect(centerx=sw // 2, y=80))

            # Two player slots side by side
            slot_w, slot_h = 320, 180
            gap = 60
            left_x  = sw // 2 - slot_w - gap // 2
            right_x = sw // 2 + gap // 2
            slot_y  = sh // 2 - slot_h // 2

            for i, slot_x in enumerate((left_x, right_x)):
                key = f"player_{i}"
                prefix = state[key]["sprite_prefix"] if state else ""
                connected = bool(prefix)
                is_me = (i == self.my_id)

                slot_rect = pygame.Rect(slot_x, slot_y, slot_w, slot_h)
                color = SLOT_ACTIVE if connected else SLOT_COLOR
                pygame.draw.rect(self.screen, color, slot_rect, border_radius=10)
                border_col = CYAN if connected else DIM
                pygame.draw.rect(self.screen, border_col, slot_rect, 2, border_radius=10)

                # Player label
                me_tag = "  (VOUS)" if is_me else ""
                label = f_label.render(f"JOUEUR {i + 1}{me_tag}", True, CYAN if is_me else TEXT)
                self.screen.blit(label, label.get_rect(centerx=slot_rect.centerx, y=slot_y + 20))

                # Champion or waiting dots
                if connected:
                    champ_surf = f_champ.render(prefix.upper(), True, CYAN)
                    self.screen.blit(champ_surf, champ_surf.get_rect(centerx=slot_rect.centerx, centery=slot_rect.centery + 10))
                    check = f_label.render("CONNECTE", True, CYAN)
                    self.screen.blit(check, check.get_rect(centerx=slot_rect.centerx, y=slot_y + slot_h - 42))
                else:
                    dots = "." * dot_count
                    wait_surf = f_label.render(f"EN ATTENTE{dots}", True, DIM)
                    self.screen.blit(wait_surf, wait_surf.get_rect(centerx=slot_rect.centerx, centery=slot_rect.centery + 10))

            hint = f_hint.render("ECHAP pour quitter", True, DIM)
            self.screen.blit(hint, hint.get_rect(centerx=sw // 2, y=sh - 80))

            pygame.display.flip()

    def run(self) -> str:
        """
        Maintains the operational application loop sequence runtime.

        Returns:
            str: Game outcome state flag identifier ('VICTORY', 'DEFEAT', or 'QUIT').
        """
        if not self._wait_for_players():
            return "QUIT"

        while self.running:
            # dt_ms : millisecondes brutes pour spawn_timer ; dt : secondes pour wave_timer
            self.dt_ms = self.clock.tick(60)
            self.dt = self.dt_ms / 1000.0
            self.handle_event()
            self.update()
            self.draw()
            if not self.nexus_v.alive or not self.nexus_r.alive:
                winner = "VICTORY" if not self.nexus_v.alive else "DEFEAT"
                end = EndScreen(self.screen, winner)
                end.draw()
                result = end.run()
                return result
        return "QUIT"