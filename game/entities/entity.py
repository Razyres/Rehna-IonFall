import pygame
from typing import List, Optional

class Entity(pygame.sprite.Sprite):
    """
    A base class representing a generic game entity in a MOBA environment.
    
    Handles core physics attributes (position, dimensions, health) for server calculations,
    as well as client-side rendering methods (sprites, health bars).
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, sprite: Optional[pygame.Surface], hp: int):
        """
        Initializes a new Entity instance.

        Args:
            x (float): The initial X coordinate in the game world.
            y (float): The initial Y coordinate in the game world.
            width (int): The width of the entity's hitbox.
            height (int): The height of the entity's hitbox.
            sprite (pygame.Surface): The visual texture of the entity (Client-side usage).
            hp (int): The initial and maximum health points.
        """
        super().__init__()
        # Position and Dimension (Shared between Server and Client)
        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
        # Health State (Server authoritative, Client read-only)
        self.hp: int = hp
        self.max_hp: int = hp
        self.alive: bool = True
        #Rendering Attributes (Client-side only)
        self.image: Optional[pygame.Surface] = sprite
        self.rect: pygame.Rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def get_rect(self) -> pygame.Rect:
        """
        Generates and returns the current physics rectangle bounding box.

        Returns:
            pygame.Rect: The current bounding box rectangle of the entity.
        """
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def take_damage(self, damage: int) -> None:
        """
        Reduces the entity's health points and processes its death state if necessary.
        
        This method must be executed exclusively on the Server.

        Args:
            damage (int): The amount of health points to deduct.
        """
        if not self.alive:
            return
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def update_server_state(self, collision_rects: List[pygame.Rect], entities: Optional[List['Entity']] = None) -> None:
        """
        Updates the server-side physics, behaviors, and logic of the entity.
        
        No graphic modules are drawn here. This method updates coordinates and state variables.

        Args:
            collision_rects (list): List of pygame. Rect objects representing map obstacles.
            entities (list, optional): List of all active game entitiesfor AI decision making. Default to None.
        """
        # Synchronize physics bounding box before processing movement behavior
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if not self.alive:
            self.image = None
    
    def draw_health_bar(self, screen: pygame.Surface, camera) -> None:
        """
        Rendering a floating health bar directly above the entity on the client's viewport.

        Args:
            screen (pygame.Surface): The game window surface where elements are drawn.
            camera (_type_): The camera object controlling the scaling and positional offsets.
        """
        if self.hp <= 0:
            return
        # Translate world coordinates into viewport/screen space coordinates
        screen_x, screen_y = camera.apply(self)
        # Adjust dimentions according to the camera zoom level
        bar_width = int(self.width * camera.zoom)
        bar_height = max(2, int(5 * camera.zoom))
        # Offset the bar position slightly above the entity's head
        bar_x = screen_x
        bar_y = screen_y - 15
        # Compute current health bar filling ratio
        hp_ratio = max(0.0, min(1.0, self.hp / self.max_hp))
        current_hp_width = int(bar_width * hp_ratio)
        # Drawing layers: 1. Red background (missing health)
        pygame.draw.rect(screen, (200, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        # 2. Green foreground (current health)
        pygame.draw.rect(screen, (0, 200, 0), (bar_x, bar_y, current_hp_width, bar_height))
        # 3. Black thin outer border
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Renders the entity's sprite onto the screen surface with scaling offset applied by the camera viewport.
        
        Args:
            screen (pygame.Surface): The game window surface where elements are drawn.
            camera (_type_): The camera object controlling the scaling and positional offsets.
        """
        #Synchronize client rendering rectangle coordinates with core physics coordinates
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.image:
            # Fetch absolute position relative to screen space using camera math
            screen_x, screen_y = camera.apply(self)
            # Apply real-time scaling factor to matching widths and heights
            scaled_width = int(self.width * camera.zoom)
            scaled_height = int(self.height * camera.zoom)
            # Draw the texture transformed to the screen surface
            scaled_sprite = pygame.transform.scale(self.image, (scaled_width, scaled_height))
            screen.blit(scaled_sprite, (screen_x, screen_y))
            #Draw the health overlay on top of the character
            self.draw_health_bar(screen, camera)