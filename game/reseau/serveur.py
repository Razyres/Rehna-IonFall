import socket
import threading
import pickle
import time

SERVER_IP = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 65536

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server.bind((SERVER_IP, PORT))
except socket.error as e:
    print(f"Server initialization binding error: {e}")

server.listen(2)
print("Authoritative Server standing by. Awaiting remote client handshakes...")

state_lock = threading.Lock()
players_ready = 0

game_state = {
    "player_0": {"x": 120.0, "y": 1430.0, "hp": 100, "sprite_prefix": ""},
    "player_1": {"x": 1459.0, "y": 109.0, "hp": 100, "sprite_prefix": ""},
    "projectiles": [],
    "minions": [],
    "ready": False
}

def threaded_client(conn, player_id):
    global game_state, players_ready

    conn.send(str(player_id).encode())

    try:
        client_prefix = conn.recv(2048).decode()
        with state_lock:
            game_state[f"player_{player_id}"]["sprite_prefix"] = client_prefix
            players_ready += 1
            if players_ready >= 2:
                game_state["ready"] = True
        print(f"Player {player_id} ready ({client_prefix}). {players_ready}/2 connected.")
    except Exception as e:
        print(f"Handshake error with player {player_id}: {e}")
        conn.close()
        return

    server_clock_delay = 1.0 / 60.0

    p_key = f"player_{player_id}"
    while True:
        start_time = time.time()
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print(f"Client disconnected: Player {player_id}")
                break

            inputs = pickle.loads(data)

            with state_lock:
                if game_state["ready"]:
                    speed = 5.0
                    if inputs.get("z"):
                        game_state[p_key]["y"] -= speed
                    if inputs.get("s"):
                        game_state[p_key]["y"] += speed
                    if inputs.get("q"):
                        game_state[p_key]["x"] -= speed
                    if inputs.get("d"):
                        game_state[p_key]["x"] += speed
                serialized = pickle.dumps(game_state)

            conn.sendall(serialized)
        except Exception as e:
            print(f"Error servicing player {player_id}: {e}")
            break

        elapsed = time.time() - start_time
        if elapsed < server_clock_delay:
            time.sleep(server_clock_delay - elapsed)

    conn.close()


def main():
    current_player_count = 0
    while True:
        try:
            conn, addr = server.accept()
            if current_player_count >= 2:
                conn.close()
                continue
            print(f"Connection from {addr}")
            t = threading.Thread(target=threaded_client, args=(conn, current_player_count))
            t.daemon = True
            t.start()
            current_player_count += 1
        except KeyboardInterrupt:
            print("\nShutting down server.")
            break


if __name__ == "__main__":
    main()
