import socket
import threading
import pickle
import time

SERVER_IP = "0.0.0.0"
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind((SERVER_IP, PORT))
except socket.error as e:
    print(str(e))

server.listen(2)
print("Serveur initialisé. En attente de joueurs...")

game_state = {
        "player_0" : {"x" : 120, "y" : 1430, "hp" : 100, "sprite_prefix" : ""},
        "player_1" : {"x" : 1232, "y" : 220, "hp" : 100, "sprite_prefix" : ""},
        "projectiles" : [],
        "minions" : []
}

def threaded_client(conn, player_id):
    """Gère la communication avec un joueur spécifique"""
    global game_state
    conn.send(str.encode(str(player_id)))
    while True:
        try :
            data = conn.recv(2048)
            if not data:
                print(f"Joueur {player_id} déconnecté.")
                break
            inputs = pickle.load(data)
            p_key = f"player_{player_id}"
            speed = 5
            if inputs.get("z"):
                game_state[p_key]["y"] -= speed
            if inputs.get("s"):
                game_state[p_key]["y"] += speed
            if inputs.get("q"):
                game_state[p_key]["x"] -= speed
            if inputs.get("d"):
                game_state[p_key]["x"] += speed
            # TODO : Verifier les collisions avec la map
            conn.sendall(pickle.dumps(game_state))
        except Exception as e:
            print(f"Erreur avec le joueur {player_id} : {e}")
            break
    print(f"Connection fermée pour le joueur {player_id}")
    conn.close()
player_count = 0
while player_count < 2:
    conn, addr = server.accept()
    print(f"Joueur {player_count} connecté depuis : {addr}")
    threading.Thread(target=threaded_client, args=(conn, player_count)).start()
    player_count += 1
