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
        return pygame.Rect(self.x, self.y, self.width/2, self.height/2)
    
    def update(self, event, collision_rects):
        if self.alive == False:
            self.sprite = None
    
    def draw(self, screen, camera):
        if self.sprite:
            screen_x, screen_y = camera.apply(self)
            scaled_width = int(self.sprite.get_width() * camera.zoom)
            scaled_height = int(self.sprite.get_height() * camera.zoom)
            scaled_sprite = pygame.transform.scale(self.sprite, (scaled_width, scaled_height))
            screen.blit(scaled_sprite, (screen_x, screen_y))
