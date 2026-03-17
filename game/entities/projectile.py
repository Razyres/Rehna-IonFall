import pygame
import math
from .entity import Entity

class Projectile(Entity):
    def __init__(self, x, y, dx, dy, speed, damage, sprite_path):
        super().__init__(x, y, 10, 10, None)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.sprite = pygame.image.load(sprite_path)
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        
    def update(self, event, collision_rect):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.rect = self.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        for rect in collision_rect:
            if self.rect.colliderect(rect):
                self.alive = False
                break
    
    def draw(self, screen, camera):
        screen_x, screen_y = camera.apply(self)
        scaled_w = self.width * camera.zoom
        scaled_h = self.height * camera.zoom
        scaled = pygame.transform.scale(self.sprite, (scaled_w, scaled_h))
        screen.blit(scaled, (int(screen_x), int(screen_y)))