import pygame
from typing import List, Optional
from .enemy import Enemy
from .entity import Entity

class Minion(Enemy):
    """
    Represents an automated lane minion (creep) within MOBA environment.
    
    Handles lane-pushing AI, basic enemy aggregation, distance-based pathfinding,
    and periodic combat engagements. This class decouples authoritative server physics
    and targeting logic from client-side texture rendering
    """
    
    def __init__(self, x: float, y: float, width: int, height: int, image: Optional[pygame.Surface], team: str):
        """
        Initializes a new Minion instance.

        Args:
            x (float): The initial world X coordinate.
            y (float): The initial world Y coordinate.
            width (int): The width of the minion's collision bounding box.
            height (int): The height of the minion's collision bounding box.
            image (Optional[pygame.Surface]): The static visual sprite (Used exclusively by the client).
            team (str): The alignement faction of the minion ('blue' or 'red').
        """
        # Call Enemy parent constructor with fixed minion base stats: 5 damage, 100 HP
        super().__init__(x, y, width, height, image, damage=5, hp=100)
        # Operational parameters and alignement (Shared/Authoritative)
        self.team: str = team
        self.target: Optional[Entity] = None
        # Combat and movement profiles (Server enforcement stats)
        self.speed: float = 2.0
        self.attack_range: float = 50.0
        self.attack_cooldown: int = 1000
        self.last_attack_time = 0
    
    def update_server_state(self, collision_rects: List[pygame.Rect], entities: Optional[List[Entity]] = None) -> None:
        """
        Processes the minion's behavior loop on the server instance.
        
        Evaluates targeting contexts, modifies coordinates via pathfinding algorithms,
        and updates the mechanical bounding box variables. This logic never invokes
        any graphical modules

        Args:
            collision_rects (List[pygame.Rect]): Global environment obstacle layout.
            entities (Optional[List[Entity]], optional): List of active world objects for tactical targeting. Defaults to None.
        """
        #Synchronize root entity structures (death processing and basic state changes)
        super().update_server_state(collision_rects, entities)
        if not self.alive or entities is None:
            return
        # Core AI sequential routine execution (Server-side exclusive)
        self._decide_action(entities)
        self._move_or_attack()
    
    def _decide_action(self, entities: List[Entity]) -> None:
        """
        Scans nearby space to acquire or update the active operational target.
        
        Validates target survival states and searches for the closest hostile unit
        within an aggressive acquisition range.

        Args:
            entities (List[Entity]): Current collectionof world objects active on the server loop.
        """
        # Clear reference if the previous target died during past tick updates
        if self.target and not self.target.alive:
            self.target = None
        # Scan world listings for elligible enemy alignements inside an aggro range of 150 units
        for entity in entities:
            if hasattr(entity, 'team') and entity.team != self.team and entity.alive:
                #Calculate vector distance magnitude
                distance = pygame.math.Vector2(entity.x - self.x, entity.y - self.y).length()
                if distance <150.0:
                    self.target= entity
                    break
    
    def _move_or_attack(self) -> None:
        """
        Manages directional movement pathing or shifts states into active combat routines.
        """
        if self.target is None:
            # Neutral Lane Pushing: Path diagonally across the map towards opposing bases
            if self.team == "blue":
                self.x += self.speed
                self.y -= self.speed
            else:
                self.x -= self.speed
                self.y += self.speed
        else:
            # Aggressive Engagement: Calculate approach bounds to acquired threat
            distance = pygame.math.Vector2(self.target.x - self.x, self.target.y - self.y).length()
            if distance > self.attack_range:
                # Adjust spatial coordinates incrementally towards target location
                if self.x < self.target.x:
                    self.x += self.speed
                if self.x > self.target.x:
                    self.x -= self.speed
                if self.y < self.target.y:
                    self.y += self.speed
                if self.y > self.target.y:
                    self.y -= self.speed
            else:
                # Target within parameters, trigger operational weapon calculations
                self._execute_attack()
        # Synchronize physics engine positioning coordinates
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _execute_attack(self) -> None: 
        """
        Applies standard attack damage to the acquired target if internal cooldown metrics permit
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if self.target and self.target.alive:
                self.target.take_damage(self.damage)
                self.last_attack_time = current_time
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """Overrides the rendering pipeline to draw the minion asset texture.

        Args:
            screen (pygame.Surface): Screen workspace to blit graphical details onto.
            camera (_type_): Active viewport manager controlling translation offsets.
        """
        # Instead of an empty method, we lean onto Entity's drawing framework
        # which correctly computes camera position shifts and updates the health overlay.
        super().draw(screen, camera)