import pygame
from typing import List, Optional
from .enemy import Enemy
from .entity import Entity

AGGRO_RANGE = 200.0
LEASH_RANGE = 400.0

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
        # Leash anchor — the position from which max chase distance is measured
        self.spawn_x: float = x
        self.spawn_y: float = y
        # Combat and movement profiles (Server enforcement stats)
        self.speed: float = 2.0
        self.attack_range: float = 50.0
        self.attack_cooldown: int = 1000
        self.last_attack_time = 0
    
    def update_server_state(self, collision_rects: List[pygame.Rect], entities: Optional[List[Entity]] = None) -> list:
        """
        Processes the minion's behavior loop on the server instance.

        Returns a list of (target, damage) tuples for tower hits so the game loop
        can relay them as server-authoritative hit events.
        """
        super().update_server_state(collision_rects, entities)
        if not self.alive or entities is None:
            return []
        self._decide_action(entities)
        return self._move_or_attack(collision_rects)
    
    def _decide_action(self, entities: List[Entity]) -> None:
        # Drop dead target
        if self.target is not None and not self.target.alive:
            self.target = None

        # Leash: stop chasing a non-minion (champion) if too far from spawn anchor
        if self.target is not None and not isinstance(self.target, Minion):
            dist_from_spawn = pygame.math.Vector2(self.x - self.spawn_x, self.y - self.spawn_y).length()
            if dist_from_spawn > LEASH_RANGE:
                self.target = None

        # Sticky: keep current target — never switch while it's alive and in leash
        if self.target is not None:
            return

        # Acquire new target: enemy minions have priority over champions/objectives
        best_minion: Optional[Entity] = None
        best_minion_dist = float('inf')
        best_other: Optional[Entity] = None
        best_other_dist = float('inf')

        for entity in entities:
            if not (hasattr(entity, 'team') and entity.team != self.team and entity.alive):
                continue
            dist = pygame.math.Vector2(entity.x - self.x, entity.y - self.y).length()
            if dist >= AGGRO_RANGE:
                continue
            if isinstance(entity, Minion):
                if dist < best_minion_dist:
                    best_minion_dist = dist
                    best_minion = entity
            else:
                if dist < best_other_dist:
                    best_other_dist = dist
                    best_other = entity

        self.target = best_minion if best_minion is not None else best_other
    
    def _move_or_attack(self, collision_rects: List[pygame.Rect]) -> list:
        """
        Manages directional movement pathing or shifts states into active combat routines.
        Returns a list of (target, damage) for tower hits (not applied locally).
        """
        dx, dy = 0.0, 0.0

        if self.target is None:
            # Neutral Lane Pushing: Path diagonally across the map towards opposing bases
            if self.team == "blue":
                dx = self.speed
                dy = -self.speed
            else:
                dx = -self.speed
                dy = self.speed
        else:
            # Aggressive Engagement: Calculate approach bounds to acquired threat
            distance = pygame.math.Vector2(self.target.x - self.x, self.target.y - self.y).length()
            if distance > self.attack_range:
                if self.x < self.target.x:
                    dx += self.speed
                if self.x > self.target.x:
                    dx -= self.speed
                if self.y < self.target.y:
                    dy += self.speed
                if self.y > self.target.y:
                    dy -= self.speed
            else:
                # Target within parameters, trigger operational weapon calculations
                return self._execute_attack()

        # AABB collision — X axis
        self.rect.x = int(self.x + dx)
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dx > 0:
                    self.rect.right = rect.left
                elif dx < 0:
                    self.rect.left = rect.right
        self.x = float(self.rect.x)

        # AABB collision — Y axis
        self.rect.y = int(self.y + dy)
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dy > 0:
                    self.rect.bottom = rect.top
                elif dy < 0:
                    self.rect.top = rect.bottom
        self.y = float(self.rect.y)
        return []

    def _execute_attack(self) -> list:
        """
        Applies attack damage to the current target if cooldown allows.
        For tower targets, damage is NOT applied locally (server-authoritative);
        instead returns [(target, damage)] so game.py can relay as a hit event.
        """
        from game.entities.tower import Tower
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if self.target and self.target.alive:
                self.last_attack_time = current_time
                if isinstance(self.target, Tower):
                    return [(self.target, self.damage)]
                self.target.take_damage(self.damage)
        return []
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """Overrides the rendering pipeline to draw the minion asset texture.

        Args:
            screen (pygame.Surface): Screen workspace to blit graphical details onto.
            camera (_type_): Active viewport manager controlling translation offsets.
        """
        # Instead of an empty method, we lean onto Entity's drawing framework
        # which correctly computes camera position shifts and updates the health overlay.
        super().draw(screen, camera)