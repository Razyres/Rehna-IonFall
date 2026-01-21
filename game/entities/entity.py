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
    
    def draw(self, screen, camera):
        if self.sprite:
            rect = self.get_rect()
            screen_rect = camera.apply(rect)
            scaled_image = pygame.transform.scale(self.sprite (int(screen_rect.width), int(screen_rect.height)))
            screen.blit(scaled_image, screen_rect)
    
