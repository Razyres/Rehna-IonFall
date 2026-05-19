import pygame
import os
from typing import Tuple

class Button:
    """
    Represents a generic, interactive user interface button component.
    
    Handles mouse hover state highlights, text rendering, and standard 
    bounding box click intersection queries.
    """
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                color: Tuple[int, int, int] = (70, 70, 70), 
                hover_color: Tuple[int, int, int] = (100, 100, 100)):
        """
        Initializes a new UI Button instance.
        """
        self.rect: pygame.Rect = pygame.Rect(x, y, width, height)
        self.text: str = text
        self.color: Tuple[int, int, int] = color
        self.hover_color: Tuple[int, int, int] = hover_color
        
        # Safe structural font loading
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.abspath(os.path.join(current_dir, "..", "assets", "font", "Orbitron-Bold.ttf"))
        
        try:
            self.font: pygame.font.Font = pygame.font.Font(font_path, 22)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("sans-serif", 22, bold=True)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Renders the button geometry and aligned text label to the screen surface.
        """
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """
        Verifies if a specific mouse down event interacts with the button area.
        """
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)