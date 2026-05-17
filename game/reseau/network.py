import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.player_id = self.connect()
    
    def connect(self):
        try:
            self.client.connect(self.addr)
            return int(self.client.recv(2048).decode())
        except Exception as e:
            print(f"Impossible de se connecter au serveur : {e}")
            return None

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.get_packet_or_recv_here(2048))
        except socket.error as e:
            print(e)
            return None

