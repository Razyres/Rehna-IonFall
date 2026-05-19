import pygame
import sys
from pathlib import Path

from game.core.game import Game
from game.ui.menu import Menu
from game.entities.champion import Champion

# Adjust runtime search directories path context references
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Fixed alignment with Menu dataset strings constraints
CHAMPIONS_CONFIG = {
    "Ordinateur": {"sprite_prefix": "0RD1N4T3UR", "speed": 5, "hp": 100},
    "Pretresse":  {"sprite_prefix": "pretresse",  "speed": 5, "hp": 120},
    "Vagabon":    {"sprite_prefix": "Vagabon",    "speed": 5, "hp": 100} 
}

def main() -> None:
    """
    Main entry point function driving client execution loop sequences.
    """
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    app_running = True
    
    while app_running:
        menu = Menu(screen)
        chosen_champion = menu.run()
        
        if not chosen_champion:
            app_running = False
            break
            
        config = CHAMPIONS_CONFIG[chosen_champion]
        game = Game(screen, clock)
        
        # Standard structural birth world vectors spawn location
        spawn_x, spawn_y = 120, 1430
        
        player = Champion(spawn_x, spawn_y, config["speed"], "sprite", config["sprite_prefix"], config["hp"])
        game.player = player
        game.add_entity(player)
        
        # Execute active runtime match loop orchestrations
        game_outcome = game.run()
        
        if game_outcome == "QUIT":
            app_running = False
            
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()