import pygame
import math
from .entity import Entity
from .sprites import Sprite
from .projectile import Projectile
class Champion(Entity):
    def __init__(self, x, y, speed, height, width, sprite_path: str ,sprite_prefix: str, hp):
        self.sprites = Sprite(sprite_path, sprite_prefix, width, height)
        super().__init__(x, y, width, height, self.sprites.current_sprite)
        self.speed = speed
        self.hp = hp
        self.last_hit_time = 0
        self.next_hit = 500
        self.rect = self.get_rect()
        self.last_shot = 0
        self.cooldown = 300
    
    def attack(self, camera):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x / camera.zoom + camera.x
        world_mouse_y = mouse_y / camera.zoom + camera.y
        dx = world_mouse_x - self.x
        dy = world_mouse_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return None
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.cooldown:
            self.last_shot = now
            return Projectile(self.x, self.y, dx/dist, dy/dist, 10, 20, 30, "sprite/bullet_0RD1N4T3UR_W.png")
        
    
    def take_damage(self, damage):
        if self.hp <= 0:
            self.alive = False
        else:
            now = pygame.time.get_ticks()
            if now - self.last_hit_time >= self.next_hit:
                self.hp -= damage
                self.last_hit_time = now
                print("HP : ", self.hp)
    
    def update(self, event, collision_rects):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_z] and keys[pygame.K_q]:
            dy -= self.speed//1.5
            dx -= self.speed//1.5
        elif keys[pygame.K_z] and keys[pygame.K_d]:
            dy -= self.speed//1.5
            dx += self.speed//1.5
        elif keys[pygame.K_s] and keys[pygame.K_q]:
            dy += self.speed//1.5
            dx -= self.speed//1.5
        elif keys[pygame.K_s] and keys[pygame.K_d]:
            dy += self.speed//1.5
            dx += self.speed//1.5
        elif keys[pygame.K_z]: dy -= self.speed
        elif keys[pygame.K_q]: dx -= self.speed
        elif keys[pygame.K_s]: dy += self.speed
        elif keys[pygame.K_d]: dx += self.speed
        

        self.rect.x = self.x + dx
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dx > 0: self.rect.right = rect.left
                if dx < 0: self.rect.left = rect.right
        self.x = self.rect.x
        self.rect.y = self.y + dy
        for rect in collision_rects:
            if self.rect.colliderect(rect):
                if dy > 0: self.rect.bottom = rect.top
                if dy < 0: self.rect.top = rect.bottom
        self.y = self.rect.y
        self.sprites.set_direction(dx, dy)

    
    def draw(self, screen, camera):
        if self.sprite:
            screen_x, screen_y = camera.apply(self)
            self.sprites.rect.topleft = (int(screen_x), int(screen_y))
            self.sprites.draw(screen)