import pygame

class Entity():
    def __init__(self, x, y, width, height, sprite):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite = sprite
        self.alive = True
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def update(self, event):
        pass
    
    def draw(self, screen):
        if self.sprite:
            screen.blit(self.sprite, (self.x, self.y))
    
