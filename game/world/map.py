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
        start_x = int(max(0, camera.x / tile_width - 1))
        start_y = int(max(0, camera.y / tile_height - 1))
        end_x = int(min(self.tmx_data.width, (camera.x + camera.screen_width / camera.zoom) / tile_width + 2))
        end_y = int(min(self.tmx_data.height, (camera.y + camera.screen_height / camera.zoom) / tile_height + 2))
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x in range(start_x, end_x):
                    for y in range(start_y, end_y):
                        gid = layer[x][y]
                        if gid:
                            tile = self.tmx_data.get_tile_image_by_gid(gid)
                            if tile:
                                world_x = x * tile_width
                                world_y = x * tile_height
                                screen_x, screen_y = camera.apply_pos(world_x, world_y)
                                scaled_width = int(tile_width * camera.zoom)
                                scaled_height = int(tile_height * camera.zoom)
                                scaled_tile = pygame.transform.scale(tile, (scaled_width, scaled_height))
                                screen.blit(scaled_tile, (screen_x, screen_y))