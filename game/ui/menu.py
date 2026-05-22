import pygame
import os
from typing import List, Dict, Optional, Tuple
from .button import Button

BACKGROUND: Tuple[int, int, int] = (8, 8, 20)
ACCENT_CYAN: Tuple[int, int, int] = (80, 220, 255)
ACCENT_PURPLE: Tuple[int, int, int] = (180, 80, 255)
BUTTON_COLOR: Tuple[int, int, int] = (40, 40, 80)
BUTTON_HOVER: Tuple[int, int, int] = (80, 80, 160)
BUTTON_PLAY: Tuple[int, int, int] = (100, 40, 180)
BUTTON_PLAY_HOVER: Tuple[int, int, int] = (140, 60, 220)
TEXT_COLOR: Tuple[int, int, int] = (220, 220, 255)
WARNING_COLOR: Tuple[int, int, int] = (255, 80, 180)

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
FONT_PATH: str = os.path.abspath(os.path.join(BASE_DIR, "..", "assets", "font", "Orbitron-Bold.ttf"))

class Menu:
    """
    Manages the character selection screen and initialization parameters before match starts.
    """
    CHAMPIONS: List[str] = ["Freud", "Ordinateur", "Vagabon"]
    
    def __init__(self, screen: pygame.Surface):
        self.screen: pygame.Surface = screen
        self.running: bool = True
        self.selected: Optional[str] = None
        self.show_warning: bool = False
        self.clock: pygame.time.Clock = pygame.time.Clock()
        
        try:
            self.font_title: pygame.font.Font = pygame.font.Font(FONT_PATH, 46)
            self.font: pygame.font.Font = pygame.font.Font(FONT_PATH, 22)
            self.font_small: pygame.font.Font = pygame.font.Font(FONT_PATH, 20)
        except FileNotFoundError:
            self.font_title = pygame.font.SysFont("sans-serif", 46, bold=True)
            self.font = pygame.font.SysFont("sans-serif", 22)
            self.font_small = pygame.font.SysFont("sans-serif", 20)
            
        self.portraits: Dict[str, pygame.Surface] = {}
        
        # Load character visual items
        for name in self.CHAMPIONS:
            path = os.path.join("sprite", f"HEAD_{name}.png")
            try:
                img = pygame.image.load(path).convert_alpha()
                self.portraits[name] = pygame.transform.scale(img, (120, 120))
            except pygame.error:
                # Build fallback placeholder surface box
                fallback = pygame.Surface((120, 120))
                fallback.fill((40, 40, 60))
                self.portraits[name] = fallback
                
        # Instantiating Play Action button
        sw, sh = screen.get_width(), screen.get_height()
        self.play_button: Button = Button(sw // 2 - 100, sh - 150, 200, 50, "LANCER")

    def _portrait_rect(self, index: int) -> pygame.Rect:
        sw = self.screen.get_width()
        total = len(self.CHAMPIONS)
        spacing = sw // (total + 1)
        x = spacing * (index + 1) - 60
        y = self.screen.get_height() // 2 - 80
        return pygame.Rect(x, y, 120, 120)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.selected = None
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.selected = None
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Evaluate interface items selection hit boxes
                for i, name in enumerate(self.CHAMPIONS):
                    if self._portrait_rect(i).collidepoint(event.pos):
                        self.selected = name
                        self.show_warning = False
                        
                if self.play_button.is_clicked(event):
                    if self.selected:
                        self.running = False
                    else:
                        self.show_warning = True

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        
        # Draw game identity headers
        title = self.font_title.render("BIENVENUE DANS IONFALL", True, ACCENT_PURPLE)
        self.screen.blit(title, title.get_rect(centerx=self.screen.get_width() // 2, y=80))
        
        # Display available entity cards
        for i, name in enumerate(self.CHAMPIONS):
            rect = self._portrait_rect(i)
            
            if self.selected == name:
                bg_rect = rect.inflate(10, 10)
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                bg_surface.fill((80, 220, 255, 60))
                self.screen.blit(bg_surface, bg_rect.topleft)
                pygame.draw.rect(self.screen, ACCENT_CYAN, bg_rect, 2, border_radius=8)
                
            self.screen.blit(self.portraits[name], rect)
            color = ACCENT_CYAN if self.selected == name else TEXT_COLOR
            label = self.font.render(name, True, color)
            self.screen.blit(label, label.get_rect(centerx=rect.centerx, y=rect.bottom + 10))
            
        self.play_button.color = BUTTON_PLAY if self.selected else BUTTON_COLOR
        self.play_button.hover_color = BUTTON_PLAY_HOVER if self.selected else BUTTON_HOVER
        self.play_button.draw(self.screen)
        
        if self.show_warning:
            warning = self.font.render("Veuillez selectionner un personnage !", True, WARNING_COLOR)
            self.screen.blit(warning, warning.get_rect(centerx=self.screen.get_width() // 2, y=self.screen.get_height() - 220))
            
        pygame.display.flip()

    def run(self) -> Optional[str]:
        while self.running:
            self.clock.tick(60)  # Standard safety framerate lock
            self.handle_events()
            self.draw()
        return self.selected