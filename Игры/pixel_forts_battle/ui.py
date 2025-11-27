import pygame
import math
from settings import *
from sprites import Block

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, (30, 30, 30), (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), border_radius=10)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=10)
        text_surf = font_medium.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed

class DropdownMenu:
    def __init__(self, x, y, width, options, colors=None):
        self.x = x
        self.y = y
        self.width = width
        self.item_height = 30
        self.options = options
        self.colors = colors or {}
        self.is_open = False
        self.selected_index = 0
    
    def draw(self, surface):
        main_rect = pygame.Rect(self.x, self.y, self.width, self.item_height)
        color = self.colors.get(self.selected_index, GRAY)
        pygame.draw.rect(surface, (40, 40, 60), main_rect, border_radius=5)
        pygame.draw.rect(surface, color, main_rect, 2, border_radius=5)
        text = font_small.render(self.options[self.selected_index], True, WHITE)
        surface.blit(text, (self.x + 10, self.y + 7))
        arrow = "▼" if not self.is_open else "▲"
        arrow_surf = font_small.render(arrow, True, WHITE)
        surface.blit(arrow_surf, (self.x + self.width - 20, self.y + 7))
        
        if self.is_open:
            for i, option in enumerate(self.options):
                item_rect = pygame.Rect(self.x, self.y + (i + 1) * self.item_height, self.width, self.item_height)
                item_color = self.colors.get(i, GRAY)
                pygame.draw.rect(surface, (50, 50, 70), item_rect)
                pygame.draw.rect(surface, item_color, item_rect, 2)
                text = font_small.render(option, True, WHITE)
                surface.blit(text, (self.x + 10, item_rect.y + 7))
    
    def handle_click(self, mouse_pos):
        main_rect = pygame.Rect(self.x, self.y, self.width, self.item_height)
        if main_rect.collidepoint(mouse_pos):
            self.is_open = not self.is_open
            return True
        if self.is_open:
            for i in range(len(self.options)):
                item_rect = pygame.Rect(self.x, self.y + (i + 1) * self.item_height, self.width, self.item_height)
                if item_rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    self.is_open = False
                    return True
            self.is_open = False
        return False
    
    def get_selected_value(self):
        return self.selected_index

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = WHITE
        self.text = text
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return self.text
            elif len(self.text) < 20:
                if event.unicode.isalnum() or event.unicode in ['_', '-']:
                    self.text += event.unicode
        return None
    
    def draw(self, surface):
        color = CYAN if self.active else WHITE
        pygame.draw.rect(surface, (40, 40, 60), self.rect, border_radius=5)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)
        text_surf = font_medium.render(self.text + ('|' if self.active else ''), True, WHITE)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + 10))

def draw_player_ui(surface, player, x, y):
    panel = pygame.Surface((200, 80), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 150), (0, 0, 200, 80), border_radius=10)
    pygame.draw.rect(panel, player.base_color, (0, 0, 200, 80), 2, border_radius=10)
    surface.blit(panel, (x, y))
    name_text = "Player 1 (WASD)" if player.name == 'p1' else "Player 2 (Arrows)"
    name_surf = font_small.render(name_text, True, player.base_color)
    surface.blit(name_surf, (x + 10, y + 5))
    hp_width = 180 * (max(0, player.hp) / 100)
    hp_color = GREEN if player.hp > 50 else ORANGE if player.hp > 25 else RED
    pygame.draw.rect(surface, (60, 60, 60), (x + 10, y + 25, 180, 12), border_radius=3)
    pygame.draw.rect(surface, hp_color, (x + 10, y + 25, hp_width, 12), border_radius=3)
    hp_text = font_small.render(f"{max(0, player.hp)}%", True, WHITE)
    surface.blit(hp_text, (x + 90, y + 24))
    ammo_surf = font_small.render(f"Ammo: {player.ammo}", True, GOLD)
    surface.blit(ammo_surf, (x + 10, y + 42))
    # Показываем взрывные заряды
    if player.has_explosive:
        exp_surf = font_small.render(f"Explosive: {player.explosive_shots}", True, ORANGE)
        surface.blit(exp_surf, (x + 100, y + 42))
    if player.in_cannon:
        cannon_name = CANNON_NAMES.get(player.cannon_type, "Unknown")
        cannon_color = CANNON_COLORS.get(player.cannon_type, WHITE)
        cannon_surf = font_small.render(f"Cannon: {cannon_name}", True, cannon_color)
        surface.blit(cannon_surf, (x + 10, y + 60))

def draw_cannon_ui(surface, player):
    x, y = player.rect.centerx - 110, player.rect.top - 100
    panel = pygame.Surface((220, 85), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 200), (0, 0, 220, 85), border_radius=8)
    cannon_color = CANNON_COLORS.get(player.cannon_type, GOLD)
    pygame.draw.rect(panel, cannon_color, (0, 0, 220, 85), 2, border_radius=8)
    surface.blit(panel, (x, y))
    cannon_name = CANNON_NAMES.get(player.cannon_type, "Cannon")
    name_surf = font_small.render(cannon_name, True, cannon_color)
    surface.blit(name_surf, (x + 10, y + 5))
    cooldown, ammo_cost = CANNON_STATS.get(player.cannon_type, (250, 1))
    stats_text = f"Cost: {ammo_cost} | CD: {cooldown}ms"
    stats_surf = font_small.render(stats_text, True, (180, 180, 180))
    surface.blit(stats_surf, (x + 10, y + 22))
    if player.name == 'p1':
        text1 = font_small.render("Aim: W/S | Shoot: A/D", True, WHITE)
        text2 = font_small.render("Exit: Q", True, (200, 200, 200))
    else:
        text1 = font_small.render("Aim: ↑/↓ | Shoot: ←/→", True, WHITE)
        text2 = font_small.render("Exit: Right Shift", True, (200, 200, 200))
    surface.blit(text1, (x + 10, y + 42))
    surface.blit(text2, (x + 10, y + 58))
    # Показываем взрывные заряды
    if player.has_explosive:
        exp_surf = font_small.render(f"EXPLOSIVE: {player.explosive_shots}", True, ORANGE)
        surface.blit(exp_surf, (x + 10, y + 72))

def draw_sniper_laser(surface, player):
    if player.cannon_type != TYPE_CANNON_SNIPER:
        return
    start = player.in_cannon.rect.center
    rad = math.radians(player.cannon_angle)
    end_x = start[0] + math.cos(rad) * 2000
    end_y = start[1] - math.sin(rad) * 2000
    color = ORANGE if player.has_explosive else (0, 255, 0)
    pygame.draw.line(surface, color, start, (end_x, end_y), 1)
    pygame.draw.circle(surface, color, (int(start[0] + math.cos(rad) * 100), 
                                         int(start[1] - math.sin(rad) * 100)), 3)

def draw_game_over_screen(surface, stats, winner_name, p1, p2):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 200), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(overlay, (0, 0))
    winner_color = BLUE if winner_name == 'p1' else RED
    winner_text = "PLAYER 1 WINS!" if winner_name == 'p1' else "PLAYER 2 WINS!"
    title = font_title.render(winner_text, True, winner_color)
    title_shadow = font_title.render(winner_text, True, BLACK)
    surface.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 53))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
    panel_width = 900
    panel_height = 400
    panel_x = SCREEN_WIDTH//2 - panel_width//2
    panel_y = 140
    pygame.draw.rect(surface, (30, 30, 50), (panel_x, panel_y, panel_width, panel_height), border_radius=15)
    pygame.draw.rect(surface, GOLD, (panel_x, panel_y, panel_width, panel_height), 3, border_radius=15)
    stats_title = font_large.render("GAME STATISTICS", True, WHITE)
    surface.blit(stats_title, (SCREEN_WIDTH//2 - stats_title.get_width()//2, panel_y + 15))
    pygame.draw.line(surface, GOLD, (panel_x + 50, panel_y + 70), (panel_x + panel_width - 50, panel_y + 70), 2)
    col1_x = panel_x + 100
    col2_x = SCREEN_WIDTH//2 - 50
    col3_x = SCREEN_WIDTH//2 + 150
    p1_header = font_medium.render("PLAYER 1", True, BLUE)
    p2_header = font_medium.render("PLAYER 2", True, RED)
    surface.blit(p1_header, (col1_x, panel_y + 85))
    surface.blit(p2_header, (col3_x, panel_y + 85))
    stat_items = [
        ("Shots Fired:", stats.shots_fired['p1'], stats.shots_fired['p2']),
        ("Hits:", stats.hits['p1'], stats.hits['p2']),
        ("Accuracy:", 
         f"{(stats.hits['p1']/max(1,stats.shots_fired['p1'])*100):.1f}%",
         f"{(stats.hits['p2']/max(1,stats.shots_fired['p2'])*100):.1f}%"),
        ("Damage Dealt:", stats.damage_dealt['p1'], stats.damage_dealt['p2']),
        ("Blocks Placed:", stats.blocks_placed['p1'], stats.blocks_placed['p2']),
        ("Boxes Collected:", stats.boxes_collected['p1'], stats.boxes_collected['p2']),
        ("Ghosts Summoned:", stats.ghosts_summoned['p1'], stats.ghosts_summoned['p2']),
        ("Ghosts Killed:", stats.ghosts_killed['p1'], stats.ghosts_killed['p2']),
    ]
    y_offset = panel_y + 120
    for stat_name, val1, val2 in stat_items:
        name_surf = font_small.render(stat_name, True, (200, 200, 200))
        surface.blit(name_surf, (col2_x - name_surf.get_width()//2, y_offset))
        val1_surf = font_medium.render(str(val1), True, WHITE)
        val2_surf = font_medium.render(str(val2), True, WHITE)
        surface.blit(val1_surf, (col1_x + 30, y_offset - 3))
        surface.blit(val2_surf, (col3_x + 30, y_offset - 3))
        y_offset += 32
    minutes = int(stats.game_time // 60)
    seconds = int(stats.game_time % 60)
    time_text = font_medium.render(f"Game Time: {minutes}:{seconds:02d}", True, CYAN)
    surface.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, panel_y + panel_height - 50))
    hint = font_medium.render("Press SPACE to return to menu, R to restart", True, (150, 150, 150))
    surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 60))

def draw_menu(surface, clouds, mountains, buttons, selected_map, map_list):
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(135 + (200 - 135) * ratio)
        g = int(206 + (220 - 206) * ratio)
        b = int(235 + (255 - 235) * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    pygame.draw.circle(surface, (255, 255, 200), (100, 80), 50)
    pygame.draw.circle(surface, (255, 255, 100), (100, 80), 40)
    
    for m in mountains:
        m.draw(surface)
    
    for cloud in clouds:
        cloud.update()
        cloud.draw(surface)
    
    pygame.draw.rect(surface, DARK_GREEN, (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60))
    pygame.draw.rect(surface, GREEN, (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 15))
    
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (0, 0, 0, 100), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(overlay, (0, 0))
    title = font_large.render("PIXEL FORTS BATTLE", True, GOLD)
    title_shadow = font_large.render("PIXEL FORTS BATTLE", True, (100, 70, 0))
    surface.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 83))
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
    subtitle = font_medium.render("Two-player cannon warfare!", True, WHITE)
    surface.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 150))
    
    for btn in buttons:
        btn.draw(surface)
    
    pygame.draw.rect(surface, (40, 40, 60, 200), (SCREEN_WIDTH//2 - 150, 400, 300, 200), border_radius=10)
    pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2 - 150, 400, 300, 200), 2, border_radius=10)
    maps_title = font_medium.render("Available Maps:", True, CYAN)
    surface.blit(maps_title, (SCREEN_WIDTH//2 - maps_title.get_width()//2, 410))
    
    for i, map_name in enumerate(map_list[:6]):
        color = GOLD if map_name == selected_map else WHITE
        map_text = font_small.render(f"• {map_name}", True, color)
        surface.blit(map_text, (SCREEN_WIDTH//2 - 130, 445 + i * 25))
    
    if not map_list:
        no_maps = font_small.render("No saved maps (using default)", True, (150, 150, 150))
        surface.blit(no_maps, (SCREEN_WIDTH//2 - no_maps.get_width()//2, 460))
    
    cannon_info_y = 615
    cannon_text = font_small.render("Cannons: Normal | Triple | Bomb | Ricochet | Shield | Sniper", True, (180, 180, 180))
    surface.blit(cannon_text, (SCREEN_WIDTH//2 - cannon_text.get_width()//2, cannon_info_y))
    ctrl1 = font_small.render("P1: WASD, Q enter/exit cannon | P2: Arrows, RShift enter/exit", True, (150, 150, 150))
    surface.blit(ctrl1, (SCREEN_WIDTH//2 - ctrl1.get_width()//2, cannon_info_y + 20))
    box_text = font_small.render("Boxes: Ammo | Health | Ghost | Explosive (piercing shots!)", True, (180, 180, 180))
    surface.blit(box_text, (SCREEN_WIDTH//2 - box_text.get_width()//2, cannon_info_y + 40))