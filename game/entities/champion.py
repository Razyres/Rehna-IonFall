import pygame
import math
from typing import List, Optional, Tuple, Dict
from entity import Entity
from sprites import Sprite
from projectile import Projectile

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