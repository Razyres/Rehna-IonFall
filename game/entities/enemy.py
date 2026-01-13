from .entity import Entity

class Enemy(Entity):
    def __init__(self, x, y, width, height, sprite, damage):
        super().__init__(x, y, width, height, sprite)
        self.damage = damage
        
    def update(self, event):
        pass
    
    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y)) 