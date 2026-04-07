from .entity import Entity
import pygame
class Enemy(Entity):
    def __init__(self, x, y, width, height, sprite, damage, hp):
        super().__init__(x, y, width, height, sprite)
        self.damage = damage
        self.hp = hp
    
    def take_damage(self, damage):
        self.hp -= damage
        print("Enemy HP : ", self.hp)
        if self.hp <= 0:
            self.alive = False
    
    def update(self, event, collision_rects):
        pass
    
    def draw(self, screen, camera):
        if self.image:
            screen_x, screen_y = camera.apply(self)
            screen.blit(self.image, (int(screen_x), int(screen_y)))