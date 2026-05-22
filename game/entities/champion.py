import pygame
import math
from typing import List, Optional, Tuple, Dict
from .entity import Entity
from .sprites import Sprite
from .projectile import Projectile

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
            self.bullet_asset: str = f"{sprite_path}/bullet_{sprite_prefix}.png"
        else:
            self.bullet_asset = ""
        # Initialize base Entity structures
        super().__init__(x, y, width, height, initial_surface, hp)
        # Gameplay Stats (server Authoritative)
        self.speed: float = speed
        # Combat Cooldowns and Safe States(Server Authoritative)
        self.last_hit_time: int = 0
        self.next_hit_cooldown: int = 500 # Invulnerability frame padding in milliseconds
        self.last_shot_time: int = 0
        self.shot_cooldown: int = 300 # Basic attack fire rate limit in milliseconds
    
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
            None
        # Cooldown checkpoint using server ticks runtime clocks
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.shot_cooldown:
            self.last_shot_time = current_time
            # Instantiate a generic projectile context on server (Asset path provided for clients later)
            return Projectile(self.x, self.y, dx / distance, dy / distance, 10, 100, 30, self.bullet_asset)
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
        # Validate internal invulnerability windows to prevent instant bursting mechanics
        if current_time - self.last_hit_time >= self.next_hit_cooldown:
            self.hp -= damage
            self.last_hit_time = current_time
            print(f"Champion Hit. Remaining HP: {self.hp}")
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
        if inputs.get("b"):
            print(f"{self.x}, {self.y}")
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
    
    def draw(self, screen: pygame.Surface, camera) -> None:
        """
        Syncs active rendering components and handles pipeline blitting processes.

        Args:
            screen (pygame.Surface): Screen workspace to display pixels onto.
            camera (_type_): Active viewport tracker applying transformation offsets.
        """
        if self.sprites:
            # Update root image placeholder right before drawing sequence triggers
            self.image = self.sprites.current_sprite
        super().draw(screen, camera)