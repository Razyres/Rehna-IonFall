import pygame
from pathlib import Path

class Sprite:
    DIRECTIONS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    
    def __init__(self, sprite_folder, sprite_prefix, width=None, height=None):
        import re
        import glob
        self.sprites = {}
        self.direction = "S"
        for direction in self.DIRECTIONS:
            pattern = str(Path(sprite_folder) / f"{sprite_prefix}_{direction}_*.png")
            matches = glob.glob(pattern)
            if not matches:
                pattern = str(Path(sprite_folder) / f"{sprite_prefix}_{direction}.png")
                matches = glob.glob(pattern)
            if not matches:
                raise FileNotFoundError(f"Sprite introuvable : {pattern}")
            path = Path(matches[0])
            img = pygame.image.load(str(path)).convert_alpha()
            if width is None or height is None:
                match = re.search(r'(\d+)x(\d+)', path.name)
                if match:
                    w = int(match.group(1))
                    h = int(match.group(2))
                else:
                    w, h = img.get_size()
            else:
                w, h = width, height
            self.sprites[direction] = pygame.transform.scale(img, (w, h))
        self.width = self.sprites["S"].get_width()
        self.height = self.sprites["S"].get_height()
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        
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
