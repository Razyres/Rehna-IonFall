from .entity import Entity
import pygame
class Enemy(Entity):
    def __init__(self, x, y, width, height, sprite, damage):
        super().__init__(x, y, width, height, sprite)
        self.damage = damage
        
    def update(self, event):
        pass
    
    def draw(self, screen, camera):
        if self.sprite:
            rect = self.get_rect()
            screen_rect = camera.apply(rect)
            scaled_image = pygame.transform.scale(self.sprite, (int(screen_rect.width), int(screen_rect.height)))
            screen.blit(scaled_image, screen_rect)