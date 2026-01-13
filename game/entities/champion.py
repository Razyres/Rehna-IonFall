import pygame
from .entity import Entity

class Champion(Entity):
    def __init__(self, x, y, speed, height, width, sprite):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = speed
        self.height = height
        self.width = width
        self.sprite = sprite
    
    def update(self, event):
        if event == "z":
            self.y -= self.speed
        if event == "q":
            self.x -= self.speed
        if event == "s":
            self.y += self.speed
        if event == "d":
            self.x += self.speed
    
    def draw(self, screen):
        print("DRAW", self.x, self.y)
        screen.blit(self.sprite, (self.x, self.y))
