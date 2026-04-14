import pygame
import math
from .entity import Entity

class Projectile(Entity):
    def __init__(self, x, y, dx, dy, speed, damage, projectile_range, sprite_path):
        image = pygame.image.load(sprite_path).convert_alpha()
        image = pygame.transform.scale(image, (2 * image.get_width(), 2 * image.get_height()))
        super().__init__(x, y, image.get_width(), image.get_height(), image, hp=0)
        self.dx = dx
        self.dy = dy
        self.speed = speed
        self.damage = damage
        self.range = projectile_range 
    #Nico modif arguments update ajout entities=None
    def update(self, dt, collision_rects,entities=None):
        if self.range <= 0:
            self.alive = False
            return
        self.range -= 1
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.rect.x = self.x
        self.rect.y = self.y
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                self.alive = False
                break
    
    def draw(self, screen, camera):
        super().draw(screen, camera)