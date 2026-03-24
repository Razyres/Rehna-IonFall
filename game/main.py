import pygame
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from game.core.game import Game
from game.ui.menu import Menu
from game.entities.champion import Champion
from game.entities.enemy import Enemy

pygame.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

menu = Menu(screen)
chosen_champion = menu.run()

if chosen_champion:
    game = Game(screen, clock)
    spawnx, spawny = 120, 1450
    ORD1N4T3UR = Champion(spawnx, spawny, 5, 86, 40, "sprite", "0RD1N4T3UR", 100)
    game.player = ORD1N4T3UR
    game.add_entity(ORD1N4T3UR)
    enemy = pygame.image.load("sprite/TheCop_S.png")
    enemy_sprite = pygame.transform.scale(enemy, (52, 94))
    enemy = Enemy(500, 500, 52, 94, enemy_sprite, 40, 100) 
    game.add_entity(enemy)
    enemy2 = pygame.image.load("sprite/Bunyon_S.png")
    enemy2_sprite = pygame.transform.scale(enemy2, (42, 102))
    enemy2 = Enemy(720, 720, 43, 102, enemy2_sprite, 20, 50)
    game.add_entity(enemy2)
    game.run()

pygame.quit()

