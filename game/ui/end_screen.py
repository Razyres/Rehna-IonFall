import pygame
import os
from typing import Tuple, Literal

# Global layout color palette configuration tokens
ACCENT_CYAN: Tuple[int, int, int] = (80, 220, 255)
ACCENT_PURPLE: Tuple[int, int, int] = (180, 80, 255)
VICTORY_COLOR: Tuple[int, int, int] = (80, 220, 255)
DEFEAT_COLOR: Tuple[int, int, int] = (255, 80, 180)

CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT: str = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
FONT_PATH: str = os.path.join(PROJECT_ROOT, "assets", "font", "Orbitron-Bold.ttf")

class EndScreen:
    """
    Manages client terminal session interfaces upon match termination sequence triggers.
    
    Renders high-contrast overlay text surfaces dislaying match outcomes
    and handles state redirection inputs back to primary menu components.
    """
    
    def __init__(self, screen: pygame.Surface, result_text: str):
        """
        Initializes a new EndScreen UI workflow layer.

        Args:
            screen (pygame.Surface): Display target workspace to execute blits upon.
            result_text (str): Evaluation identifier matching global conditions ("VICTORY" or "DEFEAT")
        """
        self.screen: pygame.Surface = screen
        self.result_text: str = result_text
        # Robust font compilation layer with safe standard sysem fallback
        try:
            self.font_title: pygame.font.Font = pygame.font.Font(FONT_PATH, 64)
            self.font_button: pygame.font.Font = pygame.font.Font(FONT_PATH, 22)
        except FileNotFoundError:
            print(f"Warning: Custom UI asset asset not found at {FONT_PATH}. Falling back to system fonts.")
            self.font_title = pygame.font.SysFont("sans-serif", 64, bold=True)
            self.font_button = pygame.font.SysFont("sans-serif", 22)
        self.main_color: Tuple[int, int, int] = VICTORY_COLOR if result_text == "VICTORY" else DEFEAT_COLOR
        self.clock: pygame.time.Clock = pygame.time.Clock()
    
    def draw(self) -> None:
        """
        Create spatial frames to blit game result layouts and stylized prompt labels.
        """
        # Create an alpha-transparent layer surface overlay to dim the underlying world map
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((8, 8, 20, 180)) # Semi-transparent dark cosmic blue
        self.screen.blit(overlay, (0, 0))
        # Generate the Title text surface asset metrics
        title_surf = self.font_title.render(self.result_text, True,self.main_color)
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))
        # Generate and offset the structural text shadow drop (glow effect matrix layout)
        glow_surf = self.font_title.render(self.result_text, True, self.main_color)
        glow_surf.set_alpha(100)
        self.screen.blit(glow_surf, title_rect.move(4, 4))
        self.screen.blit(title_surf, title_rect)
        # Draw structural layout separator lines
        sw = self.screen.get_width()
        sh = self.screen.get_height()
        pygame.draw.line(self.screen, ACCENT_PURPLE, (sw // 3, sh // 2 + 20), (2 * sw // 3, sh // 2 + 20), 2)
        # Render interaction operational user directions
        prompt_text = "APPUYEZ SUR ECHAP POUR QUITTER OU SUR ESPACE POUR RETOURNER AU MENU"
        prompt_surf = self.font_button.render(prompt_text, True, (220, 220, 255))
        prompt_rect = prompt_surf.get_rect(center=(sw // 2, sh // 2 + 80))
        self.screen.blit(prompt_surf, prompt_rect)
        pygame.display.flip()
    
    def run(self) -> Literal["QUIT", "MENU"]:
        """
        Runs the interactive event loop for the end match menu.
        
        Caps the frame evaluations to block excessive hardware CPU thread workloads.

        Returns:
            Literal["QUIT", "MENU"]: Next execution block flag identifier instruction.
        """
        waiting: bool = True
        while waiting:
            # Cap execution rate to a clean 30 FPS to reduce CPU utilization down to ~0%
            self.clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "QUIT"
                    if event.key == pygame.K_SPACE:
                        return "MENU"
        return "QUIT"