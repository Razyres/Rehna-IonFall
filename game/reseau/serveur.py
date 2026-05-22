import socket
import threading
import pickle
import time

SERVER_IP = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 65536  # FIX: 64KB au lieu de 2048 — évite la troncature des game_state pickle

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind((SERVER_IP, PORT))
except socket.error as e:
    print(f"Server initialization binding error: {e}")

server.listen(2)
print("Authoritative Server standing by. Awaiting remote client handshakes...")

# Central Authoritative Registry State Database
game_state = {
    "player_0": {"x": 120.0, "y": 1430.0, "hp": 100, "sprite_prefix": ""},
    "player_1": {"x": 1459.0, "y": 109.0, "hp": 100, "sprite_prefix": ""},
    "projectiles": [],
    "minions": []
}

def threaded_client(conn, player_id):
    global game_state
    
    # Send player ID assignment token
    conn.send(str(player_id).encode())
    
    # FIX: recv du sprite_prefix — le client envoie maintenant ce message
    try:
        client_prefix = conn.recv(2048).decode()
        p_key = f"player_{player_id}"
        game_state[p_key]["sprite_prefix"] = client_prefix
        print(f"Player {player_id} selected champion sprite prefix: {client_prefix}")
    except Exception as e:
        print(f"Handshake error with player {player_id}: {e}")
        conn.close()
        return

    server_clock_delay = 1.0 / 60.0
    
    while True:
        start_time = time.time()
        try:
            # FIX: buffer agrandi ici aussi pour les inputs (futurs messages plus longs)
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print(f"Client disconnected gracefully: Session index [Player {player_id}]")
                break
                
            inputs = pickle.loads(data)
            speed = 5.0
            
            if inputs.get("z"):
                game_state[p_key]["y"] -= speed
            if inputs.get("s"):
                game_state[p_key]["y"] += speed
            if inputs.get("q"):
                game_state[p_key]["x"] -= speed
            if inputs.get("d"):
                game_state[p_key]["x"] += speed
                
            # FIX: buffer agrandi pour envoyer le game_state complet sans troncature
            conn.sendall(pickle.dumps(game_state))
        except Exception as e:
            print(f"Critical exception triggered servicing pipeline [Player {player_id}]: {e}")
            break
            
        execution_duration = time.time() - start_time
        if execution_duration < server_clock_delay:
            time.sleep(server_clock_delay - execution_duration)
            
    conn.close()

def main():
    current_player_count = 0
    while True:
        try:
            conn, addr = server.accept()
            print(f"Established remote communication link with routing interface target: {addr}")
            
            client_thread = threading.Thread(target=threaded_client, args=(conn, current_player_count))
            client_thread.daemon = True
            client_thread.start()
            
            current_player_count += 1
        except KeyboardInterrupt:
            print("\nShutting down server nodes manually.")
            break

if __name__ == "__main__":
    main()
