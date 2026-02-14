import pygame
import pytmx

class GameMap :
    def __init__(self, tmx_file):
        self.tmx_data = pytmx.load_pygame(tmx_file)
        self.map_width = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height = self.tmx_data.height * self.tmx_data.tileheight
    
    def draw(self, screen, camera):
        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    if gid == 0:
                        continue
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        world_x = x * tile_width
                        world_y = y * tile_height
                        screen_x, screen_y = camera.apply_pos(world_x, world_y)
                        scaled_width = int(tile_width * camera.zoom)
                        scaled_height = int(tile_height * camera.zoom)
                        if (screen_x + scaled_width < 0 or screen_x > camera.screen_width or screen_y + scaled_height < 0 or screen_y > camera.screen_height):
                            continue
                        scaled_tile = pygame.transform.scale(tile, (scaled_width, scaled_height))
                        screen.blit(scaled_tile, (screen_x, screen_y))
