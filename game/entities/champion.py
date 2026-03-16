import pygame
from .entity import Entity
from .sprites import Sprite

class Champion(Entity):
    def __init__(self, x, y, speed, height, width, sprite_path: str ,sprite_prefix: str, hp):
        self.sprites = Sprite(sprite_path, sprite_prefix, width, height)
        super().__init__(x, y, width, height, self.sprites.current_sprite)
        self.speed = speed
        self.hp = hp
        self.last_hit_time = 0
        self.next_hit = 500
        self.rect = self.get_rect()
    
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
        if keys[pygame.K_z]: dy -= self.speed
        if keys[pygame.K_q]: dx -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_d]: dx += self.speed

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