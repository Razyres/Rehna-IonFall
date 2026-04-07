import pygame
import os
from pathlib import Path

from game.world.map import GameMap
from game.core.camera import Camera
from game.entities.nexus import Nexus
from game.entities.projectile import Projectile
from game.entities.enemy import Enemy
from game.ui.end_screen import EndScreen

class Game():
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.all_sprites = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.nexuses = pygame.sprite.Group()
        project_root = Path(__file__).parent.parent.parent
        map_path = os.path.join(project_root, "MAP", "MAP_1v1.tmx")
        self.game_map = GameMap(map_path)
        self.camera = Camera(screen.get_width(), screen.get_height(), self.game_map.map_width, self.game_map.map_height)
        self.collisions_rects = self.game_map.get_collision_rects()
        self.nexus_r = Nexus(253, 1240, 100, 100, "sprite/nexus_r.png", hp=1000)
        self.nexus_v = Nexus(1232, 220, 128, 128, "sprite/nexus_v.png", hp=1000)
        self.add_entity(self.nexus_r, [self.nexuses])
        self.add_entity(self.nexus_v, [self.nexuses])
        self.player = None
        self.dt = 0
    
    def add_entity(self, entity, groups=[]):
        if isinstance(entity, pygame.sprite.Sprite):
            self.all_sprites.add(entity)
            for group in groups:
                group.add(entity)
        else:
            print(f"Attention: {type(entity)} n'est pas un Sprite Pygame !")
    
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
    
    def update(self):
        self.dt = self.clock.tick(60) / 1000.0
        obstacles = self.collisions_rects + [n.get_rect() for n in self.nexuses]
        self.all_sprites.update(self.dt, obstacles)
        for proj in self.projectiles:
            hit_enemies = pygame.sprite.spritecollide(proj, self.enemies, False)
            for enemy in hit_enemies:
                enemy.take_damage(proj.damage)
                proj.alive = False
            if proj.rect.colliderect(self.nexus_v.rect):
                self.nexus_v.take_damage(proj.damage)
                proj.alive = False
        if pygame.sprite.spritecollide(self.player, self.enemies, False):
            self.player.take_damage(10) 
        for entity in list(self.all_sprites):
            if hasattr(entity, 'alive') and not entity.alive:
                entity.kill()
        self.camera.follow(self.player.get_rect())
        if not self.nexus_v.alive or not self.nexus_r.alive or not self.player.alive:
            self.running = False
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera)
        for entity in self.all_sprites:
            entity.draw(self.screen, self.camera)
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            if not self.nexus_v.alive or not self.nexus_r.alive:
                winner = "VICTORY" if not self.nexus_v.alive else "DEFEAT"
                end = EndScreen(self.screen, winner)
                end.draw()
                result = end.run()
                return result
            self.clock.tick()
        return "QUIT"