import pygame
import math
from typing import Optional
from game.entities.entity import Entity
from game.entities.minions import Minion


class TowerProjectile:
    """Visual homing projectile fired by a tower. Tracks a single target entity."""

    def __init__(self, x: float, y: float, target, speed: float, damage: int):
        self.x = x
        self.y = y
        self.target = target
        self.speed = speed
        self.damage = damage
        self.alive = True

    def update(self) -> bool:
        """Move toward target. Returns True on hit, False otherwise."""
        if not self.alive:
            return False
        if self.target is None or not self.target.alive:
            self.alive = False
            return False
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist <= self.speed:
            self.alive = False
            return True
        self.x += (dx / dist) * self.speed
        self.y += (dy / dist) * self.speed
        return False

    def draw(self, screen: pygame.Surface, camera) -> None:
        if not self.alive:
            return
        sx, sy = camera.apply_pos(self.x, self.y)
        radius = max(4, int(6 * camera.zoom))
        pygame.draw.circle(screen, (255, 200, 50), (int(sx), int(sy)), radius)


class Tower(Entity):
    """
    Represents a static defensive structure that fires homing projectiles at nearby enemies.

    Minions are prioritized over champions. On hit, minion damage is applied locally;
    champion damage is returned as (entity, damage) tuples for the game loop to relay
    as server-authoritative hit events. One projectile in-flight at a time.
    """

    def __init__(self, x: float, y: float, image: Optional[pygame.Surface], team: str, hp: int = 500):
        if image is not None:
            br = image.get_bounding_rect()
            cropped = pygame.Surface((br.width, br.height), pygame.SRCALPHA)
            cropped.blit(image, (0, 0), br)
            image = cropped
            w, h = br.width, br.height
        else:
            w, h = 64, 64
        super().__init__(x, y, w, h, image, hp)
        self.team = team

        self.range: float = 250.0
        self.damage: int = 40
        self.attack_cooldown: int = 1200
        self.last_attack_time: int = 0
        self.target = None
        self.projectile: Optional[TowerProjectile] = None

    def update_server_state(self, entities: list) -> list:
        """
        Advances the active projectile and manages targeting/firing.

        Returns a list of (target_entity, damage) tuples for champion hits only.
        The caller must convert these into server-authoritative hit events.
        """
        if not self.alive:
            self.projectile = None
            return []

        # Advance active projectile — wait for it to resolve before firing again
        if self.projectile is not None:
            if self.projectile.alive:
                hit = self.projectile.update()
                if hit:
                    target = self.projectile.target
                    self.projectile = None
                    if isinstance(target, Minion):
                        target.take_damage(self.damage)
                        return []
                    return [(target, self.damage)]
                return []
            else:
                self.projectile = None

        # Drop dead or out-of-range target
        if self.target is not None:
            if not self.target.alive or self._dist(self.target) > self.range:
                self.target = None

        if self.target is None:
            self.target = self._find_target(entities)

        if self.target is None:
            return []

        # Fire new projectile if cooldown ready
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = current_time
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            self.projectile = TowerProjectile(cx, cy, self.target, speed=5.0, damage=self.damage)

        return []

    def _find_target(self, entities: list):
        best_minion = None
        best_minion_dist = self.range
        best_other = None
        best_other_dist = self.range

        for entity in entities:
            if isinstance(entity, Tower):
                continue
            if not (hasattr(entity, 'team') and entity.team != self.team and entity.alive):
                continue
            dist = self._dist(entity)
            if isinstance(entity, Minion):
                if dist < best_minion_dist:
                    best_minion_dist = dist
                    best_minion = entity
            else:
                if dist < best_other_dist:
                    best_other_dist = dist
                    best_other = entity

        return best_minion if best_minion is not None else best_other

    def _dist(self, entity) -> float:
        return pygame.math.Vector2(entity.x - self.x, entity.y - self.y).length()

    def draw(self, screen: pygame.Surface, camera) -> None:
        super().draw(screen, camera)
        if self.projectile is not None and self.projectile.alive:
            self.projectile.draw(screen, camera)
