import pygame
import pytmx
import sys
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from game.entities.champion import Champion
from game.entities.enemy import Enemy
from game.world.map import GameMap
import os
current_dir = os.path.dirname(__file__)
game_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(game_dir)
map_path = os.path.join(project_root, "MAP", "map.tmx")

class Game :
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.entities = []
        self.player = None
        self.game_map = GameMap(map_path)
        self.camera_x = 0
        self.camera_y = 0
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "stop"
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_z]:
            return "z"
        if pressed[pygame.K_q]:
            return "q"
        if pressed[pygame.K_s]:
            return "s"
        if pressed[pygame.K_d]:
            return "d"
        
    def update(self, event):
        for entity in self.entities:
            entity.update(event)
        #Collisions
        for entity in self.entities:
            if isinstance(entity, Enemy):
                if entity.get_rect().colliderect(self.player.get_rect()):
                    self.player.take_damage(entity.damage)
        #Death
        self.entities = [e for e in self.entities if not hasattr(e, "alive") or e.alive]
        if self.player.alive == False :
            self.running = False
    
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen, (self.camera_x, self.camera_y))
        for entity in self.entities:
            entity.draw(self.screen)
        pygame.display.flip()
    
    def add_entity(self, entity):
        self.entities.append(entity)
    
    def run(self):
        while self.running:
            event = self.handle_events()
            if event == "stop":
                self.running = False
            else :
                self.update(event)
            self.draw()
            self.clock.tick(60)

pygame.init()

screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()
game = Game(screen, clock)
image = pygame.image.load("sprite/ORD1NAT3UR_face.png")
image_pres = pygame.transform.scale(image, (400, 320))
ORD1NAT3UR = Champion(10, 10, 5, 40, 32, image, 100)
game.player = ORD1NAT3UR
game.add_entity(ORD1NAT3UR)
enemy_sprit = pygame.image.load("sprite/rick-astley.png")
enemy_sprite = pygame.transform.scale(enemy_sprit, (180, 140))
enemy = Enemy(100, 100, 180, 140, enemy_sprite, 40)
game.add_entity(enemy)
game.run()

pygame.quit()
