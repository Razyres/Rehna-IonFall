import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, sprite):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = sprite
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.alive = True
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    #Nico modif arguments update ajout entities=None
    def update(self, event, collision_rects,entities=None):
        if self.alive == False:
            self.sprite = None
    
    def draw(self, screen, camera):
        if self.image:
            screen_x, screen_y = camera.apply(self)
            scaled_width = int(self.image.get_width() * camera.zoom)
            scaled_height = int(self.image.get_height() * camera.zoom)
            scaled_sprite = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            screen.blit(scaled_sprite, (screen_x, screen_y))
