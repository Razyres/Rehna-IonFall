import pygame
import math
from typing import Any, List, Optional, Tuple, Dict
from .entity import Entity
from .sprites import Sprite
from .projectile import Projectile
from game.utils import resource_path

_XP_TO_NEXT = (100, 180, 280, 400)  # XP to level up, indexed by (level - 1)
_HP_PER_LEVEL = 15
_DMG_PER_LEVEL = 0.10
MAX_LEVEL = 5

class Champion(Entity):
    """Represents a playable champion within the MOBA environment.
    
    Handles player inputs, server-side movement physics with wall collisions,
    combat cooldowns, projectile spawning, and client-side multidirectional animations.
    """
    
    def __init__(self, x: float, y: float, speed: float, sprite_path: Optional[str], sprite_prefix: Optional[str], hp: int):
        """
        Initializes a new Champion instance.

        Args:
            x (float): The initial X coordinate in the game world.
            y (float): The initial Y coordinate in the game world.
            speed (float): The base movement speed of the champion.
            sprite_path (Optional[str]): System path to the character assets (Client-side usage).
            sprite_prefix (Optional[str]): Asset identifier prefix for animations (Clients-side usage).
            hp (int): The initial and maximum health points pool.
        """
        # Client-side: Initialize directional sprite sheet manager if assets are provided
        self.sprites: Optional[Sprite] = None
        width, height = 32, 32 # Default fallback dimensions for server simulation
        initial_surface = None
        if sprite_path and sprite_prefix:
            self.sprites = Sprite(sprite_path, sprite_prefix)
            width, height = self.sprites.width, self.sprites.height
            initial_surface = self.sprites.current_sprite
            self.bullet_asset: str = resource_path(f"sprite/bullet_{sprite_prefix}.png")
        else:
            self.bullet_asset = ""
        # Initialize base Entity structures
        super().__init__(x, y, width, height, initial_surface, hp)
        self.max_hp: int = hp
        # Gameplay Stats (server Authoritative)
        self.speed: float = speed
        # Combat Cooldowns and Safe States (Server Authoritative)
        self.last_hit_time: int = 0
        self.next_hit_cooldown: int = 500
        self.last_shot_time: int = 0
        self.shot_cooldown: int = 300
        # Ability slots (assigned from main.py per champion)
        self.ability_q: Optional[Any] = None
        self.ability_e: Optional[Any] = None
        # Last movement direction used by dash abilities
        self.last_dx: float = 0.0
        self.last_dy: float = 0.0
        # Curse state (applied by Vagabon's E — doubles incoming damage for a duration)
        self.curse_multiplier: float = 1.0
        self.curse_end_ms: int = 0
        # Team attribution (assigned from network player_id : 0=blue, 1=red)
        self.team: str = ""
        # Pending heal to report to server (set by make_heal ability or level-up)
        self.pending_heal: int = 0
        # XP and leveling
        self.level: int = 1
        self.xp: int = 0
        self.damage_multiplier: float = 1.0
    
    def process_attack_intent(self, world_mouse_x: float, world_mouse_y: float) -> Optional[Projectile]:
        """
        Evaluates a client projectile fire request against authoritative server cooldown metrics.
        
        This method executes exclusively on the Server loop.

        Args:
            world_mouse_x (float): Translated targeting world X coordinates.
            world_mouse_y (float): Translated targeting world Y coordinates.

        Returns:
            Optional[Projectile]: A newly spawned Projectile object, or None if restricted by cooldowns
        """
        dx = world_mouse_x - self.x
        dy = world_mouse_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        if distance == 0:
            return None
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            self.last_shot_time = current_time
            return Projectile(self.x, self.y, dx / distance, dy / distance, 10, int(30 * self.damage_multiplier), 30, self.bullet_asset)
        return None
    
    def take_damage(self, damage: int) -> None:
        """
        Deducts health tokens from the active instance after validating safe state timers.
        
        This method excutes exclusively on the Server loop.

        Args:
            damage (int): Amount of health metrics to deduct.
        """
        if not self.alive:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_hit_time >= self.next_hit_cooldown:
            self.hp -= damage
            self.last_hit_time = current_time
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
    
    def update_server_state(self, inputs: Dict[str, bool], collision_rects: List[pygame.Rect]) -> Tuple[float, float]:
        """
        Processes directionel vector intentions and updates coordinates against physical obstacle.
        
        This method executes exclusively on the Server loop. It strips out local keyboard
        bindings to rely on mapped boolean network packets.

        Args:
            inputs (Dict[str, bool]): Dictionary mapping movement inputs ('z', 'q', 's', 'd').
            collision_rects (List[pygame.Rect]): Global environment obstacle bounding boxes.

        Returns:
            Tuple[float, float]: Calculated displacement vectors (dx. dy) for animation sync.
        """
        dx, dy = 0.0, 0.0
        # Process diagonal positioning normalization speeds (prevents faster diagonal movement cheats)
        if inputs.get("z") and inputs.get("q"):
            dy -= self.speed / 1.2
            dx -= self.speed / 1.2
        elif inputs.get("z") and inputs.get("d"):
            dy -= self.speed / 1.2
            dx += self.speed / 1.2
        elif inputs.get("s") and inputs.get("q"):
            dy += self.speed / 1.2
            dx -= self.speed / 1.2
        elif inputs.get("s") and inputs.get("d"):
            dy += self.speed / 1.2
            dx += self.speed / 1.2
        else:
            if inputs.get("z"):
                dy -= self.speed
            if inputs.get("s"):
                dy += self.speed
            if inputs.get("q"):
                dx -= self.speed
            if inputs.get("d"):
                dx += self.speed
        # Explicit AABB Collision evaluation matrix: Axis-X
        self.rect.x = int(self.x + dx)
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dx > 0:
                    self.rect.right = rect.left
                if dx < 0:
                    self.rect.left = rect.right
        self.x = float(self.rect.x)
        # Explixit AABB Collision evaluation matrix: Axis-Y
        self.rect.y = int(self.y + dy)
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dy > 0:
                    self.rect.bottom = rect.top
                if dy < 0:
                    self.rect.top = rect.bottom
        self.y = float(self.rect.y)
        if dx != 0 or dy != 0:
            self.last_dx = dx
            self.last_dy = dy
        return dx, dy
    
    def update_client_animation(self, dx: float, dy: float) -> None:
        """
        Updates the client-side rendering dimensions and shifts framework frame directions.
        
        This method executes exclusively on the Client application.

        Args:
            dx (float): Calculated horizontal displacement shift velocity.
            dy (float): Calculated vertical displacement shift velocity.
        """
        if self.sprites:
            # Sync framework animation tracking structures
            self.sprites.set_direction(int(dx), int(dy))
            self.width = self.sprites.width
            self.height = self.sprites.height
    
    def add_xp(self, amount: int) -> None:
        """Awards XP and triggers level-ups until max level is reached."""
        if self.level >= MAX_LEVEL:
            return
        self.xp += amount
        while self.level < MAX_LEVEL and self.xp >= _XP_TO_NEXT[self.level - 1]:
            self.xp -= _XP_TO_NEXT[self.level - 1]
            self.level += 1
            self.max_hp += _HP_PER_LEVEL
            self.hp = min(self.hp + _HP_PER_LEVEL, self.max_hp)
            self.pending_heal += _HP_PER_LEVEL
            self.damage_multiplier += _DMG_PER_LEVEL

    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Syncs active rendering components and handles pipeline blitting processes.

        Args:
            screen (pygame.Surface): Screen workspace to display pixels onto.
            camera (_type_): Active viewport tracker applying transformation offsets.
        """
        if self.sprites:
            self.image = self.sprites.current_sprite
        super().draw(screen, camera)