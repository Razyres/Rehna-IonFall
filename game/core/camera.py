import pygame

class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
        self.zoom = 2.0
        self.target_zoom = 2.0
        self.zoom_speed = 0.1
        self.smoothing = 0.15
    
    def follow(self, target_rect):
        target_center_x = target_rect.x + target_rect.width//2
        target_center_y = target_rect.y + target_rect.height//2
        visible_width = self.screen_width / self.zoom
        visible_height = self.screen_height / self.zoom
        target_x = target_center_x - visible_width / 2
        target_y = target_center_y - visible_height / 2
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing
    
    def set_zoom(self, zoom_level):
        self.target_zoom = max(2.0, min(zoom_level, 5.0))
    
    def update_zoom(self):
        if abs(self.zoom - self.target_zoom) > 0.01:
            self.zoom += (self.target_zoom - self.zoom) * self.zoom_speed
        else:
            self.zoom = self.target_zoom
    
    def apply(self, entity):
        screen_x = (entity.x - self.x) * self.zoom
        screen_y = (entity.y - self.y) * self.zoom 
        return screen_x, screen_y
    
    def apply_rect(self, rect):
        screen_x = (rect.x - self.x) * self.zoom
        screen_y = (rect.y - self.y) * self.zoom
        screen_width = rect.width * self.zoom
        screen_height = rect.height * self.zoom
        return pygame.Rect(screen_x, screen_y, screen_width, screen_height)
    
    def apply_pos(self, x, y):
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom
        return screen_x, screen_y