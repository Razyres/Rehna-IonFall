import socket
import threading
import pickle
import time
import sys

SERVER_IP = "0.0.0.0"
PORT = 5555
BUFFER_SIZE = 65536

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    server.bind((SERVER_IP, PORT))
except socket.error as e:
    print(f"Server initialization binding error: {e}")

server.listen(2)
print("Authoritative Server standing by. Awaiting remote client handshakes...")

state_lock = threading.Lock()
shutdown_event = threading.Event()
players_ready = 0

game_state = {
    "player_0": {"x": 120.0,  "y": 1430.0, "hp": 100, "sprite_prefix": "", "team": "blue"},
    "player_1": {"x": 1232.0, "y": 220.0,  "hp": 100, "sprite_prefix": "", "team": "red"},
    "nexus_r_hp": 1000,
    "nexus_v_hp": 1000,
    "projectiles": [],
    "minions": [],
    "ready": False,
}

MAX_HP = {"player_0": 100, "player_1": 100}


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
        shutdown_event.set()
        return

    server_clock_delay = 1.0 / 60.0
    p_key = f"player_{player_id}"

    while not shutdown_event.is_set():
        start_time = time.time()
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                print(f"Client disconnected: Player {player_id}")
                break

            inputs = pickle.loads(data)

            with state_lock:
                if game_state["ready"]:
                    # Position update
                    if "x" in inputs and "y" in inputs:
                        game_state[p_key]["x"] = inputs["x"]
                        game_state[p_key]["y"] = inputs["y"]

                    # Respawn: reset HP
                    if inputs.get("respawn"):
                        game_state[p_key]["hp"] = MAX_HP.get(p_key, 100)

                    # Heal (self-reported by client)
                    heal = inputs.get("self_heal", 0)
                    if heal > 0:
                        max_hp = inputs.get("self_max_hp", MAX_HP.get(p_key, 100))
                        game_state[p_key]["hp"] = min(max_hp, game_state[p_key]["hp"] + heal)

                    # Hit events (players + nexuses)
                    for hit in inputs.get("hits", []):
                        target = hit.get("target")
                        target_id = hit.get("target_id")
                        dmg = hit.get("damage", 0)
                        if target == "nexus_r":
                            game_state["nexus_r_hp"] = max(0, game_state["nexus_r_hp"] - dmg)
                        elif target == "nexus_v":
                            game_state["nexus_v_hp"] = max(0, game_state["nexus_v_hp"] - dmg)
                        elif target_id is not None:
                            tk = f"player_{target_id}"
                            if tk in game_state:
                                game_state[tk]["hp"] = max(0, game_state[tk]["hp"] - dmg)

                serialized = pickle.dumps(game_state)

            conn.sendall(serialized)

        except Exception as e:
            print(f"Error servicing player {player_id}: {e}")
            break

        elapsed = time.time() - start_time
        if elapsed < server_clock_delay:
            time.sleep(server_clock_delay - elapsed)

    conn.close()
    print(f"Player {player_id} thread exiting. Triggering shutdown.")
    shutdown_event.set()


def main():
    current_player_count = 0
    server.settimeout(1.0)

    while not shutdown_event.is_set():
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
        except socket.timeout:
            pass
        except KeyboardInterrupt:
            print("\nShutting down server (keyboard interrupt).")
            break

    print("Server shutting down.")
    server.close()
    sys.exit(0)


if __name__ == "__main__":
    main()
