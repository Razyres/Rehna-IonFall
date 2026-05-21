import pygame
from typing import List, Optional
from .entity import Entity

class Nexus(Entity):
    """
    Represents a teams's core base structure (Nexus) within the MOBA environment.
    
    Acts as the primary objective of the game. Handles team-specific structural
    damage protection rules on the server and scales its visual layout on the client.
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, image: Optional[pygame.Surface], team: str, hp: int = 1000):
        """
        Initializes a new Nexus instance.

        Args:
            x (float): The structural world X coordinate.
            y (float): The structural world Y coordinate.
            width (int): The width of the structure's physical footprint.
            height (int): The height of the structure's physical footprint.
            image (Optional[pygame.Surface]): The preloaded asset texture (Client-side usage).
            team (str): Faction alliance ownership code ('blue' or 'red').
            hp (int, optional): The structural maximum health pool. Defaults to 1000.
        """
        # Call Entity parent constructor to establish standard properties
        super().__init__(x, y, width, height, image, hp)
        # Faction Configuration (Server and Client usage)
        self.team: str = team
    
    def take_damage_from_team(self, damage: int, attacker_team: str) -> None:
        """
        Applies structural damage to the health pool if the attacker belongs to an opposing faction.
        
        This method is authoritative and must execute exclusively on the Server loop.

        Args:
            damage (int): The quantity of structural damage to deal.
            attacker_team (str): Faction alignement string of the attacking unit.
        """
        if not self.alive:
            return
        #Friendly fire validation barrier
        if self.team == attacker_team:
            return
        #Deduct health metrics via parent class mechanics
        super().take_damage(damage)
        print(f"Nexus [{self.team.upper()}] HP : {self.hp}")
    
    def update_server_state(self, collision_rects: List[pygame.Rect], entities: Optional[List[Entity]] = None) -> None:
        """
        Maintains the physical integrity state of the static objective structure.
        
        This structural process runs exclusively within the server environment.

        Args:
            collision_rects (List[pygame.Rect]): Global environment obstacle layout.
            entities (Optional[List[Entity]], optional): Active game objects registry. Defaults to None.
        """
        super().update_server_state(collision_rects, entities)
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Renders the sturctural asset configuration and overlays its health metrics.

        Args:
            screen (pygame.Surface): Surface viewport to blit pixels onto.
            camera (_type_): Layout tracking mechanism handling translation offsets.
        """
        # We leverage Entity.draw() to process zoom modifications
        # and automatically append the floating sructural health overlay!
        super().draw(screen, camera)