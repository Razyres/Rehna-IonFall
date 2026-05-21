import socket
import pickle
from typing import Optional, Any, Tuple

class Network:
    """
    Manages low-level client-side socket TCP connectivity and data serialization.
    
    Acts as the network interface engine connecting the local client runtime
    to the authoritative game server instance using object streaming protocols.
    """
    
    BUFFER_SIZE: int = 65536  # 64KB — suffisant pour un game_state pickle complet
    
    def __init__(self, sprite_prefix: str = "Vagabon"):
        """
        Initializes a new network connection bridge interface.

        Args:
            sprite_prefix (str): The champion sprite prefix to send to the server during handshake.
        """
        self.client: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server: str = "127.0.0.1"
        self.port: int = 5555
        self.addr: Tuple[str, int] = (self.server, self.port)
        self.sprite_prefix: str = sprite_prefix
        # FIX: le handshake envoie maintenant le sprite_prefix après avoir reçu l'ID
        self.player_id: Optional[int] = self.connect()
    
    def connect(self) -> Optional[int]:
        """
        Establishes an active handshaking connection to the targeted server address.
        Sends the sprite_prefix to the server after receiving the player ID.

        Returns:
            Optional[int]: The parsed unique network identifier token or None if connection fails.
        """
        try:
            self.client.connect(self.addr)
            # Receive our assigned player ID
            response = self.client.recv(2048).decode()
            player_id = int(response)
            # FIX: envoyer le sprite_prefix au serveur (étape manquante côté client)
            self.client.send(self.sprite_prefix.encode())
            return player_id
        except (socket.error, ValueError, ConnectionRefusedError) as e:
            print(f"Network Connection Layer Error: Unable to resolve socket route to remote node: {e}")
            return None
    
    def send(self, data: Any) -> Optional[Any]:
        """
        Serializes and dispatches local updates while intercepting synchronous state responses.

        Args:
            data (Any): Structural python payload dictionary containing state attributes or action vectors.

        Returns:
            Optional[Any]: Deserialized world matrix context payload from the server, or None if packet loss triggers.
        """
        try:
            self.client.send(pickle.dumps(data))
            # FIX: buffer agrandi pour recevoir les gros paquets game_state sans troncature
            raw_response = self.client.recv(self.BUFFER_SIZE)
            if not raw_response:
                return None
            return pickle.loads(raw_response)
        except (socket.error, pickle.PickleError) as e:
            print(f"Network Synchronizer Pipeline Error: Data package transfer failed: {e}")
            return None

