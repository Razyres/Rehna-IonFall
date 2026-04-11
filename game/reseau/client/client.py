import socket
import threading
import json
import queue
from protocols import Protocols


class Client:
    def __init__(self, host="127.0.0.1", port=55555):
        self.nickname = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

        self.closed        = False
        self.started       = False
        self.opponent_name = None
        self.winner        = None
        self.player_id     = None  # 1 = équipe bleue (bas), 2 = équipe rouge (haut)

        # File thread-safe : le thread réseau y dépose les messages de jeu,
        # la boucle de jeu les consomme via get_messages().
        self.message_queue = queue.Queue()

    def start(self):
        receive_thread = threading.Thread(target=self.receive, daemon=True)
        receive_thread.start()

    def send(self, request, message):
        data = {"type": request, "data": message}
        try:
            self.server.send(json.dumps(data).encode("ascii"))
        except Exception:
            pass

    def receive(self):
        while not self.closed:
            try:
                # BUG FIX : était self.client.recv (AttributeError)
                data = self.server.recv(4096).decode("ascii")
                message = json.loads(data)
                self.handle_response(message)
            except Exception:
                break

    def close(self):
        self.closed = True
        self.server.close()

    def handle_response(self, response):
        r_type = response.get("type")
        data   = response.get("data")

        if r_type == Protocols.Response.OPPONENT:
            self.opponent_name = data

        elif r_type == Protocols.Response.START:
            self.started = True

        elif r_type == Protocols.Response.WINNER:
            self.winner = data
            self.close()

        elif r_type == Protocols.Response.OPPONENT_LEFT:
            self.close()

        elif r_type == Protocols.Response.PLAYER_ID:
            self.player_id = data

        # Messages de jeu → file d'attente (consommés par la boucle pygame)
        elif r_type in (
            Protocols.Response.OPPONENT_UPDATE,
            Protocols.Response.OPPONENT_PROJECTILE,
            Protocols.Response.NEXUS_DAMAGE,
        ):
            self.message_queue.put(response)

    def get_messages(self):
        """Vide la file et retourne tous les messages en attente."""
        messages = []
        while not self.message_queue.empty():
            try:
                messages.append(self.message_queue.get_nowait())
            except queue.Empty:
                break
        return messages
