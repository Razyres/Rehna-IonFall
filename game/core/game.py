import pygame
import os
from pathlib import Path
from typing import List, Dict, Optional, Any

from game.world.map import GameMap
from game.core.camera import Camera
from game.entities.nexus import Nexus
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
    
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """
        Initializes a new Game management sequence.

        Args:
            screen (pygame.Surface): Main window display workspace.
            clock (pygame.time.Clock): Game runtime tracking engine for framerate capping.
        """
        self.screen: pygame.Surface = screen
        self.clock: pygame.time.Clock = clock
        self.running: bool = True
        # Network Engine Synchronizer Initialization
        self.net: Network = Network()
        self.my_id: Any = self.net.player_id
        # Entity Pipeline Containers
        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group()
        self.projectiles: pygame.sprite.Group = pygame.sprite.Group()
        self.enemies: pygame.sprite.Group = pygame.sprite.Group()
        self.nexuses: pygame.sprite.Group = pygame.sprite.Group()
        # Map Layout and Collision Processing
        project_root = Path(__file__).parent.parent.parent
        map_path = os.path.join(project_root, "MAP", "MAP_1v1.tmx")
        self.game_map: GameMap = GameMap(map_path)
        # Viewport Camera Bounds configuration
        self.camera: Camera = Camera(
            screen.get_width(), screen.get_height(),
            self.game_map.map_width, self.game_map.map_height
        )
        self.collisions_rects: List[pygame.Rect] = self.game_map.get_collision_rects()
        # Authoritative Structural Bases Initialization (Nexus Objectives)
        self.nexus_r: Nexus = Nexus(253, 1240, 100, 100, "sprite/nexus_r.png", "blue", hp=1000)
        self.nexus_v: Nexus = Nexus(1232, 220, 128, 128, "sprite/nexus_v.png", "red", hp=1000)
        self.add_entity(self.nexus_r, [self.nexuses])
        self.add_entity(self.nexus_v, [self.nexuses])
        # Player Configuration Context (Instantiated as Champion)
        self.player: Optional[Champion] = None
        self.dt: float = 0.0
        # Minion Waves Procedural Spawner Configuration
        self.spawn_timer: float = 0.0
        self.wave_timer: float = 0.0
        self.minions_spawnd_in_wave: int = 0
        self.wave_size: int = 4
        self.is_wave_active: bool = True
        # Graphic Assets Preloading
        self.blue_minion_img: pygame.Surface = pygame.image.load("sprite/test_sbire_blue.png").convert_alpha()
        self.red_minion_img: pygame.Surface = pygame.image.load("sprite/test_sbire_red.png").convert_alpha()
    
    def add_entity(self, entity: pygame.sprite.Sprite, groups: List[pygame.sprite.Group] = []) -> None:
        """
        Safely registers a game entity into the central rendering and processing groups.

        Args:
            entity (pygame.sprite.Sprite): The element instance to inject.
            groups (List[pygame.sprite.Group], optional): Auxiliary filters (e.g. projectiles, enemies). Defaults to [].
        """
        if isinstance(entity, pygame.sprite.Sprite):
            self.all_sprites.add(entity)
            for group in groups:
                group.add(entity)
        else:
            print(f"Warning: {type(entity)} is not a supported Pygame Sprite component subclass!")
    
    def handle_event(self) -> None:
        """
        Captures hardware devices events and translates them into network or application triggers.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            # Action intent trigger: Combat engagement request
            if event.key == pygame.K_a and self.player and self.player.alive:
                # Fetch crosshair coordinates from camera viewport translation
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_mouse_x = mouse_x / self.camera.zoom + self.camera.x
                world_mouse_y = mouse_y / self.camera.zoom + self.camera.y
                # Request server firing permissions
                new_proj = self.player.process_attack_intent(world_mouse_x, world_mouse_y)
                if new_proj:
                    self.add_entity(new_proj, [self.projectiles])
    
    def _update_minion_spawning(self) -> None:
        """
        Calculates delta steps to execute procedural server-side lane minion wave deployments.
        """
        self.spawn_timer += self.dt * 1000
        if self.is_wave_active and self.minions_spawned_in_wave < self.wave.size:
            if self.spawn_timer > 800:
                blue_minion = Minion(253, 1240, 32, 32, self.blue_minion_img, "blue")
                self.add_entity(blue_minion, [self.enemies])
                red_minion = Minion(1232, 220, 32, 32, self.red_minion_img, "red")
                self.add_entity(red_minion, [self.enemies])
                self.minions_spawnd_in_wave += 1
                self.spawn_timer = 0
        elif self.minions_spawnd_in_wave >= self.wave_size:
            self.is_wave_active = False
            self.wave_timer += self.dt
            if self.wave_timer > 30.0:
                self.wave_timer = 0.0
                self.minions_spawnd_in_wave = 0
                self.is_wave_active = True
    
    def update(self) -> None:
        """
        Executes the authoritative step look tick processing for mechanics, AI tracking, and coordinates.
        """
        # Track framerate delta step metrics
        self.dt = self.clock.tick(60) / 1000.0
        # Process minion deployment tracking
        self._update_minion_spawning()
        # Build global obstacle bounding arrays (Walls + Nexus structural frames)
        obstacles = self.collisions_rects + [n.get_rect() for n in self.nexuses]
        # Handle network input mappings for player character
        if self.player and self.player.alive:
            keys = pygame.key.get_pressed()
            input_map = {
                "z": keys[pygame.K_z],
                "q": keys[pygame.K_q],
                "s": keys[pygame.K_s],
                "d": keys[pygame.K_d]
            }
            # Execute authoritative server physics calculation
            dx, dy = self.player.update_server_physics(input_map, obstacles)
            # Synchronize client rendering frames direction
            self.player.update_client_animation(dx, dy)
        # Update remaining world entities loops (Minions AI, projctiles trajectories)
        all_entities_list: List[Entity] = list(self.all_sprites) # type: ignore
        for entity in all_entities_list:
            if entity != self.player:
                entity.update_server_state(obstacles, all_entities_list)
        # Process Projectiles hit calculation checks
        for proj in list(self.projectiles): #type: ignore
            if not proj.alive:
                continue
            hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False)
            for enemy in hit_enemies:
                if enemy.alive:
                    enemy.take_damage(proj.damage)
                    proj.alive = False
            if proj.alive and proj.rect.colliderect(self.nexus_v.rect):
                self.nexus_v.take_damage_from_team(proj.damage, "blue")
                proj.alive = False
            if proj.alive and proj.rect.colliderect(self.nexus_r.rect):
                self.nexus_r.take_damage_from_team(proj.damage, "red")
                proj.alive = False
        # Environmental threats: Aggro bounds intersection contact checks
        if self.player and self.player.alive:
            if pygame.sprite.spritecollide(self.player, self.enemies, False):
                self.player.take_damage(10)
        # Memory Garbage Collection cleanup layer: Burry dead entities
        for entity in all_entities_list:
            if hasattr(entity, 'alive') and not entity.alive:
                entity.kill()
        # Move viewport lens focusing on current player layout metrics
        if self.player:
            self.camera.follow(self.player.get_rect())
        # Global game status terminal constraints verification
        if not self.nexus_v.alive or not self.nexus_r.alive or (self.player and not self.player.alive):
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
    
    def run(self) -> str:
        """
        Maintains the operational application loop sequence runtime.

        Returns:
            str: Game outcome state flag identifier ('VICTORY', 'DEFEAT', or 'QUIT').
        """
        while self.running:
            self.handle_event()
            self.update()
            self.draw()
            if not self.nexus_v.alive or not self.nexus_r.alive:
                winner = "VICTORY" if not self.nexus_v.alive else "DEFEAT"
                end = EndScreen(self.screen, winner)
                end.draw()
                result = end.run
                return result
            self.clock.tick()
        return "QUIT"