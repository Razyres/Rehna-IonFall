from .entity import Entity
import pygame

class Nexus(Entity):
    def __init__(self, x, y, width, height, spritepath, hp=1000):
        sprite = pygame.image.load(spritepath).convert_alpha()
        super().__init__(x, y, width, height, sprite)
        self.hp = hp
    
    def take_damage(self, damage):
        self.hp -= damage
        print(f"Nexus HP : {self.hp}")
        if self.hp <= 0:
            self.alive = False
    
    def update(self, event, collisions):
        pass
    
    def draw(self, screen, camera):
        if self.sprite:
            screen_x, screen_y = camera.apply(self)
            scaled_w = int(self.width * camera.zoom)
            scaled_h = int(self.height * camera.zoom)
            scaled = pygame.transform.scale(self.sprite, (scaled_w, scaled_h))
            screen.blit(scaled, (int(screen_x), int(screen_y)))
