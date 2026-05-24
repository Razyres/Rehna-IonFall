import pygame
import sys
import multiprocessing
import time
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from game.core.game import Game
from game.ui.menu import Menu
from game.entities.champion import Champion
from game.combat.ability import make_heal, make_heavy_shot, make_dash, make_burst, make_curse

CHAMPIONS_CONFIG = {
    "Freud":      {"sprite_prefix": "Freud",      "speed": 5, "hp": 110},
    "Ordinateur": {"sprite_prefix": "0RD1N4T3UR", "speed": 5, "hp": 100},
    "Pretresse":  {"sprite_prefix": "pretresse",  "speed": 5, "hp": 120},
    "Vagabon":    {"sprite_prefix": "Vagabon",    "speed": 5, "hp": 100},
}

# Q slot = touche E | E slot = touche R
ABILITIES = {
    "Freud":      {"q": make_dash(6000, 150),    "e": make_burst(8000, 20, 5)},
    "Pretresse":  {"q": make_heal(10000, 30),    "e": make_heavy_shot(5000, 60, 6.0)},
    "Ordinateur": {"q": make_dash(8000, 150),    "e": make_burst(6000, 20, 5)},
    "Vagabon":    {"q": make_dash(6000, 150),    "e": make_curse(7000, 15, 4000)},
}

# Points de spawn selon le slot réseau attribué par le serveur
SPAWN_POINTS = {
    0: (120.0, 1430.0),   # Joueur 0 — nexus bleu (bas)
    1: (1464.0, 103.0),   # Joueur 1 — nexus rouge (haut)
}

def _server_process() -> None:
    from game.reseau.serveur import main as server_main
    server_main()


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    app_running = True
    server_proc: multiprocessing.Process = None

    while app_running:
        menu = Menu(screen)
        chosen_champion, server_ip, is_host = menu.run()

        if not chosen_champion:
            app_running = False
            break

        if is_host:
            server_proc = multiprocessing.Process(target=_server_process, daemon=True)
            server_proc.start()
            time.sleep(1.2)  # Give the server time to bind the port

        config = CHAMPIONS_CONFIG[chosen_champion]

        game = Game(screen, clock, sprite_prefix=config["sprite_prefix"], server_ip=server_ip)

        # FIX: spawn dynamique selon l'ID réseau reçu du serveur (0 = bas, 1 = haut)
        # Fallback sur le spawn joueur 0 si la connexion a échoué (my_id = None)
        player_id = game.my_id if game.my_id is not None else 0
        spawn_x, spawn_y = SPAWN_POINTS.get(player_id, SPAWN_POINTS[0])

        player = Champion(spawn_x, spawn_y, config["speed"], "sprite", config["sprite_prefix"], config["hp"])
        player.player_id = player_id
        player.spawn_x = spawn_x
        player.spawn_y = spawn_y
        player.team = "blue" if player_id == 0 else "red"
        abilities = ABILITIES[chosen_champion]
        player.ability_q = abilities["q"]
        player.ability_e = abilities["e"]
        game.player = player
        game.add_entity(player)
        
        game_outcome = game.run()

        if server_proc is not None and server_proc.is_alive():
            server_proc.terminate()
            server_proc.join(timeout=2)
            if server_proc.is_alive():
                server_proc.kill()
                server_proc.join(timeout=1)
            server_proc = None

        if game_outcome == "QUIT":
            app_running = False
        # DISCONNECT and VICTORY/DEFEAT fall through → back to menu loop

    if server_proc is not None and server_proc.is_alive():
        server_proc.terminate()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()