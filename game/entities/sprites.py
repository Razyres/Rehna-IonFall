import pygame
from pathlib import Path

class Sprite:
    DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    
    def __init__(self, sprite_folder, sprite_prefix, width, height):
        self.sprites = {}
        self.direction = "S"
        for direction in self.DIRECTIONS:
            path = Path(sprite_folder)/ f"{sprite_prefix}_{direction}.png"
            img = pygame.image.load(path).convert_alpha()
            self.sprites[direction] = pygame.transform.scale(img, (width, height))
        self.rect = self.sprites["S"].get_rect()
        self.height = height
        self.width = width
        
    @property
    def current_sprite(self):
        return self.sprites[self.direction]
    
    def set_direction(self, dx, dy):
        if dx == 0 and dy == 0:
            return
        dir_map = {
            (0, -1): "N", (-1, -1): "NW", (-1, 0): "W", (-1, 1): "SW", (0, 1): "S", (1, 1): "SE", (1, 0): "E", (1, -1): "NE"
        }
        nx = (dx > 0) - (dx < 0)
        ny = (dy > 0) - (dy < 0)
        self.direction = dir_map.get((nx, ny), self.direction)
        
    def draw(self, surface):
        surface.blit(self.sprites[self.direction], self.rect)
