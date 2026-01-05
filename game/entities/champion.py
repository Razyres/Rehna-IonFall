import pygame
from .entity import Entity

class Champion(Entity):
    def __init__(self, x, y, speed, height, width, sprite):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = speed
        self.height = height
        self.width = width
        self.sprite = sprite
    
    def update(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_z]:
            self.y -= self.speed
        if pressed[pygame.K_q]:
            self.x -= self.speed
        if pressed[pygame.K_s]:
            self.y += self.speed
        if pressed[pygame.K_d]:
            self.x += self.speed
    
    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))