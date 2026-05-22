import pygame
import math
from typing import Callable, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities.champion import Champion


class Ability:
    """Active ability slot with cooldown tracking and execution logic."""

    def __init__(self, name: str, key_label: str, cooldown_ms: int, execute_fn: Callable):
        self.name = name
        self.key_label = key_label
        self.cooldown_ms = cooldown_ms
        self.last_used_ms: int = -cooldown_ms  # Ready from game start
        self._execute = execute_fn

    @property
    def is_ready(self) -> bool:
        return pygame.time.get_ticks() - self.last_used_ms >= self.cooldown_ms

    @property
    def cooldown_fraction(self) -> float:
        """1.0 = ready, 0.0 = just used."""
        elapsed = pygame.time.get_ticks() - self.last_used_ms
        return min(1.0, elapsed / self.cooldown_ms)

    @property
    def cooldown_remaining_s(self) -> float:
        remaining = self.cooldown_ms - (pygame.time.get_ticks() - self.last_used_ms)
        return max(0.0, remaining / 1000.0)

    def try_use(self, champion: Any, world_mx: float, world_my: float) -> Optional[List]:
        if not self.is_ready:
            return None
        self.last_used_ms = pygame.time.get_ticks()
        result = self._execute(champion, world_mx, world_my)
        return result if result is not None else []


# ---------------------------------------------------------------------------
# Ability factories
# ---------------------------------------------------------------------------

def _direction_to_mouse(champ: Any, mx: float, my: float):
    dx = mx - champ.x
    dy = my - champ.y
    dist = math.sqrt(dx**2 + dy**2)
    if dist == 0:
        return None, None
    return dx / dist, dy / dist


def make_heal(cooldown_ms: int = 10000, hp_restore: int = 30) -> Ability:
    def execute(champ, mx, my):
        champ.pending_heal = hp_restore  # Server applies the heal authoritatively
        return []
    return Ability("Soin", "E", cooldown_ms, execute)


def make_heavy_shot(cooldown_ms: int = 5000, damage: int = 60, speed: float = 6.0) -> Ability:
    from game.entities.projectile import Projectile
    def execute(champ, mx, my):
        ndx, ndy = _direction_to_mouse(champ, mx, my)
        if ndx is None:
            return []
        proj = Projectile(champ.x, champ.y, ndx, ndy, speed, damage, 50, champ.bullet_asset)
        return [proj]
    return Ability("Impact", "R", cooldown_ms, execute)


def make_dash(cooldown_ms: int = 8000, distance: int = 150) -> Ability:
    def execute(champ, mx, my):
        ddx, ddy = champ.last_dx, champ.last_dy
        dist = math.sqrt(ddx**2 + ddy**2)
        if dist > 0:
            champ.x += (ddx / dist) * distance
            champ.y += (ddy / dist) * distance
            champ.rect.x = int(champ.x)
            champ.rect.y = int(champ.y)
        return []
    return Ability("Schift", "E", cooldown_ms, execute)


def make_burst(cooldown_ms: int = 6000, damage: int = 20, count: int = 5) -> Ability:
    from game.entities.projectile import Projectile
    def execute(champ, mx, my):
        ndx, ndy = _direction_to_mouse(champ, mx, my)
        if ndx is None:
            return []
        base_angle = math.atan2(ndy, ndx)
        spread = math.pi / 5
        projs = []
        for i in range(count):
            angle = base_angle + spread * (i - count // 2) / max(count - 1, 1)
            projs.append(Projectile(champ.x, champ.y, math.cos(angle), math.sin(angle), 10, damage, 30, champ.bullet_asset))
        return projs
    return Ability("IEM", "R", cooldown_ms, execute)


def make_curse(cooldown_ms: int = 7000, damage: int = 15, duration_ms: int = 4000) -> Ability:
    from game.entities.projectile import Projectile
    def execute(champ, mx, my):
        ndx, ndy = _direction_to_mouse(champ, mx, my)
        if ndx is None:
            return []
        proj = Projectile(champ.x, champ.y, ndx, ndy, 5, damage, 60, champ.bullet_asset)
        proj.is_curse = True
        proj.curse_duration_ms = duration_ms
        return [proj]
    return Ability("Malediction", "R", cooldown_ms, execute)
