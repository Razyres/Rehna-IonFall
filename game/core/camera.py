import pygame

class Camera():
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0
        self.y = 0
        self.zoom = 1.5
        self.target_zoom = 1.5
        self.zoom_speed = 0.1
        self.smoothing = 0.1
        
    def follow(self, target_rect):
        target_x = target_rect.centerx - (self.width / 2) / self.zoom
        target_y = target_rect.centery - (self.height / 2) / self.zoom
        self.x = (target_x - self.x) / self.smoothing
        self.y = (target_y - self.y) / self.smoothing
        self.x = max(0, min(self.x, self.map_width - self.width / self.zoom))
        self.y = max(0, min(self.y, self.map_height - self.height / self.zoom))
    
    def apply(self, rect):
        return pygame.Rect(
            (rect.x - self.x) * self.zoom,
            (rect.y - self.y) * self.zoom,
            self.width * self.zoom,
            self.height * self.zoom
        )
    
    def apply_position(self, x, y):
        return (
            (x - self.x) * self.zoom,
            (y - self.y) * self.zoom
        )
    
    def update_zoom(self):
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed
    
    def set_zoom(self, zoom_level):
        self.target_zoom = max(2.0, min(zoom_level, 3,0))