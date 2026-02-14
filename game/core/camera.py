import pygame


class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        """
        Initialise la caméra
        
        Args:
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran
            map_width: Largeur de la map en pixels
            map_height: Hauteur de la map en pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.x = 0.0
        self.y = 0.0
        self.zoom = 2.0
        self.smoothing = 0.2
    
    def follow(self, target_rect):
        """
        Suit le joueur avec un effet smooth ET respecte les limites de la map
        
        Args:
            target_rect: pygame.Rect de l'entité à suivre
        """
        target_center_x = target_rect.x + target_rect.width / 2.0
        target_center_y = target_rect.y + target_rect.height / 2.0
        visible_width = self.screen_width / self.zoom
        visible_height = self.screen_height / self.zoom
        target_x = target_center_x - visible_width / 2.0
        target_y = target_center_y - visible_height / 2.0
        if visible_width >= self.map_width:
            target_x = -(visible_width - self.map_width) / 2.0
        else:
            max_x = self.map_width - visible_width
            target_x = max(0.0, min(target_x, max_x))
        
        if visible_height >= self.map_height:
            target_y = -(visible_height - self.map_height) / 2.0
        else:
            max_y = self.map_height - visible_height
            target_y = max(0.0, min(target_y, max_y))
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing
    
    def apply(self, entity):
        """
        Retourne la position d'une entité relative à la caméra avec le zoom
        
        Args:
            entity: L'entité (doit avoir x, y)
            
        Returns:
            tuple: (x, y) position à l'écran
        """
        screen_x = (entity.x - self.x) * self.zoom
        screen_y = (entity.y - self.y) * self.zoom
        return screen_x, screen_y
    
    def apply_rect(self, rect):
        """
        Applique le décalage et le zoom à un rectangle
        
        Args:
            rect: pygame.Rect
            
        Returns:
            pygame.Rect: Rectangle ajusté pour l'affichage
        """
        screen_x = (rect.x - self.x) * self.zoom
        screen_y = (rect.y - self.y) * self.zoom
        screen_width = rect.width * self.zoom
        screen_height = rect.height * self.zoom
        return pygame.Rect(screen_x, screen_y, screen_width, screen_height)
    
    def apply_pos(self, x, y):
        """
        Applique le décalage et le zoom à une position
        
        Args:
            x: Coordonnée x dans le monde
            y: Coordonnée y dans le monde
            
        Returns:
            tuple: (x, y) position à l'écran
        """
        screen_x = (x - self.x) * self.zoom
        screen_y = (y - self.y) * self.zoom
        return screen_x, screen_y