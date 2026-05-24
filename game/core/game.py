import pygame
from typing import List, Optional, Any

from game.utils import resource_path
from game.world.map import GameMap
from game.ui.hud import HUD
from game.core.camera import Camera
from game.entities.nexus import Nexus
from game.entities.tower import Tower
from game.entities.minions import Minion
from game.entities.champion import Champion
from game.entities.projectile import Projectile
from game.ui.end_screen import EndScreen
from game.reseau.network import Network

_XP_MINION = 20       # XP awarded when a nearby enemy minion dies
_XP_CHAMPION = 150    # XP awarded on champion kill
_XP_RANGE = 300.0     # Max distance to collect minion XP

_RECALL_DURATION_MS: float = 3000.0
_SPAWN_POS = {0: (120.0, 1430.0), 1: (1464.0, 103.0)}

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
        self.game_map: GameMap = GameMap(resource_path("MAP/MAP_1v1.tmx"))

        # Viewport Camera
        self.camera: Camera = Camera(
            screen.get_width(), screen.get_height(),
            self.game_map.map_width, self.game_map.map_height
        )
        self.collisions_rects: List[pygame.Rect] = self.game_map.get_collision_rects()
        # Pure terrain walls for projectile collision — structures (towers, nexuses) excluded
        # so projectiles can reach explicit damage checks instead of dying silently on contact.
        self.wall_rects: List[pygame.Rect] = list(self.collisions_rects)

        # Nexuses
        nexus_r_i = pygame.image.load(resource_path("sprite/nexus_r.png"))
        nexus_v_i = pygame.image.load(resource_path("sprite/nexus_v.png"))
        self.nexus_r = Nexus(253, 1240, 100, 100, nexus_r_i, "blue", hp=1000)
        self.nexus_v = Nexus(1220, 239, 140, 140, nexus_v_i, "red", hp=1000)
        self.add_entity(self.nexus_r, [self.nexuses])
        self.add_entity(self.nexus_v, [self.nexuses])
        self.collisions_rects.append(self.nexus_r.rect)
        self.collisions_rects.append(self.nexus_v.rect)
        # Towers
        self.towers = pygame.sprite.Group()
        tower_r_img = pygame.image.load(resource_path("sprite/Tower_R.png")).convert_alpha()
        tower_v_img = pygame.image.load(resource_path("sprite/Tower_V.png")).convert_alpha()
        self.tower_blue_1 = Tower(415, 1005, tower_r_img, "blue", hp=500)
        self.tower_blue_2 = Tower(575, 845, tower_r_img, "blue", hp=500)
        self.tower_red_1 = Tower(1100, 480, tower_v_img, "red", hp=500)
        self.tower_red_2 = Tower(940, 640, tower_v_img, "red", hp=500)
        for t in [self.tower_blue_1, self.tower_blue_2, self.tower_red_1, self.tower_red_2]:
            self.add_entity(t, [self.towers])
            self.collisions_rects.append(t.rect)
        self._tower_keys = {
            self.tower_blue_1: "tower_blue_1",
            self.tower_blue_2: "tower_blue_2",
            self.tower_red_1: "tower_red_1",
            self.tower_red_2: "tower_red_2",
        }
        # Minion collision rects: terrain only — towers and nexuses are passable for minions.
        # Nexuses are excluded because minions spawn inside their own nexus rect; keeping them
        # in the list causes the AABB to push red minions to x=1360 (right of nexus_v), which
        # sends them on a deviated path that hits map terrain walls near tower_red_1.
        _excluded_rect_ids = (
            {id(t.rect) for t in [self.tower_blue_1, self.tower_blue_2, self.tower_red_1, self.tower_red_2]}
            | {id(self.nexus_r.rect), id(self.nexus_v.rect)}
        )
        self.minion_collision_rects = [r for r in self.collisions_rects if id(r) not in _excluded_rect_ids]
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

        # HUD and match stats
        self.hud: HUD = HUD(screen)
        self.game_start_ms: int = 0
        self.kills: int = 0
        self.deaths: int = 0

        # Projectile spawns to relay to server this frame
        self._new_proj_spawns: list = []

        # Respawn system
        self.is_respawning: bool = False
        self.respawn_timer_ms: float = 0.0
        self.pending_respawn: bool = False

        # Recall system
        self.is_recalling: bool = False
        self.recall_elapsed_ms: float = 0.0

        # Minion sync (player 0 = authority)
        self.minion_id_counter: int = 0
        self._remote_minions: dict = {}  # id → Minion instance, used by player 1 only
        font_path = resource_path("game/assets/font/Orbitron-Bold.ttf")
        try:
            self.f_death     = pygame.font.Font(font_path, 54)
            self.f_respawn_cd = pygame.font.Font(font_path, 30)
        except (FileNotFoundError, OSError):
            self.f_death     = pygame.font.SysFont("sans-serif", 54, bold=True)
            self.f_respawn_cd = pygame.font.SysFont("sans-serif", 30, bold=True)
    
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

            if event.type == pygame.KEYDOWN and self.player is not None and self.player.alive:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mx = mouse_x / self.camera.zoom + self.camera.x
                world_my = mouse_y / self.camera.zoom + self.camera.y

                if event.key == pygame.K_a:
                    proj = self.player.process_attack_intent(world_mx, world_my)
                    if proj:
                        proj.team = self.player.team
                        self.add_entity(proj, [self.projectiles])
                        self._new_proj_spawns.append(self._proj_to_dict(proj))

                elif event.key == pygame.K_e and self.player.ability_q:
                    projs = self.player.ability_q.try_use(self.player, world_mx, world_my)
                    if projs:
                        for p in projs:
                            p.team = self.player.team
                            self.add_entity(p, [self.projectiles])
                            self._new_proj_spawns.append(self._proj_to_dict(p))

                elif event.key == pygame.K_r and self.player.ability_e:
                    projs = self.player.ability_e.try_use(self.player, world_mx, world_my)
                    if projs:
                        for p in projs:
                            p.team = self.player.team
                            self.add_entity(p, [self.projectiles])
                            self._new_proj_spawns.append(self._proj_to_dict(p))

                elif event.key == pygame.K_b:
                    if self.is_recalling:
                        self.is_recalling = False
                        self.recall_elapsed_ms = 0.0
                    else:
                        self.is_recalling = True
                        self.recall_elapsed_ms = 0.0
                elif event.key == pygame.K_x:
                    print(f"{self.tower_blue_1.width}, {self.tower_blue_1.height}, {self.tower_red_1.width}, {self.tower_red_1.height}")
    
    def _update_minion_spawning(self) -> None:
        """
        Calculates delta steps to execute procedural lane minion wave deployments.
        Only called by player 0 (the minion authority).
        """
        self.spawn_timer += self.dt_ms
        if self.is_wave_active and self.minions_spawned_in_wave < self.wave_size:
            if self.spawn_timer > 800:
                blue_minion = Minion(353, 1340, "blue")
                blue_minion.minion_id = self.minion_id_counter
                self.minion_id_counter += 1
                self.add_entity(blue_minion, [self.enemies])
                red_minion = Minion(1360, 379, "red")
                red_minion.minion_id = self.minion_id_counter
                self.minion_id_counter += 1
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
        # --- 1. Inputs ---
        keys = pygame.key.get_pressed()
        inputs = {
            "z": keys[pygame.K_z],
            "q": keys[pygame.K_q],
            "s": keys[pygame.K_s],
            "d": keys[pygame.K_d],
        }

        # --- 1b. Recall channel ---
        if self.is_recalling and self.player is not None:
            if not self.player.alive:
                self.is_recalling = False
                self.recall_elapsed_ms = 0.0
            elif inputs.get("z") or inputs.get("q") or inputs.get("s") or inputs.get("d"):
                self.is_recalling = False
                self.recall_elapsed_ms = 0.0
            else:
                self.recall_elapsed_ms += self.dt_ms
                if self.recall_elapsed_ms >= _RECALL_DURATION_MS:
                    self.is_recalling = False
                    self.recall_elapsed_ms = 0.0
                    spawn = _SPAWN_POS.get(self.my_id, (120.0, 1430.0))
                    self.player.x = spawn[0]
                    self.player.y = spawn[1]
                    self.player.rect.x = int(spawn[0])
                    self.player.rect.y = int(spawn[1])
                    heal = self.player.max_hp - self.player.hp
                    if heal > 0:
                        self.player.hp = self.player.max_hp
                        self.player.pending_heal = heal

        # --- 2. Player movement with collisions (frozen during recall) ---
        dx, dy = 0.0, 0.0
        if self.player is not None and self.player.alive and not self.is_recalling:
            dx, dy = self.player.update_server_state(inputs, self.collisions_rects)
            self.player.update_client_animation(dx, dy)

        # --- 3. Projectiles : movement + hit collection ---
        hits_this_frame: list = []
        for proj in list(self.projectiles):
            if not proj.alive:
                continue
            proj.update_server_state(self.wall_rects)
            if not proj.alive:
                continue

            if proj.is_ghost:
                # Ghost = visual replica of an enemy projectile; damage is already
                # handled server-side by the remote client. Just disappear on contact.
                if self.player is not None and self.player.alive:
                    if proj.rect.colliderect(self.player.rect):
                        proj.alive = False
                if proj.alive:
                    for nexus in self.nexuses:
                        if proj.rect.colliderect(nexus.rect):
                            proj.alive = False
                            break
                if proj.alive:
                    for tower in self.towers:
                        if tower.alive and tower.team != proj.team and proj.rect.colliderect(tower.rect):
                            proj.alive = False
                            break
                continue

            # Collision → minion enemies (enemy team only)
            # Player 0 applies damage locally (minion authority).
            # Player 1 relays hit to server so player 0 can apply it authoritatively.
            for enemy in list(self.enemies):
                if getattr(enemy, 'team', '') != proj.team and proj.rect.colliderect(enemy.rect):
                    if self.my_id == 0:
                        enemy.take_damage(proj.damage)
                    else:
                        hits_this_frame.append({"minion_id": enemy.minion_id, "damage": proj.damage})
                    proj.alive = False
                    break
            # Collision → remote champion : report hit to server
            if proj.alive:
                for rp in list(self.remote_players):
                    if proj.rect.colliderect(rp.rect):
                        now = pygame.time.get_ticks()
                        curse_mult = rp.curse_multiplier if now < rp.curse_end_ms else 1.0
                        dmg = int(proj.damage * curse_mult)
                        hits_this_frame.append({"target_id": rp.player_id, "damage": dmg})
                        if proj.is_curse:
                            rp.curse_multiplier = 2.0
                            rp.curse_end_ms = now + proj.curse_duration_ms
                        proj.alive = False
                        break
            # Collision → nexus (team-based, server-authoritative via hit event)
            # Tower chain: nexus only takes damage when all protecting towers are destroyed.
            if proj.alive and proj.team:
                enemy_nexus = self.nexus_r if proj.team == "red" else self.nexus_v
                enemy_nexus_key = "nexus_r" if proj.team == "red" else "nexus_v"
                own_nexus = self.nexus_v if proj.team == "red" else self.nexus_r
                if proj.rect.colliderect(enemy_nexus.rect):
                    if proj.team == "red":
                        protecting_alive = self.tower_blue_1.alive or self.tower_blue_2.alive
                    else:
                        protecting_alive = self.tower_red_1.alive or self.tower_red_2.alive
                    if not protecting_alive:
                        hits_this_frame.append({"target": enemy_nexus_key, "damage": proj.damage})
                    proj.alive = False  # Always blocked by nexus, damage only when all towers down
                elif proj.rect.colliderect(own_nexus.rect):
                    proj.alive = False  # Blocked by own nexus, no damage
            # Collision → towers (HP server-authoritative via hit event)
            if proj.alive and proj.team:
                for tower in list(self.towers):
                    if not tower.alive:
                        continue
                    if proj.rect.colliderect(tower.rect):
                        if tower.team != proj.team:
                            hits_this_frame.append({"target": self._tower_keys[tower], "damage": proj.damage})
                        proj.alive = False
                        break

        # --- 4. Minion contact damage (enemy team only, reported to server) ---
        if self.player is not None and self.player.alive:
            enemy_minions = [e for e in self.enemies
                             if getattr(e, "team", "") != self.player.team]
            touching = [e for e in enemy_minions if self.player.rect.colliderect(e.rect)]
            if touching:
                now = pygame.time.get_ticks()
                if now - self.player.last_hit_time >= self.player.next_hit_cooldown:
                    self.player.last_hit_time = now
                    if self.my_id is not None:
                        hits_this_frame.append({"target_id": self.my_id, "damage": touching[0].damage})

        # --- 4b. Tower AI ---
        # Towers target: enemy minions (local damage) and champions (hit events).
        # Each client only reports tower hits on the LOCAL player to avoid double-counting —
        # the remote client handles hits on itself from the same tower.
        # Player 1 excludes synced minions from tower targets: their lifecycle is controlled
        # by player 0, so local tower kills would cause flickering.
        if self.my_id == 0:
            tower_targets = list(self.enemies) + list(self.remote_players)
        else:
            tower_targets = list(self.remote_players)
        if self.player is not None:
            tower_targets.append(self.player)
        for tower in list(self.towers):
            if not tower.alive:
                continue
            champ_hits = tower.update_server_state(tower_targets)
            for (target, dmg) in champ_hits:
                if target is self.player and self.my_id is not None:
                    hits_this_frame.append({"target_id": self.my_id, "damage": dmg})
                # Remote player hits discarded: the remote client self-reports them

        # --- 5. Minion waves + AI (player 0 only) ---
        # Must run before the network send so minion hits land in the same frame's packet.
        # Player 0 is the minion authority: it spawns, simulates, and relays minion state.
        # Player 1 receives positions from the server and does not run local AI.
        if self.my_id == 0:
            self._update_minion_spawning()
            # All sprites are valid targets so enemy minions can aggro the local player
            minion_targets = list(self.all_sprites)
            minion_list = [e for e in list(self.all_sprites) if isinstance(e, Minion)]
            minion_rects_snap = [e.rect.copy() for e in minion_list]
            for i, entity in enumerate(minion_list):
                other_minion_rects = [r for j, r in enumerate(minion_rects_snap) if j != i]
                combined_rects = self.minion_collision_rects + other_minion_rects
                hits = entity.update_server_state(combined_rects, minion_targets)
                entity.update_client_animation(entity.last_dx, entity.last_dy)
                for (target, dmg) in hits:
                    if target in self._tower_keys:
                        hits_this_frame.append({"target": self._tower_keys[target], "damage": dmg})
                    elif target is self.player and self.my_id is not None:
                        now = pygame.time.get_ticks()
                        if now - self.player.last_hit_time >= self.player.next_hit_cooldown:
                            self.player.last_hit_time = now
                            hits_this_frame.append({"target_id": self.my_id, "damage": dmg})
                    elif hasattr(target, 'player_id'):
                        hits_this_frame.append({"target_id": target.player_id, "damage": dmg})
                    elif isinstance(target, Minion):
                        target.take_damage(dmg)

        # --- 6. Network : send position + inputs + hits + respawn flag, receive global state ---
        packet = dict(inputs)
        if self.player is not None:
            packet["x"] = self.player.x
            packet["y"] = self.player.y
        if hits_this_frame:
            packet["hits"] = hits_this_frame
        if self.pending_respawn:
            packet["respawn"] = True
            self.pending_respawn = False
        if self.player is not None and self.player.pending_heal > 0:
            packet["self_heal"] = self.player.pending_heal
            packet["self_max_hp"] = self.player.max_hp
            self.player.pending_heal = 0
        packet["new_projectiles"] = self._new_proj_spawns
        self._new_proj_spawns = []
        # Player 0 is the minion authority — relay all minion states to server
        if self.my_id == 0:
            packet["minion_states"] = [
                {"id": e.minion_id, "x": e.x, "y": e.y, "hp": e.hp, "team": e.team, "alive": e.alive}
                for e in self.all_sprites if isinstance(e, Minion)
            ]
        server_state = self.net.send(packet)
        if server_state is None:
            self._disconnected = True
            self.running = False
            return

        if server_state:
            for player_key, player_data in server_state.items():
                if not player_key.startswith("player_"):
                    continue
                pid = int(player_key.split("_")[1])
                server_hp = player_data["hp"]

                if self.my_id is not None and pid == self.my_id:
                    # Sync own HP from server (damage applied by opponent or minions)
                    if self.player is not None:
                        was_alive = self.player.alive
                        self.player.hp = server_hp
                        if self.player.hp <= 0:
                            self.player.hp = 0
                            self.player.alive = False
                            if was_alive:
                                self.deaths += 1
                    continue

                # Remote player : update position + HP
                found = None
                for rp in self.remote_players:
                    if getattr(rp, "player_id", None) == pid:
                        found = rp
                        break
                remote_champ = None
                if found:
                    old_x, old_y = found.x, found.y
                    found.x = player_data["x"]
                    found.y = player_data["y"]
                    found.rect.x = int(found.x)
                    found.rect.y = int(found.y)
                    rdx = found.x - old_x
                    rdy = found.y - old_y
                    found.update_client_animation(rdx, rdy)
                    found.max_hp = player_data.get("max_hp", found.max_hp)
                    was_alive = found.alive
                    found.hp = server_hp
                    if found.hp <= 0:
                        found.hp = 0
                        found.alive = False
                        if was_alive:
                            self.kills += 1
                            self.hud.push_kill(self.kills)
                            if self.player is not None:
                                self.player.add_xp(_XP_CHAMPION)
                    elif not found.alive:
                        found.alive = True  # Remote player respawned
                    remote_champ = found
                elif server_hp > 0:
                    # Only spawn remote entity if alive (prevents kill-counter loop while dead)
                    opp_prefix = player_data.get("sprite_prefix") or "Vagabon"
                    opp_max_hp = player_data.get("max_hp", 100)
                    opponent = Champion(player_data["x"], player_data["y"], 5, "sprite", opp_prefix, opp_max_hp)
                    opponent.player_id = pid
                    opponent.team = "blue" if pid == 0 else "red"
                    opponent.hp = server_hp
                    self.remote_players.add(opponent)
                    self.all_sprites.add(opponent)
                    remote_champ = opponent

                # Spawn ghost projectiles for shots fired by the remote player this frame
                if remote_champ is not None:
                    for pd in player_data.get("new_projectiles", []):
                        ghost = Projectile(
                            pd["x"], pd["y"], pd["dx"], pd["dy"],
                            pd["speed"], pd["damage"], pd["range"],
                            remote_champ.bullet_asset,
                        )
                        ghost.is_ghost = True
                        ghost.team = remote_champ.team
                        ghost.is_curse = pd.get("is_curse", False)
                        ghost.curse_duration_ms = pd.get("curse_duration_ms", 0)
                        self.add_entity(ghost, [self.projectiles])

            # Sync nexus HP from server
            nexus_r_hp = server_state.get("nexus_r_hp")
            if nexus_r_hp is not None:
                self.nexus_r.hp = nexus_r_hp
                if self.nexus_r.hp <= 0:
                    self.nexus_r.hp = 0
                    self.nexus_r.alive = False
            nexus_v_hp = server_state.get("nexus_v_hp")
            if nexus_v_hp is not None:
                self.nexus_v.hp = nexus_v_hp
                if self.nexus_v.hp <= 0:
                    self.nexus_v.hp = 0
                    self.nexus_v.alive = False

            # Player 1: sync minion positions/HP from server (player 0 is the authority)
            if self.my_id != 0:
                minion_states = server_state.get("minions", [])
                received_ids = {s["id"] for s in minion_states}
                for state in minion_states:
                    mid = state["id"]
                    if mid not in self._remote_minions:
                        team = state["team"]
                        m = Minion(state["x"], state["y"], team)
                        m.minion_id = mid
                        self.add_entity(m, [self.enemies])
                        self._remote_minions[mid] = m
                    else:
                        m = self._remote_minions[mid]
                        dx = state["x"] - m.x
                        dy = state["y"] - m.y
                        m.x = state["x"]
                        m.y = state["y"]
                        m.hp = state["hp"]
                        m.rect.x = int(m.x)
                        m.rect.y = int(m.y)
                        m.update_client_animation(dx, dy)
                # Remove minions player 0 has already cleaned up
                for mid in list(self._remote_minions):
                    if mid not in received_ids:
                        self._remote_minions[mid].alive = False
                        del self._remote_minions[mid]

            # Player 0: apply minion hits reported by player 1
            if self.my_id == 0:
                for mhit in server_state.get("minion_hits", []):
                    mid = mhit.get("minion_id")
                    dmg = mhit.get("damage", 0)
                    for e in list(self.all_sprites):
                        if isinstance(e, Minion) and e.minion_id == mid:
                            e.take_damage(dmg)
                            break

            # Sync tower HP from server
            for _tkey, _tower in [
                ("tower_blue_1_hp", self.tower_blue_1), ("tower_blue_2_hp", self.tower_blue_2),
                ("tower_red_1_hp", self.tower_red_1),   ("tower_red_2_hp", self.tower_red_2),
            ]:
                _hp = server_state.get(_tkey)
                if _hp is not None:
                    _tower.hp = _hp
                    if _tower.hp <= 0:
                        _tower.hp = 0
                        _tower.alive = False

        # --- 7. Respawn management ---
        if self.is_respawning:
            self.respawn_timer_ms -= self.dt_ms
            if self.respawn_timer_ms <= 0:
                self._do_respawn()
        elif self.player is not None and not self.player.alive:
            self._start_respawn()

        # --- 8. Entity cleanup (player excluded — managed by respawn system) ---
        for entity in list(self.all_sprites):
            if entity is self.player:
                continue
            if hasattr(entity, "alive") and not entity.alive:
                if (isinstance(entity, Minion)
                        and self.player is not None and self.player.alive
                        and pygame.math.Vector2(entity.x - self.player.x, entity.y - self.player.y).length() <= _XP_RANGE):
                    self.player.add_xp(_XP_MINION)
                if entity.rect in self.collisions_rects:
                    self.collisions_rects.remove(entity.rect)
                entity.kill()

        # --- 9. Camera ---
        if self.player is not None:
            self.camera.follow(self.player.get_rect())

        # --- 10. End conditions : only nexus destruction ends the game ---
        if not self.nexus_v.alive or not self.nexus_r.alive:
            self.running = False
    
    def draw(self) -> None:
        """
        Clears the workspace view matrix and blits active scene elements onto the frame layout.
        """
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera)
        for entity in self.all_sprites:
            if entity is self.player and not entity.alive:
                continue  # Don't draw dead local player
            entity.draw(self.screen, self.camera)

        # Curse indicator: purple border on cursed remote players
        now = pygame.time.get_ticks()
        for rp in self.remote_players:
            if now < rp.curse_end_ms:
                sx, sy = self.camera.apply_pos(rp.x, rp.y)
                w = int(rp.width * self.camera.zoom) + 4
                h = int(rp.height * self.camera.zoom) + 4
                pygame.draw.rect(self.screen, (180, 80, 255),
                                pygame.Rect(sx - 2, sy - 2, w, h), 2, border_radius=3)

        if self.player is not None:
            self.hud.draw(self.player, self.game_start_ms, self.kills, self.deaths)
            if self.is_recalling:
                self.hud.draw_recall(self.recall_elapsed_ms, _RECALL_DURATION_MS)

        if self.is_respawning:
            sw, sh = self.screen.get_width(), self.screen.get_height()
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            dead_surf = self.f_death.render("MORT", True, (255, 60, 60))
            self.screen.blit(dead_surf, dead_surf.get_rect(centerx=sw // 2, centery=sh // 2 - 50))
            remaining_s = max(0.0, self.respawn_timer_ms / 1000.0)
            cd_surf = self.f_respawn_cd.render(f"Respawn dans  {remaining_s:.1f}s", True, (220, 220, 255))
            self.screen.blit(cd_surf, cd_surf.get_rect(centerx=sw // 2, centery=sh // 2 + 20))

        pygame.display.flip()
    
    @staticmethod
    def _proj_to_dict(proj) -> dict:
        return {
            "x": proj.x, "y": proj.y,
            "dx": proj.dx, "dy": proj.dy,
            "speed": proj.speed, "damage": proj.damage,
            "range": proj.range,
            "is_curse": proj.is_curse,
            "curse_duration_ms": proj.curse_duration_ms,
        }

    def _start_respawn(self) -> None:
        elapsed_s = (pygame.time.get_ticks() - self.game_start_ms) // 1000
        # Respawn time grows by 1s per minute of game time, capped at 15s
        respawn_s = min(5 + (elapsed_s // 60) * 1, 15)
        self.respawn_timer_ms = float(respawn_s * 1000)
        self.is_respawning = True

    def _do_respawn(self) -> None:
        self.is_respawning = False
        if self.player is None:
            return
        self.player.hp = self.player.max_hp
        self.player.alive = True
        spawn_x = getattr(self.player, 'spawn_x', 120.0)
        spawn_y = getattr(self.player, 'spawn_y', 1430.0)
        self.player.x = spawn_x
        self.player.y = spawn_y
        self.player.rect.x = int(spawn_x)
        self.player.rect.y = int(spawn_y)
        self.pending_respawn = True  # Signals server to reset HP next packet

    def _wait_for_players(self) -> bool:
        BG          = (8,   8,  20)
        CYAN        = (80, 220, 255)
        PURPLE      = (180,  80, 255)
        TEXT        = (220, 220, 255)
        SLOT_COLOR  = (40,  40,  80)
        SLOT_ACTIVE = (30,  60, 100)
        DIM         = (80,  80, 100)

        font_path = resource_path("game/assets/font/Orbitron-Bold.ttf")
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
        dummy_inputs = {"z": False, "q": False, "s": False, "d": False}
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

        self.game_start_ms = pygame.time.get_ticks()

        self._disconnected = False

        while self.running:
            # dt_ms : millisecondes brutes pour spawn_timer ; dt : secondes pour wave_timer
            self.dt_ms = self.clock.tick(60)
            self.dt = self.dt_ms / 1000.0
            self.handle_event()
            self.update()
            self.draw()

            if getattr(self, '_disconnected', False):
                return "DISCONNECT"

            if not self.nexus_v.alive or not self.nexus_r.alive:
                # Blue player attacks nexus_v (red), red player attacks nexus_r (blue)
                player_team = self.player.team if self.player else ""
                if not self.nexus_v.alive:
                    winner = "VICTORY" if player_team == "blue" else "DEFEAT"
                else:
                    winner = "VICTORY" if player_team == "red" else "DEFEAT"
                end = EndScreen(self.screen, winner, kills=self.kills, deaths=self.deaths)
                end.draw()
                result = end.run()
                return result
        return "QUIT"