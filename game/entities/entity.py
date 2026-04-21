import pygame

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, sprite, hp):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = sprite
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.hp = hp
        self.max_hp = hp
        self.alive = True
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    #Nico modif arguments update ajout entities=None
    def update(self, event, collision_rects,entities=None):
        if self.alive == False:
            self.sprite = None
    
    def draw_health_bar(self, screen, camera):
        self.rect.x, self.rect.y = self.x, self.y
        if self.hp > 0:
            screen_x, screen_y = camera.apply(self)
            bar_width = int(self.width * camera.zoom)
            bar_height = max(2, int(5 * camera.zoom))#
            bar_x = screen_x
            bar_y = screen_y - 15
            hp_ratio = self.hp/self.max_hp
            current_hp_width = int(bar_width * hp_ratio)
            pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, current_hp_width, bar_height))
            pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def draw(self, screen, camera):
        if self.image:
            screen_x, screen_y = camera.apply(self)
            scaled_width = int(self.image.get_width() * camera.zoom)
            scaled_height = int(self.image.get_height() * camera.zoom)
            scaled_sprite = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            screen.blit(scaled_sprite, (screen_x, screen_y))
            self.draw_health_bar(screen, camera)
