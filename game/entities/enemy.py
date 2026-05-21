import pygame
from typing import List, Optional
from .entity import Entity

class Enemy(Entity):
    """
    A base class representing an AI-controlled or hostile NPC within the MOBA environment.
    
    Acts as an intermediary layer between generic entities and specific behaviors
    like lane minions or jungle monsters. It decouples server-side logic from
    client-side rendering.
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, image: Optional[pygame.Surface], damage: int, hp: int):
        """
        Initializes a new Enemy instances.

        Args:
            x (float): The initial X coordinate in the game world.
            y (float): The initial Y coordinate in the game world.
            width (int): The width of the enemy's hitbox.
            height (int): The height of the enemy's hitbox.
            image (Optional[pygame.Surface]): The visual texture or sprite surface (Client-side usage).
            damage (int): The offensive attack power or impact damage.
            hp (int): The initial and maximum health points.
        """
        # Call the parent Entity constructor to initialize core attributes (position, health, etc...)
        super().__init__(x, y, width, height, image, hp)
        self.damage: int = damage
    
    def update_server_state(self, collision_rects: List[pygame.Rect], entities: Optional[List[Entity]] = None) -> None:
        """
        Udates the server-side behavioral routine for the enemy.
        
        This method is purely logical and mathematical. It must be executed
        exclusively on the Server loop. Overridden by specific child classes (e.g., Minions).

        Args:
            collision_rects (List[pygame.Rect]): List map obstacles and terrain boundaries.
            entities (Optional[List[Entity]], optional): List of all active world entities for AI targeting. Defaults to None.
        """
        super().update_server_state(collision_rects, entities)
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """Renders the enemy asset texture and its overlay indicators onto the client viewport.

        Args:
            screen (pygame.Surface): The client display window surface.
            camera (_type_): The viewport system managing screen scaling and positional adjustments.
        """
        # We leverage the clean rendering logic from Entity.draw() which natively handles :
        # 1. Camera translation and zoom transformations.
        # 2. Rendering of the floating health overlay.
        super().draw(screen, camera)