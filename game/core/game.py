import pygame
import sys
from pathlib import Path


root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from game.entities.champion import Champion

class Game :
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.running = True
        self.entities = []
    
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

screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
game = Game(screen, clock)
image = pygame.image.load("sprite/ORD1NAT3UR_face.png")
print(image)
ORD1NAT3UR = Champion(10, 10, 10, 40, 32, image)
game.add_entity(ORD1NAT3UR)
game.run()

pygame.quit()
