import pygame
import re
import glob
import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from game.utils import resource_path

class Sprite:
    """
    An asset animation and orientation sheet manager for client-side viewport objects.
    
    Loads multi-directional bitmap frames from local storage profiles and map spatial
    displacement velocity vectors to structural static orientation frames (8-way pathing grid)
    """
    # Immutable 8-way navigation compass tracking keys
    DIRECTIONS: List[str] = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    
    def __init__(self, sprite_folder: str, sprite_prefix: str, width: Optional[int] = None, height: Optional[int] = None):
        """
        Initializes a new Sprite directory orientation matrix.

        Args:
            sprite_folder (str): System path pointing to the graphical source assets folder.
            sprite_prefix (str): Textual identifiertoken filtering target directiona items.
            width (Optional[int], optional): Force scale horizontal rendering dimention context. Defaults to None.
            height (Optional[int], optional): Force scale vertical rendering dimension context. Defaults to None.
        
        Raises:
            FileNotFoundError: Discovered if asset mapping patterns fail to resolve any valid asset path.
        """
        self.sprites: Dict[str, pygame.Surface] = {}
        self.direction: str = "S"
        w, h = 32, 32 # Stable structural fallbacks to prevent variable bounds leaks
        if not os.path.isabs(sprite_folder):
            sprite_folder = resource_path(sprite_folder)
        for direction in self.DIRECTIONS:
            # Pattern matching lookup variant A: Frame counting parameters (* notation)
            pattern = str(Path(sprite_folder) / f"{sprite_prefix}_{direction}_*.png")
            matches = glob.glob(pattern)
            # Pattern matching lookup variant B: Single discrete directional assets
            if not matches:
                pattern = str(Path(sprite_folder) / f"{sprite_prefix}_{direction}.png")
                matches = glob.glob(pattern)
            if not matches:
                raise FileNotFoundError(f"Sprite asset not found resolving path pattern: {pattern}")
            path = Path(matches[0])
            img = pygame.image.load(str(path)).convert_alpha()
            # Automatic asset resolution via file naming syntax parsing (e.g. hero_S_32x32.png)
            if width is None or height is None:
                match = re.search(r'(\d+)x(\d+)', path.name)
                if match:
                    w = int(match.group(1))
                    h = int(match.group(2))
                else:
                    w, h = img.get_size()
            else:
                w, h = width, height
            # Assign stuctural texture scaling data into memorry maps
            self.sprites[direction] = pygame.transform.scale(img, (w, h))
        # Core dimension footprint variables (Required by client physics mirrors)
        self.width: int = w
        self.height: int = h
        self.rect: pygame.Rect = pygame.Rect(0, 0, self.width, self.height)
    
    @property
    def current_sprite(self) -> pygame.Surface:
        """
        Fetches the active orientation surface mapped to the current movement heading.

        Returns:
            pygame.Surface: The active directional render surface template.
        """
        return self.sprites[self.direction]
    def set_direction(self, dx: float, dy: float) -> None:
        """
        Translates real-number spatial displacement vectors into discrete directional compass state.

        Args:
            dx (float): Horizontal speed/displacement translation scalar.
            dy (float): Vertical speed/displacement translation scalar.
        """
        # Maintain stance orientation if velocity inputs are zeroed out
        if dx == 0 and dy == 0:
            return
        # 2D Grid mapping registry matching normalizzed matrix targets to compass strings
        dir_map: Dict[Tuple[int, int], str] = {
            (0, -1): "N", (-1, -1): "NW", (-1, 0): "W", (-1, 1): "SW",
            (0, 1): "S", (1, 1): "SE", (1, 0): "E", (1, -1): "NE"
        }
        # Safe normalization to discrete sign indicators (-1, 0, 1)
        nx = int((dx > 0) - (dx < 0))
        ny = int((dy > 0) - (dy < 0))
        # Update orientation status fallback on past tracking context if mismatch triggers
        self.direction = dir_map.get((nx, ny), self.direction)
        # Synchronize model bounds properties to prevent sprite compression artifacts
        self.width = self.sprites[self.direction].get_width()
        self.height = self.sprites[self.direction].get_height()
    
    def draw(self, surface: pygame.Surface) -> None:
        """
        Executes a basic fixed viewport rendering blit.
        
        Note: Mostly bypassed in favor of advanced automated camera system processing.

        Args:
            surface (pygame.Surface): Display target to apply blit operations onto.
        """
        surface.blit(self.sprites[self.direction], self.rect)