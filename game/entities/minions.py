import pygame
from typing import List, Optional
from .enemy import Enemy
from .entity import Entity
from .sprites import MinionSprite

AGGRO_RANGE = 200.0
LEASH_RANGE = 400.0

class Minion(Enemy):
    """
    Represents an automated lane minion (creep) within MOBA environment.

    Handles lane-pushing AI, basic enemy aggregation, distance-based pathfinding,
    and periodic combat engagements. This class decouples authoritative server physics
    and targeting logic from client-side texture rendering.
    """

    def __init__(self, x: float, y: float, team: str, sprite_folder: str = "sprite"):
        """
        Initializes a new Minion instance.

        Args:
            x (float): The initial world X coordinate.
            y (float): The initial world Y coordinate.
            team (str): The alignment faction of the minion ('blue' or 'red').
            sprite_folder (str): Path to the sprite assets folder (client-side usage).
        """
        self.sprites: Optional[MinionSprite] = None
        width, height = 22, 22
        initial_surface = None
        try:
            self.sprites = MinionSprite(sprite_folder, team)
            width = self.sprites.width
            height = self.sprites.height
            initial_surface = self.sprites.current_sprite
        except Exception:
            pass

        super().__init__(x, y, width, height, initial_surface, damage=5, hp=100)
        self.team: str = team
        self.minion_id: int = -1
        self.target: Optional[Entity] = None
        self.spawn_x: float = x
        self.spawn_y: float = y
        self.speed: float = 2.0
        self.attack_range: float = 50.0
        self.attack_cooldown: int = 1000
        self.last_attack_time = 0
        self.last_dx: float = 0.0
        self.last_dy: float = 0.0

    def update_client_animation(self, dx: float, dy: float) -> None:
        """Updates the directional sprite based on movement vector (client-side)."""
        if self.sprites and (dx != 0 or dy != 0):
            self.sprites.set_direction(dx, dy)
            self.width = self.sprites.width
            self.height = self.sprites.height

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

        if self.target is not None and not self.target.alive:
            self.target = None

        if self.target is not None and not isinstance(self.target, (Tower, Nexus)):
            if pygame.math.Vector2(self.x - self.spawn_x, self.y - self.spawn_y).length() > LEASH_RANGE:
                self.target = None

        if self.target is not None and not isinstance(self.target, (Tower, Nexus)):
            return

        best_unit: Optional[Entity] = None
        best_unit_dist = AGGRO_RANGE
        best_structure: Optional[Entity] = None
        best_structure_dist = float('inf')

        for entity in entities:
            if not (hasattr(entity, 'team') and entity.team != self.team and entity.alive):
                continue
            if hasattr(entity, 'dx'):
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

        # Store last movement for animation sync
        if dx != 0 or dy != 0:
            self.last_dx = dx
            self.last_dy = dy
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
        """Overrides the rendering pipeline to draw the minion directional sprite."""
        if self.sprites:
            self.image = self.sprites.current_sprite
        super().draw(screen, camera)
