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
    
    def take_damage(self, damage):
        if self.hp <= 0:
            self.alive = False
        else:
            now = pygame.time.get_ticks()
            if now - self.last_hit_time >= self.next_hit:
                self.hp -= damage
                self.last_hit_time = now
                print("HP : ", self.hp)
    
    def update(self, event):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            self.y -= self.speed
        if keys[pygame.K_q]:
            self.x -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_d]:
            self.x += self.speed
            
    def draw(self, screen, camera):
        if self.sprite:
            screen_x, screen_y = camera.apply(self)
            self.sprites.rect.topleft = (screen_x, screen_y)
            self.sprites.draw(screen)