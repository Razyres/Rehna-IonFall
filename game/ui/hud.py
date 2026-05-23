import pygame
from typing import Any
from game.utils import resource_path
from game.entities.champion import _XP_TO_NEXT, MAX_LEVEL


class HUD:
    """Renders the in-game overlay: bottom bar (HP + abilities), timer, and K/D."""

    BAR_H    = 110
    ICON_SZ  = 64
    ICON_GAP = 14

    CYAN   = (80, 220, 255)
    PURPLE = (180, 80, 255)
    GREEN  = (60, 220, 80)
    YELLOW = (255, 220, 40)
    RED    = (255, 60, 60)
    TEXT   = (220, 220, 255)
    DIM    = (80, 80, 100)
    ICON_BG = (25, 25, 55)

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sw = screen.get_width()
        self.sh = screen.get_height()
        font_path = resource_path("game/assets/font/Orbitron-Bold.ttf")
        try:
            self.f_timer    = pygame.font.Font(font_path, 30)
            self.f_kda      = pygame.font.Font(font_path, 22)
            self.f_hp       = pygame.font.Font(font_path, 16)
            self.f_key      = pygame.font.Font(font_path, 16)
            self.f_cd       = pygame.font.Font(font_path, 13)
            self.f_name     = pygame.font.Font(font_path, 11)
            self.f_announce = pygame.font.Font(font_path, 46)
        except (FileNotFoundError, OSError):
            self.f_timer    = pygame.font.SysFont("sans-serif", 30, bold=True)
            self.f_kda      = pygame.font.SysFont("sans-serif", 22, bold=True)
            self.f_hp       = pygame.font.SysFont("sans-serif", 16, bold=True)
            self.f_key      = pygame.font.SysFont("sans-serif", 16, bold=True)
            self.f_cd       = pygame.font.SysFont("sans-serif", 13)
            self.f_name     = pygame.font.SysFont("sans-serif", 11)
            self.f_announce = pygame.font.SysFont("sans-serif", 46, bold=True)

        # Kill announcements: list of (text, color, expiry_ms)
        self._announcements: list = []

    def push_kill(self, total_kills: int) -> None:
        """Queue a kill announcement banner. Call whenever the local kill counter increments."""
        now = pygame.time.get_ticks()
        if total_kills == 1:
            text, color = "FIRST BLOOD !", (255, 70, 70)
        else:
            text, color = "AN ENEMY HAS BEEN KILLED !", self.GREEN
        self._announcements.append((text, color, now + 2500))

    def draw(self, player: Any, game_start_ms: int, kills: int, deaths: int) -> None:
        self._draw_bottom_bar(player)
        self._draw_timer(game_start_ms)
        self._draw_kda(kills, deaths)
        self._draw_announcements()

    # ------------------------------------------------------------------

    def _draw_bottom_bar(self, player: Any) -> None:
        bar_surf = pygame.Surface((self.sw, self.BAR_H), pygame.SRCALPHA)
        bar_surf.fill((8, 8, 20, 215))
        self.screen.blit(bar_surf, (0, self.sh - self.BAR_H))
        pygame.draw.line(self.screen, self.CYAN,
                        (0, self.sh - self.BAR_H),
                        (self.sw, self.sh - self.BAR_H), 1)

        # --- HP bar (left side) ---
        hp_x = 24
        hp_y = self.sh - self.BAR_H + 20
        hp_w, hp_h = 220, 20
        max_hp = getattr(player, 'max_hp', 100)
        hp_frac = max(0.0, min(1.0, player.hp / max_hp)) if max_hp > 0 else 0.0
        hp_color = self.GREEN if hp_frac > 0.5 else self.YELLOW if hp_frac > 0.25 else self.RED

        pygame.draw.rect(self.screen, (20, 20, 40), (hp_x, hp_y, hp_w, hp_h), border_radius=5)
        if hp_frac > 0:
            pygame.draw.rect(self.screen, hp_color,
                             (hp_x, hp_y, int(hp_w * hp_frac), hp_h), border_radius=5)
        pygame.draw.rect(self.screen, self.CYAN, (hp_x, hp_y, hp_w, hp_h), 1, border_radius=5)

        hp_text = self.f_hp.render(f"HP   {max(0, player.hp)} / {max_hp}", True, self.TEXT)
        self.screen.blit(hp_text, (hp_x, hp_y + hp_h + 8))

        # --- XP bar + level (below HP) ---
        level = getattr(player, 'level', 1)
        xp    = getattr(player, 'xp', 0)
        xp_y  = hp_y + hp_h + 30
        xp_w, xp_h = 220, 6
        if level < MAX_LEVEL:
            xp_frac = min(1.0, xp / _XP_TO_NEXT[level - 1])
            xp_label = f"NIV {level}   {xp} / {_XP_TO_NEXT[level - 1]} XP"
        else:
            xp_frac  = 1.0
            xp_label = f"NIV {level}   MAX"
        pygame.draw.rect(self.screen, (20, 20, 40), (hp_x, xp_y, xp_w, xp_h), border_radius=3)
        if xp_frac > 0:
            pygame.draw.rect(self.screen, self.PURPLE,
                             (hp_x, xp_y, int(xp_w * xp_frac), xp_h), border_radius=3)
        pygame.draw.rect(self.screen, self.DIM, (hp_x, xp_y, xp_w, xp_h), 1, border_radius=3)
        lv_surf = self.f_name.render(xp_label, True, self.PURPLE if level >= MAX_LEVEL else self.TEXT)
        self.screen.blit(lv_surf, (hp_x, xp_y + xp_h + 3))

        # --- Ability icons (center) ---
        total_icons = 3
        total_w = total_icons * self.ICON_SZ + (total_icons - 1) * self.ICON_GAP
        start_x = self.sw // 2 - total_w // 2
        icon_y = self.sh - self.BAR_H + (self.BAR_H - self.ICON_SZ) // 2

        slots = [
            ("A",  None,                              "Attaque"),
            ("E",  getattr(player, 'ability_q', None), ""),
            ("R",  getattr(player, 'ability_e', None), ""),
        ]
        for i, (key, ability, fallback_name) in enumerate(slots):
            ix = start_x + i * (self.ICON_SZ + self.ICON_GAP)
            self._draw_icon(ix, icon_y, key, ability, fallback_name)

    def _draw_icon(self, x: int, y: int, key: str, ability: Any, fallback_name: str) -> None:
        sz = self.ICON_SZ
        rect = pygame.Rect(x, y, sz, sz)

        pygame.draw.rect(self.screen, self.ICON_BG, rect, border_radius=7)

        if ability is None:
            # Basic attack slot
            pygame.draw.rect(self.screen, self.CYAN, rect, 1, border_radius=7)
            name_s = self.f_name.render(fallback_name, True, self.DIM)
            self.screen.blit(name_s, name_s.get_rect(centerx=x + sz // 2, y=y + 6))
            key_s = self.f_key.render(key, True, self.TEXT)
            self.screen.blit(key_s, key_s.get_rect(right=x + sz - 5, bottom=y + sz - 4))
            return

        frac = ability.cooldown_fraction  # 1.0 ready, 0.0 just used

        # Cooldown grey overlay (fills from top, shrinks as cooldown recovers)
        if frac < 1.0:
            filled_h = int(sz * (1.0 - frac))
            overlay = pygame.Surface((sz, sz), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170), pygame.Rect(0, 0, sz, filled_h))
            self.screen.blit(overlay, (x, y))

        # Border: purple when ready, dim when on cooldown
        border_col = self.PURPLE if frac >= 1.0 else self.DIM
        pygame.draw.rect(self.screen, border_col, rect, 2, border_radius=7)

        # Ability name (top)
        name_s = self.f_name.render(ability.name[:9], True, self.TEXT if frac >= 1.0 else self.DIM)
        self.screen.blit(name_s, name_s.get_rect(centerx=x + sz // 2, y=y + 5))

        # Cooldown number (center when on cooldown)
        if frac < 1.0:
            cd_s = self.f_cd.render(f"{ability.cooldown_remaining_s:.1f}s", True, self.TEXT)
            self.screen.blit(cd_s, cd_s.get_rect(center=(x + sz // 2, y + sz // 2 + 4)))

        # Key label (bottom right)
        key_col = self.CYAN if frac >= 1.0 else self.DIM
        key_s = self.f_key.render(key, True, key_col)
        self.screen.blit(key_s, key_s.get_rect(right=x + sz - 5, bottom=y + sz - 4))

    def _draw_timer(self, game_start_ms: int) -> None:
        elapsed_s = (pygame.time.get_ticks() - game_start_ms) // 1000
        minutes = elapsed_s // 60
        seconds = elapsed_s % 60
        timer_s = self.f_timer.render(f"{minutes:02d}:{seconds:02d}", True, self.TEXT)
        # Background pill
        tr = timer_s.get_rect(centerx=self.sw // 2, y=10)
        bg = pygame.Surface((tr.width + 20, tr.height + 8), pygame.SRCALPHA)
        bg.fill((8, 8, 20, 180))
        self.screen.blit(bg, (tr.x - 10, tr.y - 4))
        self.screen.blit(timer_s, tr)

    def _draw_kda(self, kills: int, deaths: int) -> None:
        k_s = self.f_kda.render(f"K  {kills}", True, self.GREEN)
        d_s = self.f_kda.render(f"D  {deaths}", True, self.RED)
        self.screen.blit(k_s, k_s.get_rect(right=self.sw - 24, y=10))
        self.screen.blit(d_s, d_s.get_rect(right=self.sw - 24 + k_s.get_height() + 4, y=10))

    def _draw_announcements(self) -> None:
        now = pygame.time.get_ticks()
        self._announcements = [a for a in self._announcements if now < a[2]]
        y = 68  # Below the timer pill (~y=10 + 30px height + gap)
        for text, color, expiry in self._announcements:
            remaining = expiry - now
            alpha = 255 if remaining > 500 else int(remaining / 500 * 255)

            shadow = self.f_announce.render(text, True, (0, 0, 0))
            shadow.set_alpha(alpha // 2)
            surf = self.f_announce.render(text, True, color)
            surf.set_alpha(alpha)

            rect = surf.get_rect(centerx=self.sw // 2, y=y)
            self.screen.blit(shadow, (rect.x + 2, rect.y + 2))
            self.screen.blit(surf, rect)
            y += surf.get_height() + 8
