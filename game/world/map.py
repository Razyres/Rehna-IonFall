import pygame
import pytmx
from typing import List, Tuple, Dict, Any

class GameMap:
    """
    Manages loading, parsing, parsing structural physics boundaries, and drawing map layouts.
    
    Interfaces with PyTMX data structures to extract collision rectangles, query spawn positions,
    an optimize localized tile render loops using surface scaling caches.
    """
    
    def __init__(self, tmx_file: str):
        """
        Initializes a new GameMap instance by parsing a Tiled TMX asset.

        Args:
            tmx_file (str): Local system file path to the target .tmx map descriptor.
        """
        self.tmx_data: pygame.TiledMap = pytmx.load_pygame(tmx_file)
        self.map_width: int = self.tmx_data.width * self.tmx_data.tilewidth
        self.map_height: int = self.tmx_data.height * self.tmx_data.tileheight
        # Performance Cache Optimization: Stores pre-scaled surfaces to avoid realtime CPU scaling
        self._scaled_tile_cache: Dict[Tuple[int, float], pygame.Surface] = {}
    
    def get_collision_rects(self) -> List[pygame.Rect]:
        """
        Parses the absolute spatial coordinates of all obstacle bounding shapes.
        
        Typically requestes by authoritative server physics engines to block physical movement.

        Returns:
            List[pygame.Rect]: Vector array containing structural static collision walls.
        """
        collision_rects: List[pygame.Rect] = []
        # Loop through object groups to locate the explicit bounding layout definitions
        for layer in self.tmx_data.objectgroups:
            if layer.name == "Collision":
                for obj in layer:
                    collision_rects.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))
        return collision_rects

    def get_spawn_point(self) -> Tuple[float, float]:
        """
        Queries designated geographic positioning vectors from map configuration files.

        Returns:
            Tuple[float, float]: World coordinates (X, Y) pointing to the initial birth zone.
        """
        for layer in self.tmx_data.objectgroups:
            if layer.name == "Spawns":
                for obj in layer:
                    return (float(obj.x), float(obj.y))
        return (0.0, 0.0) # Safe absolute fallback origin
    
    def draw(self, screen: pygame.Surface, camera: Any) -> None:
        """
        Renders visible layer graphics onto the main window viewport.
        
        Applies mathematical frustum culling optimizations to discard drawing commands
        for map sectors drifting outside screen limits.

        Args:
            screen (pygame.Surface): Display target workspace to execute blits upon.
            camera (Any): Active client camera engine tracking zoom scales and focal offsets.
        """
        tile_width: int = self.tmx_data.tilewidth
        tile_height: int = self.tmx_data.tileheight
        # Target dimension properties under active camera zoom parameters
        scaled_width = int(tile_width * camera.zoom)
        scaled_height = int(tile_height * camera.zoom)
        # Iterate over structural orthographic tile maps layers
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, 'data'):
                for x, y, gid in layer:
                    if gid == 0:
                        continue # Skip transparent/empty grid spaces
                    #Translate abstract layout grid indexes to absolute world units
                    world_x = x * tile_width
                    world_y = y * tile_height
                    # Compute relative positioning values according to camera offsets
                    screen_x, screen_y = camera.apply_pos(world_x, world_y)
                    # Frustum Culling: Abort blit operations if tile boundaries lie fully outside screen boundaries
                    if (screen_x + scaled_width < 0 or screen_x > camera.screen_width or
                        screen_y + scaled_height < 0 or screen_y > camera.screen_height):
                        continue
                    # Retrieve tile graphics asset referencing the global dictionnary identifier
                    cache_key = (gid, camera.zoom)
                    if cache_key in self._scaled_tile_cache:
                        scaled_tile = self._scaled_tile_cache[cache_key]
                    else:
                        tile = self.tmx_data.get_title_image_by_gid(gid)
                        if tile:
                            scaled_tile = pygame.transform.scale(tile, (scaled_width, scaled_height))
                            self._scaled_tile_cache[cache_key] = scaled_tile
                        else:
                            continue
                    # Draw scaled texture on screen matrix coordinates
                    screen.blit(scaled_tile, (screen_x, screen_y))







