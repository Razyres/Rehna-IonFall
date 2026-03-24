import pygame
import pytmx
import sys
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from game.entities.champion import Champion
from game.entities.enemy import Enemy
from game.world.map import GameMap
from game.core.camera import Camera
from game.entities.sprites import Sprite
from game.entities.projectile import Projectile
import os
current_dir = os.path.dirname(__file__)
game_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(game_dir)
map_path = os.path.join(project_root, "MAP", "MAP_1v1.tmx")

class Game :
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.entities = []
        self.player = None
        self.game_map = GameMap(map_path)
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        self.camera = Camera(screen_width, screen_height, self.game_map.map_width, self.game_map.map_height)
        self.collisions_rects = self.game_map.get_collision_rects()

    
    def get_input(self):
        dx, dy = 0, 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_q]:
            dx -= 1
        if keys[pygame.K_s]:
            dy += 1
        if keys[pygame.K_z]:
            dy -= 1
        return dx, dy
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_a:
                    projectile = self.player.attack(self.camera)
                    if projectile:
                        self.add_entity(projectile)
            
    def update(self):
        for entity in self.entities:
            entity.update(None, self.collisions_rects)
        for entity in self.entities:
            if isinstance(entity, Enemy):
                if entity.get_rect().colliderect(self.player.get_rect()):
                    self.player.take_damage(entity.damage)
        for entity in self.entities:
            if isinstance(entity, Projectile):
                for other in self.entities:
                    if isinstance(other, Enemy):
                        if entity.rect.colliderect(other.get_rect()):
                            other.take_damage(entity.damage)
                            entity.alive = False
        self.entities = [e for e in self.entities if not hasattr(e, "alive") or e.alive]
        if self.player.alive == False:
            self.running = False
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
        self.camera.follow(player_rect)
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, self.camera)
        for entity in self.entities:
            entity.draw(self.screen, self.camera)
        pygame.display.flip()
    
    def add_entity(self, entity):
        self.entities.append(entity)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

