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
        self.minion_id: int = -1  # Assigned by player 0; used for cross-client sync
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
        from game.entities.tower import Tower
        from game.entities.nexus import Nexus

        # Drop dead target
        if self.target is not None and not self.target.alive:
            self.target = None

        # Leash: release unit targets (not structures) if too far from anchor
        if self.target is not None and not isinstance(self.target, (Tower, Nexus)):
            if pygame.math.Vector2(self.x - self.spawn_x, self.y - self.spawn_y).length() > LEASH_RANGE:
                self.target = None

        # Sticky: don't switch away from a unit target while it's still alive
        if self.target is not None and not isinstance(self.target, (Tower, Nexus)):
            return

        # Scan entities: units within AGGRO_RANGE have priority; structures are lane objectives
        best_unit: Optional[Entity] = None
        best_unit_dist = AGGRO_RANGE
        best_structure: Optional[Entity] = None
        best_structure_dist = float('inf')

        for entity in entities:
            if not (hasattr(entity, 'team') and entity.team != self.team and entity.alive):
                continue
            if hasattr(entity, 'dx'):  # skip projectiles
                continue
            dist = pygame.math.Vector2(entity.x - self.x, entity.y - self.y).length()
            if isinstance(entity, (Tower, Nexus)):
                if dist < best_structure_dist:
                    best_structure_dist = dist
                    best_structure = entity
            else:
                if dist < best_unit_dist:
                    best_unit_dist = dist
                    best_unit = entity

        # Units beat structures; structures are always targeted as lane objective
        if best_unit is not None:
            self.target = best_unit
        elif best_structure is not None:
            self.target = best_structure
    
    def _move_or_attack(self, collision_rects: List[pygame.Rect]) -> list:
        """
        Manages directional movement pathing or shifts states into active combat routines.
        Returns a list of (target, damage) for tower hits (not applied locally).
        """
        dx, dy = 0.0, 0.0

        if self.target is None:
            # Fallback diagonal push when no objective found (normalized)
            norm = 1.4142
            dx = (self.speed / norm) * (1 if self.team == "blue" else -1)
            dy = (self.speed / norm) * (-1 if self.team == "blue" else 1)
        else:
            from game.entities.tower import Tower
            from game.entities.nexus import Nexus
            mcx = self.x + self.width / 2
            mcy = self.y + self.height / 2
            tx = self.target.x + getattr(self.target, 'width', 0) / 2
            ty = self.target.y + getattr(self.target, 'height', 0) / 2
            vec = pygame.math.Vector2(tx - mcx, ty - mcy)
            # For structures use nearest-point-on-rect so the minion attacks on contact
            # regardless of which edge it presses against (avoids sliding-behind bug)
            if isinstance(self.target, (Tower, Nexus)):
                tr = pygame.Rect(self.target.x, self.target.y, self.target.width, self.target.height)
                nx = max(tr.left, min(mcx, tr.right))
                ny = max(tr.top, min(mcy, tr.bottom))
                distance = pygame.math.Vector2(mcx - nx, mcy - ny).length()
            else:
                distance = vec.length()
            if distance > self.attack_range:
                if vec.length() > 0:
                    norm_vec = vec.normalize()
                    dx = norm_vec.x * self.speed
                    dy = norm_vec.y * self.speed
            else:
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
        Returns [(target, damage)] if the cooldown allows an attack this frame.
        All hit resolution is delegated to the game loop so each target type
        (tower, player, minion) is handled server-authoritatively.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            if self.target and self.target.alive:
                self.last_attack_time = current_time
                return [(self.target, self.damage)]
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