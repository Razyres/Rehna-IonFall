import pygame
import os

ACCENT_CYAN   = (80, 220, 255)
ACCENT_PURPLE = (180, 80, 255)
VICTORY_COLOR = (80, 220, 255)
DEFEAT_COLOR  = (255, 80, 180)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
FONT_PATH = os.path.join(PROJECT_ROOT, "assets", "font", "Orbitron-Bold.ttf")

class EndScreen():
    def __init__(self, screen, result_text):
        self.screen = screen
        self.result_text = result_text
        self.font_title = pygame.font.Font(FONT_PATH, 64)
        self.font_button = pygame.font.Font(FONT_PATH, 22)
        self.main_color = VICTORY_COLOR if result_text == "VICTORY" else DEFEAT_COLOR
    
    def draw(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((8, 8, 20, 180))
        self.screen.blit(overlay, (0, 0))
        title_surf = self.font_title.render(self.result_text, True, self.main_color)
        title_rect = title_surf.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
        glow_surf = self.font_title.render(self.result_text, True, self.main_color)
        glow_surf.set_alpha(100)
        self.screen.blit(glow_surf, title_rect.move(4, 4))
        self.screen.blit(title_surf, title_rect)
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        pygame.draw.line(self.screen, ACCENT_PURPLE, (sw//3, sh//2 + 20), (2*sw//3, sh//2 + 20), 2)
        prompt_surf = self.font_button.render("APPUYEZ SUR ECHAP POUR QUITTER OU APPUYEZ SUR ESPACE POUR RETOURNER AU MENU", True, (220, 220, 255))
        prompt_rect = prompt_surf.get_rect(center=(sw//2, sh//2 + 80))
        self.screen.blit(prompt_surf, prompt_rect)
        pygame.display.flip()
    
    def run(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "QUIT"
                    if event.key == pygame.K_SPACE:
                        return "MENU"
        return "QUIT"