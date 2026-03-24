import pygame
import os
from .button import Button

class Menu():
    CHAMPIONS = ["Bunnyon", "Freud", "Pretresse", "SuperComputer", "Wanderer"]
    
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.selected = None
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
        self.font = pygame.font.SysFont("Arial", 24)
        self.portraits = {}
        for name in self.CHAMPIONS:
            path = os.path.join("Fiche_perso", f"{name}.png")
            img = pygame.image.load(path).convert_alpha()
            self.portraits[name] = pygame.transform.scale(img, (150, 200))
        sw = screen.get_width()
        sh = screen.get_height()
        self.play_button = Button (sw//2 - 100, sh - 120, 200, 60, "JOUER", color=(200, 50, 50), hover_color=(230, 80, 80))
    
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
        return None
    
    def draw(self):
        self.screen.fill((20, 20, 30))
        title = self.font_title.render("CHOISISSEZ VOTRE PERSONNAGE", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(centerx=self.screen.get_width()//2, y=40))
        for i, name in enumerate(self.CHAMPIONS):
            rect = self._portrait_rect(i)
            if self.selected == name:
                pygame.draw.rect(self.screen, (200, 50, 50), rect.inflate(10, 10), border_radius=8)
            self.screen.blit(self.portraits[name], rect)
            label = self.font.render(name, True, (255, 255, 255))
            self.screen.blit(label, label.get_rect(centerx=rect.centerx, y=rect.bottom + 8))
        self.play_button.draw(self.screen)
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