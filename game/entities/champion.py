import pygame
from .entity import Entity

class Champion(Entity):
    def __init__(self, x, y, speed, height, width, sprite_d, hp, sprite_up, sprite_ul, sprite_ur, sprite_l, sprite_r, sprite_dl, sprite_dr):
        super().__init__(x, y, width, height, sprite_d)
        self.speed = speed
        self.hp = hp
        self.last_hit_time = 0
        self.next_hit = 500
        self.sprite_d = sprite_d
        self.sprite_dl = sprite_dl
        self.sprite_dr = sprite_dr
        self.sprite_l = sprite_l
        self.sprite_r = sprite_r
        self.sprite_up = sprite_up
        self.sprite_ul = sprite_ul
        self.sprite_ur = sprite_ur
        
    
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
        if keys[pygame.K_z] and keys[pygame.K_q]:
            self.y -= self.speed
            self.x -= self.speed
            self.sprite = self.sprite_ul
        elif keys[pygame.K_z] and keys[pygame.K_d]:
            self.y -= self.speed
            self.x += self.speed
            self.sprite = self.sprite_ur
        elif keys[pygame.K_s] and keys[pygame.K_q]:
            self.y += self.speed
            self.x -= self.speed
            self.sprite = self.sprite_dl
        elif keys[pygame.K_s] and keys[pygame.K_d]:
            self.y += self.speed
            self.x += self.speed
            self.sprite = self.sprite_dr
        elif keys[pygame.K_z]:
            self.y -= self.speed
            self.sprite = self.sprite_up
        elif keys[pygame.K_q]:
            self.x -= self.speed
            self.sprite = self.sprite_l
        elif keys[pygame.K_s]:
            self.y += self.speed
            self.sprite = self.sprite_d
        elif keys[pygame.K_d]:
            self.x += self.speed
            self.sprite = self.sprite_r
            
    def draw(self, screen, camera):
        if self.sprite:
            screen_x, screen_y = camera.apply(self)
            screen.blit(self.sprite, (screen_x, screen_y))