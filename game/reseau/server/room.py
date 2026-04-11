class Room:
    def __init__(self, client1, client2):
        self.client1  = client1   # joueur 1 (bleu)
        self.client2  = client2   # joueur 2 (rouge)
        self.finished = False
        self.winner   = None      # 1 ou 2
