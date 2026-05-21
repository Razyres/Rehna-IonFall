import pygame
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from game.core.game import Game
from game.ui.menu import Menu
from game.entities.champion import Champion

CHAMPIONS_CONFIG = {
    "Ordinateur": {"sprite_prefix": "0RD1N4T3UR", "speed": 5, "hp": 100},
    "Freud":      {"sprite_prefix": "pretresse",  "speed": 5, "hp": 120},
    "Vagabon":    {"sprite_prefix": "Vagabon",    "speed": 5, "hp": 100},
}

# Points de spawn selon le slot réseau attribué par le serveur
SPAWN_POINTS = {
    0: (120.0, 1430.0),   # Joueur 0 — nexus bleu (bas)
    1: (1232.0, 220.0),   # Joueur 1 — nexus rouge (haut)
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

        # FIX: passer sprite_prefix à Game pour que Network l'envoie au serveur lors du handshake
        game = Game(screen, clock, sprite_prefix=config["sprite_prefix"])

        # FIX: spawn dynamique selon l'ID réseau reçu du serveur (0 = bas, 1 = haut)
        # Fallback sur le spawn joueur 0 si la connexion a échoué (my_id = None)
        player_id = game.my_id if game.my_id is not None else 0
        spawn_x, spawn_y = SPAWN_POINTS.get(player_id, SPAWN_POINTS[0])

        player = Champion(spawn_x, spawn_y, config["speed"], "sprite", config["sprite_prefix"], config["hp"])
        player.player_id = player_id
        game.player = player
        game.add_entity(player)
        
        game_outcome = game.run()
        
        if game_outcome == "QUIT":
            app_running = False
            
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()