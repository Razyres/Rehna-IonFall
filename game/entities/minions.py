#Nico création minions
import pygame
from .entity import Entity
from .enemy import Enemy


class Minion(Enemy):
    def __init__(self, x, y, width, height, sprite, team):
        super().__init__(x, y, width, height, sprite, damage=5, hp=100)
        self.team = team
        self.target = None
        self.speed = 2
        self.attack_range = 50
        self.attack_cooldown = 1000  
        self.last_attack_time = 0

    def update(self, event, collision_rects,entities):
        super().update(event, collision_rects,entities)
        if self.alive:
            self.decide_action(entities)
            self.move()
        

    def decide_action(self, entities):
        if self.target and not self.target.alive:
            self.target = None
        for entity in entities:
            if hasattr(entity, 'team') and entity.team != self.team and entity.alive:
                dist = pygame.math.Vector2(entity.x - self.x, entity.y - self.y).length()
                if dist < 150:
                    self.target = entity
                    break

    def move(self):
        if self.target is None:
            if self.team == "blue":
                    self.x += self.speed  
                    self.y -= self.speed  
            else:
                    self.x -= self.speed  
                    self.y += self.speed
        else:
            dist = pygame.math.Vector2(self.target.x - self.x, self.target.y - self.y).length()
            if dist > self.attack_range:
                if self.x < self.target.x: 
                    self.x += self.speed
                if self.x > self.target.x:
                    self.x -= self.speed
                if self.y < self.target.y: 
                    self.y += self.speed
                if self.y > self.target.y: 
                    self.y -= self.speed
            else:
                self.attack()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def attack(self):
        tmps = pygame.time.get_ticks()
        if tmps - self.last_attack_time > self.attack_cooldown:
            self.target.take_damage(self.damage)
            self.last_attack_time = tmps
    
    def draw(screen, camera, wtf):
        pass