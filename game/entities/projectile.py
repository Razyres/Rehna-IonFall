import pygame
from typing import List, Optional
from .entity import Entity

class Projectile(Entity):
    """
    Represents a dynamic offensive projectile fired by champions or entities.
    
    Manages linear directional travel, lifetime range restrictions, and obstacle
    collision intersection checkmarks. Decouples server positioning computation
    from client rendering layers.
    """
    
    def __init__(self, x: float, y: float, dx: float, dy: float, speed: float, damage: int, projectile_range: int, sprite_path: Optional[str]):
        """
        Initializes a new Projectile instance.

        Args:
            x (float): The starting world X coordinate.
            y (float): The starting world Y coordinate.
            dx (float): Normalized horizontal movement direction component.
            dy (float): Normalized vertical movement direction component.
            speed (float): Positional translation scaling speed factor per update tick.
            damage (int): Offensive raw threat points applied to victims upon impact.
            projectile_range (int): Total lifetime duration quantified in tick frames.
            sprite_path (Optional[str]): System path to load the visual bullet asset texture (Client-side usage).
        """
        # Fallback structural dimensions for server simulation
        width, height = 8, 8
        image_surface: Optional[pygame.Surface] = None
        # Client-side configuration: Safe asset convertion and loading parameters
        if sprite_path:
            try:
                raw_image = pygame.image.load(sprite_path).convert_alpha()
                # Apply structural double-scale up to maintain baseline vizualization consistency
                image_surface = pygame.transform.scale(raw_image, (2 * raw_image.get_width(), 2 * raw_image.get_height()))
                width, height = image_surface.get_width(), image_surface.get_height()
            except pygame.error:
                # Fallback safeguard in case asset mapping path discrepancies occur
                pass
        # Call Entity parent constructor (Projectiles hold 0 HP by system default design)
        super().__init__(x, y, width, height, image_surface, hp=0)
        # Physics Trajectory and Structural Stats (Server Authoritative)
        self.dx: float = dx
        self.dy: float = dy
        self.speed: float = speed
        self.damage: int = damage
        self.range: int = projectile_range
        # Optional curse payload (set by make_curse ability)
        self.is_curse: bool = False
        self.curse_duration_ms: int = 0
        # Team of the player who fired this projectile
        self.team: str = ""
    
    def update_server_state(self, collision_rects: List[pygame.Rect], entities: Optional[List[Entity]] = None) -> None:
        """
        Updates the projectile's trajectory coordinates and ticks down its lifetime bounds.
        
        Performs vector translation logic and obstacle bounding box intersection queries.
        This process runs exclusively on the Server instance.

        Args:
            collision_rects (List[pygame.Rect]): Collection of impassable environmental structures.
            entities (Optional[List[Entity]], optional): Active objects array for targeted hit validations.  Defaults to None.
        """
        # Instantly invalidate instance if lifetime expiration parameters match
        if self.range <= 0:
            self.alive = False
            return
        # Process spatial linear translations
        self.range -= 1
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        # Synchronize physics collision validation structures
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        # Evaluate structural obstacle collisions (Walls/Terrain intersection points)
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                self.alive = False
                break
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Renders the projectile asset texture configuration onto the screen workspace.

        Args:
            screen (pygame.Surface): Layout display surface to apply blit pixels onto.
            camera (_type_): Viewport tracking mechanism handling translation offsets.
        """
        # Leverage base Entity rendering system which perfectly manages camera transformations.
        # (Since health points are 0, it won't draw any unnecessary health bars)
        super().draw(screen, camera)