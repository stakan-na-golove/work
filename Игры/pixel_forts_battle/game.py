import pygame
import math
import random
from settings import *
from sprites import Player, Ghost, FlyingObject, ItemBox, Cloud, BackgroundMountain
from projectiles import Projectile, BombProjectile, RicochetProjectile, SniperProjectile, ShieldProjectile
from ui import draw_player_ui, draw_cannon_ui, draw_sniper_laser, draw_game_over_screen
from utils import draw_background, load_map, create_default_map, get_map_list
from editor import run_editor

class GameStats:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.shots_fired = {'p1': 0, 'p2': 0}
        self.hits = {'p1': 0, 'p2': 0}
        self.blocks_placed = {'p1': 0, 'p2': 0}
        self.boxes_collected = {'p1': 0, 'p2': 0}
        self.ghosts_killed = {'p1': 0, 'p2': 0}
        self.ghosts_summoned = {'p1': 0, 'p2': 0}
        self.damage_dealt = {'p1': 0, 'p2': 0}
        self.deaths = {'p1': 0, 'p2': 0}
        self.winner = None
        self.game_time = 0

def run_game(screen, clock, selected_map):
    from utils import load_map, create_default_map
    
    tiles, cannons = load_map(selected_map) if selected_map else create_default_map()
    
    projectiles = pygame.sprite.Group()
    boxes = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()
    stats = GameStats()
    
    flying_obj = FlyingObject()
    flying_group = pygame.sprite.GroupSingle(flying_obj)
    
    p1_controls = {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'up': pygame.K_w,
        'down': pygame.K_s,
        'shoot_left': pygame.K_a,
        'shoot_right': pygame.K_d,
        'toggle_cannon': pygame.K_q  # Вход/выход из пушки
    }
    p2_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'shoot_left': pygame.K_LEFT,
        'shoot_right': pygame.K_RIGHT,
        'toggle_cannon': pygame.K_RSHIFT  # Вход/выход из пушки
    }
    
    p1 = Player(100, 300, BLUE, p1_controls, 'p1')
    p2 = Player(SCREEN_WIDTH - 140, 300, RED, p2_controls, 'p2')
    players = [p1, p2]
    
    clouds = [Cloud() for _ in range(8)]
    mountains = [
        BackgroundMountain(50, 120, (100, 130, 100)),
        BackgroundMountain(250, 180, (80, 110, 80)),
        BackgroundMountain(500, 150, (90, 120, 90)),
        BackgroundMountain(750, 200, (70, 100, 70)),
        BackgroundMountain(1000, 140, (85, 115, 85)),
    ]
    
    game_over = False
    winner = None
    start_time = pygame.time.get_ticks()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if game_over:
                    if event.key == pygame.K_SPACE:
                        return "MENU"
                    elif event.key == pygame.K_r:
                        return run_game(screen, clock, selected_map)
            if not game_over:
                for p in players:
                    p.handle_event(event, tiles, projectiles, cannons, players, stats)
        
        if not game_over:
            stats.game_time = (pygame.time.get_ticks() - start_time) / 1000
            flying_group.update(boxes)
            boxes.update(tiles, players, ghosts, stats)
            projectiles.update(tiles, players, ghosts, stats)
            ghosts.update(players, tiles)
            for p in players:
                p.update(tiles, cannons, projectiles, players)
                if p.check_death(stats):
                    winner = 'p2' if p.name == 'p1' else 'p1'
                    stats.winner = winner
                    game_over = True
        
        draw_background(screen, clouds, mountains)
        tiles.draw(screen)
        boxes.draw(screen)
        flying_group.draw(screen)
        projectiles.draw(screen)
        ghosts.draw(screen)
        
        for p in players:
            if p.in_cannon:
                if p.cannon_type == TYPE_CANNON_SNIPER:
                    draw_sniper_laser(screen, p)
                start = p.in_cannon.rect.center
                rad = math.radians(p.cannon_angle)
                end = (start[0] + math.cos(rad) * 50, start[1] - math.sin(rad) * 50)
                cannon_color = CANNON_COLORS.get(p.cannon_type, (80, 80, 80))
                # Оранжевый ствол если есть взрывные
                if p.has_explosive:
                    cannon_color = ORANGE
                pygame.draw.line(screen, (30, 30, 30), start, end, 10)
                pygame.draw.line(screen, cannon_color, start, end, 6)
                pygame.draw.circle(screen, cannon_color, (int(end[0]), int(end[1])), 8)
                draw_cannon_ui(screen, p)
            else:
                screen.blit(p.image, p.rect)
        
        draw_player_ui(screen, p1, 20, 20)
        draw_player_ui(screen, p2, SCREEN_WIDTH - 220, 20)
        
        if not game_over:
            hint = font_small.render("ESC - Menu", True, (200, 200, 200))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 10))
        else:
            draw_game_over_screen(screen, stats, winner, p1, p2)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return "MENU"