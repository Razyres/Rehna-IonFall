import pygame
import sys
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from game.entities.champion import Champion
from game.entities.enemy import Enemy

class Game :
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.entities = []
        self.player = None
    
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
    
    def draw(self):
        self.screen.fill((0, 0, 0))
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
ORD1NAT3UR = Champion(10, 10, 10, 40, 32, image, 100)
game.player = ORD1NAT3UR
game.add_entity(ORD1NAT3UR)
enemy_sprit = pygame.image.load("sprite/rick-astley.png")
enemy_sprite = pygame.transform.scale(enemy_sprit, (45, 32))
enemy = Enemy(100, 100, 45, 32, enemy_sprite, 40)
game.add_entity(enemy)
game.run()

pygame.quit()
