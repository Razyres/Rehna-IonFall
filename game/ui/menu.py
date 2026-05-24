import pygame
from typing import List, Dict, Optional, Tuple
from .button import Button
from game.utils import resource_path

BACKGROUND: Tuple[int, int, int] = (8, 8, 20)
ACCENT_CYAN: Tuple[int, int, int] = (80, 220, 255)
ACCENT_PURPLE: Tuple[int, int, int] = (180, 80, 255)
BUTTON_COLOR: Tuple[int, int, int] = (40, 40, 80)
BUTTON_HOVER: Tuple[int, int, int] = (80, 80, 160)
BUTTON_PLAY: Tuple[int, int, int] = (100, 40, 180)
BUTTON_PLAY_HOVER: Tuple[int, int, int] = (140, 60, 220)
TEXT_COLOR: Tuple[int, int, int] = (220, 220, 255)
WARNING_COLOR: Tuple[int, int, int] = (255, 80, 180)

FONT_PATH: str = resource_path("game/assets/font/Orbitron-Bold.ttf")

class Menu:
    """
    Manages the character selection screen and initialization parameters before match starts.
    """
    CHAMPIONS: List[str] = ["Freud", "Pretresse", "Ordinateur", "Vagabon"]
    
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
            path = resource_path(f"sprite/HEAD_{name}.png")
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

    def _draw_ip_input(self, ip_text: str) -> None:
        self.screen.fill(BACKGROUND)
        sw, sh = self.screen.get_width(), self.screen.get_height()

        title = self.font_title.render("CONNEXION AU SERVEUR", True, ACCENT_PURPLE)
        self.screen.blit(title, title.get_rect(centerx=sw // 2, y=80))

        label = self.font.render("IP du serveur :", True, TEXT_COLOR)
        self.screen.blit(label, label.get_rect(centerx=sw // 2, y=sh // 2 - 70))

        box_rect = pygame.Rect(sw // 2 - 220, sh // 2 - 30, 440, 55)
        pygame.draw.rect(self.screen, BUTTON_COLOR, box_rect, border_radius=8)
        pygame.draw.rect(self.screen, ACCENT_CYAN, box_rect, 2, border_radius=8)
        ip_surf = self.font.render(ip_text + "|", True, ACCENT_CYAN)
        self.screen.blit(ip_surf, ip_surf.get_rect(center=box_rect.center))

        hint = self.font_small.render("ENTREE pour connecter   |   ECHAP pour retour", True, TEXT_COLOR)
        self.screen.blit(hint, hint.get_rect(centerx=sw // 2, y=sh // 2 + 60))
        pygame.display.flip()

    def _run_ip_input(self) -> Optional[str]:
        ip_text = "127.0.0.1"
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return ip_text if ip_text else "127.0.0.1"
                    elif event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    elif event.unicode in "0123456789.":
                        ip_text += event.unicode
            self._draw_ip_input(ip_text)

    def _draw_mode_select(self, host_btn: Button, join_btn: Button) -> None:
        self.screen.fill(BACKGROUND)
        sw, sh = self.screen.get_width(), self.screen.get_height()

        title = self.font_title.render("MODE DE JEU", True, ACCENT_PURPLE)
        self.screen.blit(title, title.get_rect(centerx=sw // 2, y=80))

        sub_host = self.font_small.render("Cree et heberge une partie sur ce PC", True, TEXT_COLOR)
        self.screen.blit(sub_host, sub_host.get_rect(centerx=sw // 2, y=sh // 2 - 100))

        host_btn.draw(self.screen)

        sub_join = self.font_small.render("Rejoindre une partie existante (entrer l'IP)", True, TEXT_COLOR)
        self.screen.blit(sub_join, sub_join.get_rect(centerx=sw // 2, y=sh // 2 + 10))

        join_btn.draw(self.screen)

        hint = self.font_small.render("ECHAP pour retour", True, (120, 120, 160))
        self.screen.blit(hint, hint.get_rect(centerx=sw // 2, y=sh - 100))

        pygame.display.flip()

    def _run_mode_select(self) -> Optional[str]:
        """Returns 'host', 'join', or None (back to champion select)."""
        sw, sh = self.screen.get_width(), self.screen.get_height()
        host_btn = Button(sw // 2 - 160, sh // 2 - 70, 320, 55, "HEBERGER", BUTTON_PLAY, BUTTON_PLAY_HOVER)
        join_btn = Button(sw // 2 - 160, sh // 2 + 55, 320, 55, "REJOINDRE", BUTTON_COLOR, BUTTON_HOVER)
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if host_btn.is_clicked(event):
                        return "host"
                    if join_btn.is_clicked(event):
                        return "join"
            self._draw_mode_select(host_btn, join_btn)

    def run(self) -> Tuple[Optional[str], str, bool]:
        while True:
            # Phase 1: champion selection
            self.running = True
            self.selected = None
            self.show_warning = False
            while self.running:
                self.clock.tick(60)
                self.handle_events()
                self.draw()
            if not self.selected:
                return None, "", False
            # Phase 2: mode selection — ESC goes back to champion selection
            mode = self._run_mode_select()
            if mode is None:
                continue
            if mode == "host":
                return self.selected, "127.0.0.1", True
            # Phase 3: IP input — ESC goes back to mode selection
            ip = self._run_ip_input()
            if ip is not None:
                return self.selected, ip, False