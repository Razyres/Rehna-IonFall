import pygame
from .entity import Entity

class Champion(Entity):
    def __init__(self, x, y, speed, height, width, sprite, hp):
        super().__init__(x, y, width, height, sprite)
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
        if event == "z":
            self.y -= self.speed
        if event == "q":
            self.x -= self.speed
        if event == "s":
            self.y += self.speed
        if event == "d":
            self.x += self.speed
    
    def draw(self, screen, camera):
        if self.sprite:
            rect = self.get_rect()
            screen_rect = camera.apply(rect)
            scaled_image = pygame.transform.scale(self.sprite, (screen_rect.width, screen_rect.height))
            screen.blit(scaled_image, screen_rect)
