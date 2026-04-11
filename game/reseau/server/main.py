import socket
import threading
import json
from protocols import Protocols
from room import Room
import time


class Server:
    def __init__(self, host="127.0.0.1", port=55555):
        self.host   = host
        self.port   = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.client_names    = {}  # socket → pseudo
        self.opponent        = {}  # socket → socket adverse
        self.rooms           = {}  # socket → Room
        self.waiting_for_pair = None

    # ---------------------------------------------------------------- connexion

    def handle_connect(self, client):
        """Demande le pseudo puis place le client dans une room."""
        while True:
            self.send(Protocols.Response.NICKNAME, None, client)
            try:
                message = json.loads(client.recv(1024).decode("ascii"))
            except Exception:
                return

            r_type = message.get("type")
            data   = message.get("data")

            if r_type != Protocols.Request.NICKNAME:
                continue

            self.client_names[client] = data
            print(f"[Server] {data} connecté.")

            if not self.waiting_for_pair:
                self.waiting_for_pair = client
                print(f"[Server] {data} attend un adversaire…")
            else:
                self.create_room(client)
            break

    def get_client_name(self, client):
        return self.client_names.get(client, "Inconnu")

    def create_room(self, client):
        """Associe deux clients, crée la room et assigne les IDs joueur."""
        partner = self.waiting_for_pair
        print(f"[Server] Création de la room : {self.get_client_name(partner)} vs {self.get_client_name(client)}")

        room = Room(partner, client)
        self.opponent[client]  = partner
        self.opponent[partner] = client
        self.rooms[client]     = room
        self.rooms[partner]    = room
        self.waiting_for_pair  = None

        # Notifier chaque joueur du pseudo adverse
        self.send(Protocols.Response.OPPONENT, self.get_client_name(client),  partner)
        self.send(Protocols.Response.OPPONENT, self.get_client_name(partner), client)

        # Assigner les IDs : le premier connecté = joueur 1 (bleu, bas de carte)
        #                     le second          = joueur 2 (rouge, haut de carte)
        self.send(Protocols.Response.PLAYER_ID, 1, partner)
        self.send(Protocols.Response.PLAYER_ID, 2, client)

    def wait_for_room(self, client):
        """Attend que la room soit prête puis envoie START."""
        while True:
            if self.rooms.get(client) and self.opponent.get(client):
                time.sleep(0.5)  # petit délai pour que les deux clients soient prêts
                self.send(Protocols.Response.START, None, client)
                break

    # ----------------------------------------------------------------- boucle

    def handle(self, client):
        self.handle_connect(client)
        self.wait_for_room(client)

        while True:
            try:
                data = client.recv(4096).decode("ascii")
                if not data:
                    break
                message = json.loads(data)
                self.handle_receive(message, client)
            except Exception:
                break

        self.send_to_opponent(Protocols.Response.OPPONENT_LEFT, None, client)
        self.disconnect(client)

    def handle_receive(self, message, client):
        """Redirige les messages de jeu vers l'adversaire (serveur relais)."""
        r_type = message.get("type")

        if r_type == Protocols.Request.PLAYER_UPDATE:
            # Position du joueur → adversaire
            self.send_to_opponent(Protocols.Response.OPPONENT_UPDATE,
                                  message.get("data"), client)

        elif r_type == Protocols.Request.PROJECTILE_FIRED:
            # Projectile tiré → adversaire
            self.send_to_opponent(Protocols.Response.OPPONENT_PROJECTILE,
                                  message.get("data"), client)

        elif r_type == Protocols.Request.NEXUS_HIT:
            # Dégât sur un nexus → adversaire (pour sync des HP)
            self.send_to_opponent(Protocols.Response.NEXUS_DAMAGE,
                                  message.get("data"), client)

    # ---------------------------------------------------------------- helpers

    def disconnect(self, client):
        opponent = self.opponent.get(client)
        for key in (client, opponent):
            self.opponent.pop(key, None)
            self.client_names.pop(key, None)
            self.rooms.pop(key, None)
        try:
            client.close()
        except Exception:
            pass

    def send(self, r_type, data, client):
        message = json.dumps({"type": r_type, "data": data}).encode("ascii")
        try:
            client.send(message)
        except Exception:
            pass

    def send_to_opponent(self, r_type, data, client):
        """Envoie un message à l'adversaire du client donné."""
        opponent = self.opponent.get(client)
        if not opponent:
            return
        self.send(r_type, data, opponent)

    def receive(self):
        print(f"[Server] En écoute sur {self.host}:{self.port}")
        while True:
            client, address = self.server.accept()
            print(f"[Server] Connexion depuis {address}")
            thread = threading.Thread(target=self.handle, args=(client,), daemon=True)
            thread.start()


if __name__ == "__main__":
    server = Server()
    server.receive()
