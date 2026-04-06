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

CHAMPIONS_CONFIG = {
    "Ordinateur": {"sprite_prefix": "0RD1N4T3UR", "speed": 5, "hp": 100},
    "Freud":     {"sprite_prefix": "pretresse",  "speed": 5, "hp": 120},
    "Vagabon": {"sprite_prefix": "Vagabon", "speed": 5, "hp" : 100}
}

if chosen_champion and chosen_champion in CHAMPIONS_CONFIG:
    config = CHAMPIONS_CONFIG[chosen_champion]
    game = Game(screen, clock)
    spawn_x, spawn_y = 120, 1430
    player = Champion(spawn_x, spawn_y,config["speed"], "sprite", config["sprite_prefix"], config["hp"])
    game.player = player
    game.add_entity(player)
    game.run()

pygame.quit()

