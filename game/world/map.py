import pygame
import pytmx

class GameMap :
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight
    
    def draw(self, screen, camera_offset = (0, 0)):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        pos_x = x * self.tmx_data.tilewidth - camera_offset[0]
                        pos_y = y * self.tmx_data.tileheight - camera_offset[1]
                        screen.blit(tile, (pos_x, pos_y))