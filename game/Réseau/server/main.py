import socket
import threading
import json
from protocols import Protocols
from room import Room
import time

class Server:
    def __init__(self, host="127.0.0.1", port=55555):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        
        self.client_names = {}
        self.opponent = {}
        self.rooms = {}
        self.waiting_for_pair = None
        
    def handle_connect(self, client):
        while True:
            self.send(Protocols.Response.NICKNAME, None, client)
            message = json.loads(client.recv(1024).decode("ascii"))
            r_type = message.get("type")
            data = message.get("data")
            
            if r_type == Protocols.Request.NICKNAME:
                self.client_names[client] = data
            else:
                continue
            
            if not self.waiting_for_pair:
                self.waiting_for_pair = client
                print("waiting for a room")
            else:
                self.create_room(client)
            
            break
    
    def create_room(self, client):
        print("Creating room.")
        room = Room(client, self.waiting_for_pair)
        self.opponent[client] = self.waiting_for_pair
        self.opponent[self.waiting_for_pair] = client

        self.send(Protocols.Response.OPPONENT, self.get_client_data(client), self.waiting_for_pair)
        self.send(Protocols.Response.OPPONENT, self.get_client_data(self.waiting_for_pair), client)

        self.rooms[client] = room
        self.rooms[self.waiting_for_pair] = room
        self.waiting_for_pair = None
    
    def wait_for_room(self, client):
        while True:
            room = self.rooms.get(client)
            opponent = self.opponent.get(client)

            if room and opponent:
                self.send(Protocols.Response.QUESTIONS, room.questions, client)
                time.sleep(1)
                self.send(Protocols.Response.START, None, client)
                break
            
    def handle(self, client):
        self.handle_connect(client)
        self.wait_for_room(client)
    
        while True :
            try:
                data = client.recv(1024).decode("ascii")
                if not data:
                    break
                message = json.loads(data)
                self.handle_receive(message, client)
            except:
                break
        
        self.send_to_opponent(Protocols.Response.OPPONENT_LEFT, None, client)
        self.disconnect(client)
        
    def disconnect(self, client):
        pass
    
    def handle_receive(self, message, client):
        pass
    
    def send(self, r_type, data, client):
        pass
    
    def send_to_player(self, r_type, data, client):
        pass
    
    def receive(self):
        while True:
            client, address = self.server.accept()
            print(f"Connected with {str(address)}")
            thread = threading.Thread(target=self.handle, args=(client,))
            thread.start()
    
    
        