import pygame
import os
from .button import Button

BACKGROUND    = (8, 8, 20)
ACCENT_CYAN   = (80, 220, 255)
ACCENT_PURPLE = (180, 80, 255)
BUTTON_COLOR  = (40, 40, 80)
BUTTON_HOVER  = (80, 80, 160)
BUTTON_PLAY        = (100, 40, 180)
BUTTON_PLAY_HOVER  = (140, 60, 220)
TEXT_COLOR    = (220, 220, 255)
WARNING_COLOR = (255, 80, 180)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "..", "assets", "font", "Orbitron-Bold.ttf")

class Menu():
    CHAMPIONS = ["Pretresse", "SuperComputer"]
    
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.selected = None
        self.show_warning = False
        self.font_title = pygame.font.Font(FONT_PATH, 46)
        self.font       = pygame.font.Font(FONT_PATH, 22)
        self.font_small = pygame.font.Font(FONT_PATH, 20)
        self.portraits = {}
        for name in self.CHAMPIONS:
            path = os.path.join("Fiche_perso", f"{name}.png")
            img = pygame.image.load(path).convert_alpha()
            self.portraits[name] = pygame.transform.scale(img, (150, 200))
        sw = screen.get_width()
        sh = screen.get_height()
        self.play_button = Button (sw//2 - 100, sh - 120, 200, 60, "JOUER", color=BUTTON_PLAY, hover_color=BUTTON_PLAY_HOVER)
    
    def handle_event(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, name in enumerate(self.CHAMPIONS):
                    rect = self._portrait_rect(i)
                    if rect.collidepoint(event.pos):
                        self.selected = name
            if self.play_button.is_clicked(event):
                if self.selected:
                    return self.selected
                else:
                    self.show_warning = True
        return None
    
    def draw_background(self):
        for y in range(self.screen.get_height()):
            ratio = y / self.screen.get_height()
            r = int(8 + 20 * ratio)
            g = int(8 + 15 * ratio)
            b = (20 + 60 * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.screen.get_width(), y))
    
    def draw(self):
        self.draw_background()
        title = self.font_title.render("CHOISISSEZ VOTRE PERSONNAGE", True, ACCENT_CYAN)
        self.screen.blit(title, title.get_rect(centerx=self.screen.get_width()//2, y=40))
        sw = self.screen.get_width()
        pygame.draw.line(self.screen, ACCENT_PURPLE, (sw//4, 110), (3*sw//4, 110), 2)
        for i, name in enumerate(self.CHAMPIONS):
            rect = self._portrait_rect(i)
            if self.selected == name:
                bg_rect = rect.inflate(10, 10)
                bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                bg_surface.fill((80, 220, 255, 60))
                pygame.draw.rect(self.screen, ACCENT_CYAN, bg_rect, 2, border_radius=8)
            self.screen.blit(self.portraits[name], rect)
            color = ACCENT_CYAN if self.selected == name else TEXT_COLOR
            label = self.font.render(name, True, color)
            self.screen.blit(label, label.get_rect(centerx=rect.centerx, y=rect.bottom + 10))
        self.play_button.color = BUTTON_PLAY if self.selected else BUTTON_COLOR
        self.play_button.hover_color = BUTTON_PLAY_HOVER if self.selected else BUTTON_HOVER
        self.play_button.draw(self.screen)
        if self.show_warning:
            warning = self.font.render("Veuillez séléctionner un personnage !", True, WARNING_COLOR)
            self.screen.blit(warning, warning.get_rect(centerx=self.screen.get_width()//2, y=self.screen.get_height() - 207))
        pygame.display.flip()
    
    def _portrait_rect(self, index):
        sw = self.screen.get_width()
        total = len(self.CHAMPIONS)
        spacing = sw // (total+1)
        x = spacing * (index + 1) - 75
        y = self.screen.get_height()//2 - 150
        return pygame.Rect(x, y, 150, 200)
    
    def run(self):
        while self.running:
            result = self.handle_event()
            if result:
                return result
            self.draw()
        return None