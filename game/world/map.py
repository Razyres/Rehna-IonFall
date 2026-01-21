import pygame
import pytmx

class GameMap :
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight
    
    def draw(self, screen, camera):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        world_x = x * self.tmx_data.tilewidth
                        world_y = y * self.tmx_data.tileheight
                        screen_x, screen_y = camera.apply_position(world_x, world_y)
                        tile_width = self.tmx_data.tilewidth * camera.zoom
                        tile_height = self.tmx_data.tileheight * camera.zoom
                        if (tile_width < screen_x < camera.width) and (tile_height < screen_y < camera.height):
                            scaled_tile = pygame.transform.scale(tile, (int(tile_width), int(tile_height)))
                            screen.blit(scaled_tile, (screen_x, screen_y))