from .entity import Entity
import pygame
class Enemy(Entity):
    def __init__(self, x, y, width, height, sprite, damage):
        super().__init__(x, y, width, height, sprite)
        self.damage = damage
        
    def update(self, event, collision_rects):
        pass
    
    def draw(self, screen, camera):
        if self.sprite:
            rect = self.get_rect()
            screen_rect = camera.apply(rect)
            screen.blit(self.sprite, screen_rect)