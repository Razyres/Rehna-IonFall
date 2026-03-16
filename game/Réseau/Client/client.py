import socket
import threading
import json
from protocols import Protocols


class Client:
        def __init__(self, host="127.0.0.1", port=55555):
            self.nickname = None
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((host, port))

            self.closed = False
            self.started = False
            self.opponent_name = None
            self.winner = None
        
        def start(self):
            receive_thread = threading.Thread(target=self.receive)
            receive_thread.start()
        
        def send(self, request, message):
            data = {"type": request, "data": message}
            self.server.send(json.dumps(data).encode("ascii"))
        
        def receive(self):
            while not self.closed:
                try:
                    data = self.client.recv(1024).decode("ascii")
                    message = json.loads(data)
                    self.handle_response(message)
                except:
                    break  
          
        def close(self):
            self.closed = True
            self.server.close()
        
        def handle_response(self, response):
            r_type = response.get("type")
            data = response.get("data")
            
            if r_type == Protocols.Response.OPPONENT:
                self.opponent_name = data
            elif r_type == Protocols.Response.START:
                self.started = True
            elif r_type == Protocols.Response.WINNER:
                self.winner = data
                self.close()
            elif r_type == Protocols.Response.OPPONENT_LEFT:
                self.close()
