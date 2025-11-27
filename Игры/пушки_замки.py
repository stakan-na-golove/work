import pygame
import json
import os
import math
import random

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
BLOCK_SIZE = 40
FPS = 60
MAPS_FOLDER = "maps"

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
BLUE = (65, 105, 225)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
GOLD = (255, 215, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
PURPLE = (148, 0, 211)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 105, 180)
YELLOW = (255, 255, 0)

# Типы блоков
TYPE_AIR = 0
TYPE_GROUND = 1
TYPE_STONE = 2
TYPE_CANNON = 3
TYPE_CANNON_TRIPLE = 4
TYPE_CANNON_BOMB = 5
TYPE_CANNON_RICOCHET = 6
TYPE_CANNON_SHIELD = 7
TYPE_CANNON_SNIPER = 8

# Все типы пушек
CANNON_TYPES = [TYPE_CANNON, TYPE_CANNON_TRIPLE, TYPE_CANNON_BOMB, 
                TYPE_CANNON_RICOCHET, TYPE_CANNON_SHIELD, TYPE_CANNON_SNIPER]

CANNON_NAMES = {
    TYPE_CANNON: "Обычная",
    TYPE_CANNON_TRIPLE: "Тройная",
    TYPE_CANNON_BOMB: "Бомбомёт",
    TYPE_CANNON_RICOCHET: "Рикошет",
    TYPE_CANNON_SHIELD: "Щит-пушка",
    TYPE_CANNON_SNIPER: "Снайперка"
}

CANNON_COLORS = {
    TYPE_CANNON: RED,
    TYPE_CANNON_TRIPLE: ORANGE,
    TYPE_CANNON_BOMB: BROWN,
    TYPE_CANNON_RICOCHET: CYAN,
    TYPE_CANNON_SHIELD: PURPLE,
    TYPE_CANNON_SNIPER: GREEN
}

# Характеристики пушек: (cooldown_ms, ammo_cost)
CANNON_STATS = {
    TYPE_CANNON: (250, 1),
    TYPE_CANNON_TRIPLE: (400, 3),
    TYPE_CANNON_BOMB: (600, 2),
    TYPE_CANNON_RICOCHET: (350, 1),
    TYPE_CANNON_SHIELD: (1500, 8),
    TYPE_CANNON_SNIPER: (1200, 1)
}

# Типы коробок
BOX_AMMO = 0
BOX_HEALTH = 1
BOX_GHOST = 2
BOX_EXPLOSIVE = 3  # Новая коробка - взрывной заряд

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel Forts Battle")
clock = pygame.time.Clock()

# Шрифты
try:
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    font_title = pygame.font.Font(None, 96)
except:
    font_large = pygame.font.SysFont("Arial", 56, bold=True)
    font_medium = pygame.font.SysFont("Arial", 28, bold=True)
    font_small = pygame.font.SysFont("Arial", 18)
    font_title = pygame.font.SysFont("Arial", 72, bold=True)

# Создаём папку для карт
if not os.path.exists(MAPS_FOLDER):
    os.makedirs(MAPS_FOLDER)


# --- КЛАСС СТАТИСТИКИ ---
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


# --- ФОНОВЫЕ ЭЛЕМЕНТЫ ---
class Cloud:
    def __init__(self):
        self.x = random.randint(-100, SCREEN_WIDTH + 100)
        self.y = random.randint(50, 250)
        self.speed = random.uniform(0.2, 0.8)
        self.size = random.randint(40, 100)
        
    def update(self):
        self.x += self.speed
        if self.x > SCREEN_WIDTH + 150:
            self.x = -150
            self.y = random.randint(50, 250)
    
    def draw(self, surface):
        s = self.size
        pygame.draw.ellipse(surface, WHITE, (self.x, self.y, s, s//2))
        pygame.draw.ellipse(surface, WHITE, (self.x + s//3, self.y - s//4, s//1.5, s//2))
        pygame.draw.ellipse(surface, WHITE, (self.x + s//2, self.y, s//1.2, s//2.5))


class BackgroundMountain:
    def __init__(self, x, height, color):
        self.x = x
        self.height = height
        self.color = color
        self.width = random.randint(150, 300)
    
    def draw(self, surface):
        points = [
            (self.x, SCREEN_HEIGHT - 60),
            (self.x + self.width // 2, SCREEN_HEIGHT - 60 - self.height),
            (self.x + self.width, SCREEN_HEIGHT - 60)
        ]
        pygame.draw.polygon(surface, self.color, points)


def draw_background(surface, clouds, mountains):
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


# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ РИСОВАНИЯ ---
def draw_pixel_char(surface, color, facing_right):
    surface.fill((0, 0, 0, 0))
    pygame.draw.rect(surface, color, (10, 0, 20, 20))
    pygame.draw.rect(surface, (min(255, color[0]+30), min(255, color[1]+30), min(255, color[2]+30)), 
                     (12, 2, 16, 16))
    eye_x = 22 if facing_right else 12
    pygame.draw.rect(surface, WHITE, (eye_x, 5, 6, 6))
    pygame.draw.rect(surface, BLACK, (eye_x + 2 if facing_right else eye_x, 7, 2, 2))
    body_color = (int(color[0] * 0.7), int(color[1] * 0.7), int(color[2] * 0.7))
    pygame.draw.rect(surface, body_color, (5, 20, 30, 20))
    pygame.draw.rect(surface, color, (8, 22, 24, 16))
    pygame.draw.rect(surface, (50, 50, 50), (10, 40, 8, 10))
    pygame.draw.rect(surface, (50, 50, 50), (22, 40, 8, 10))


def draw_box(surface, box_type):
    surface.fill(BROWN)
    pygame.draw.rect(surface, (180, 100, 60), (2, 2, 26, 8))
    pygame.draw.rect(surface, BLACK, (0, 0, 30, 30), 2)
    
    if box_type == BOX_AMMO:
        pygame.draw.rect(surface, GOLD, (12, 10, 6, 12))
        pygame.draw.polygon(surface, GOLD, [(12, 10), (18, 10), (15, 5)])
    elif box_type == BOX_HEALTH:
        pygame.draw.rect(surface, RED, (13, 8, 4, 16))
        pygame.draw.rect(surface, RED, (7, 14, 16, 4))
    elif box_type == BOX_GHOST:
        pygame.draw.ellipse(surface, (200, 200, 255), (8, 8, 14, 12))
        pygame.draw.rect(surface, (200, 200, 255), (8, 14, 14, 8))
        pygame.draw.circle(surface, BLACK, (12, 12), 2)
        pygame.draw.circle(surface, BLACK, (18, 12), 2)
    elif box_type == BOX_EXPLOSIVE:
        # Взрывной заряд - оранжевая звезда/взрыв
        pygame.draw.circle(surface, ORANGE, (15, 15), 8)
        pygame.draw.circle(surface, YELLOW, (15, 15), 5)
        # Лучи взрыва
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = 15 + math.cos(rad) * 6
            y1 = 15 + math.sin(rad) * 6
            x2 = 15 + math.cos(rad) * 10
            y2 = 15 + math.sin(rad) * 10
            pygame.draw.line(surface, YELLOW, (x1, y1), (x2, y2), 2)


def get_neighbor_stones(block, tiles):
    """Возвращает соседние камни"""
    neighbors = []
    for b in tiles:
        if b.type == TYPE_STONE and b != block:
            dx = abs(b.rect.centerx - block.rect.centerx)
            dy = abs(b.rect.centery - block.rect.centery)
            if dx <= BLOCK_SIZE and dy <= BLOCK_SIZE:
                neighbors.append(b)
    return neighbors


# --- КЛАССЫ СНАРЯДОВ ---
class Projectile(pygame.sprite.Sprite):
    """Обычный снаряд"""
    def __init__(self, x, y, angle, owner_name, explosive=False):
        super().__init__()
        self.explosive = explosive
        self.piercing = explosive  # Пробивает первое препятствие
        self.has_pierced = False  # Уже пробил одно препятствие
        
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        if explosive:
            pygame.draw.circle(self.image, ORANGE, (7, 7), 7)
            pygame.draw.circle(self.image, YELLOW, (7, 7), 4)
        else:
            pygame.draw.circle(self.image, (40, 40, 40), (7, 7), 7)
            pygame.draw.circle(self.image, (80, 80, 80), (7, 7), 5)
            pygame.draw.circle(self.image, (60, 60, 60), (5, 5), 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        speed = 16
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = -math.sin(math.radians(angle)) * speed
        self.owner_name = owner_name
        self.gravity = 0.15
        self.damage = 30 if explosive else 20

    def update(self, tiles, players, ghosts, stats):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        for block in list(tiles):
            if self.rect.colliderect(block.rect):
                if block.type == TYPE_STONE:
                    block.kill()
                    if self.piercing and not self.has_pierced:
                        self.has_pierced = True
                        continue
                    self.kill()
                    return
                elif block.type == TYPE_GROUND:
                    if self.piercing and not self.has_pierced:
                        self.has_pierced = True
                        continue
                    self.kill()
                    return

        for ghost in list(ghosts):
            if self.rect.colliderect(ghost.rect):
                if ghost.take_damage(40 if self.explosive else 30):
                    stats.ghosts_killed[self.owner_name] += 1
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        for p in players:
            if p.name != self.owner_name and self.rect.colliderect(p.rect):
                p.hp -= self.damage
                stats.hits[self.owner_name] += 1
                stats.damage_dealt[self.owner_name] += self.damage
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        if self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()


class BombProjectile(pygame.sprite.Sprite):
    """Тяжёлая бомба"""
    def __init__(self, x, y, angle, owner_name, explosive=False):
        super().__init__()
        self.explosive = explosive
        self.piercing = explosive
        self.has_pierced = False
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        if explosive:
            pygame.draw.circle(self.image, ORANGE, (10, 10), 10)
            pygame.draw.circle(self.image, YELLOW, (10, 10), 6)
        else:
            pygame.draw.circle(self.image, (30, 30, 30), (10, 10), 10)
            pygame.draw.circle(self.image, (60, 60, 60), (10, 10), 7)
        pygame.draw.line(self.image, ORANGE, (10, 0), (10, 4), 2)
        pygame.draw.circle(self.image, YELLOW, (10, 2), 3)
        
        self.rect = self.image.get_rect(center=(x, y))
        speed = 12
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = -math.sin(math.radians(angle)) * speed
        self.owner_name = owner_name
        self.gravity = 0.4
        self.damage = 45 if explosive else 35
        self.explosion_radius = 70 if explosive else 60

    def update(self, tiles, players, ghosts, stats):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        hit = False
        hit_block = None
        for block in list(tiles):
            if self.rect.colliderect(block.rect):
                hit = True
                hit_block = block
                break

        if hit and hit_block:
            # Взрыв - разрушает центральный блок
            destroyed_blocks = []
            if hit_block.type == TYPE_STONE:
                destroyed_blocks.append(hit_block)
                
                # Разрушаем 0-3 соседних камня
                neighbors = get_neighbor_stones(hit_block, tiles)
                num_to_destroy = random.randint(0, min(3, len(neighbors)))
                if num_to_destroy > 0:
                    to_destroy = random.sample(neighbors, num_to_destroy)
                    destroyed_blocks.extend(to_destroy)
                
                for b in destroyed_blocks:
                    b.kill()
            
            # Урон игрокам в радиусе
            for p in players:
                if p.name != self.owner_name:
                    dist = math.hypot(p.rect.centerx - self.rect.centerx,
                                     p.rect.centery - self.rect.centery)
                    if dist < self.explosion_radius:
                        damage = int(self.damage * (1 - dist / self.explosion_radius))
                        p.hp -= damage
                        stats.hits[self.owner_name] += 1
                        stats.damage_dealt[self.owner_name] += damage
            
            # Проверяем пробивание
            if self.piercing and not self.has_pierced:
                self.has_pierced = True
            else:
                self.kill()
                return

        for p in players:
            if p.name != self.owner_name and self.rect.colliderect(p.rect):
                p.hp -= self.damage
                stats.hits[self.owner_name] += 1
                stats.damage_dealt[self.owner_name] += self.damage
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        if self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()


class RicochetProjectile(pygame.sprite.Sprite):
    """Рикошетящий снаряд"""
    def __init__(self, x, y, angle, owner_name, explosive=False):
        super().__init__()
        self.explosive = explosive
        self.piercing = explosive
        self.has_pierced = False  # Активируется только после всех рикошетов
        
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        if explosive:
            pygame.draw.circle(self.image, ORANGE, (6, 6), 6)
            pygame.draw.circle(self.image, YELLOW, (6, 6), 3)
        else:
            pygame.draw.circle(self.image, CYAN, (6, 6), 6)
            pygame.draw.circle(self.image, WHITE, (6, 6), 3)
        
        self.rect = self.image.get_rect(center=(x, y))
        speed = 14
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = -math.sin(math.radians(angle)) * speed
        self.owner_name = owner_name
        self.gravity = 0.1
        self.damage = 25 if explosive else 15
        self.bounces = 5

    def update(self, tiles, players, ghosts, stats):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Отскок от краёв экрана
        if self.rect.left < 0:
            self.rect.left = 0
            self.vel_x = -self.vel_x
            self.bounces -= 1
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vel_x = -self.vel_x
            self.bounces -= 1

        # Отскок от блоков
        for block in list(tiles):
            if self.rect.colliderect(block.rect):
                if self.bounces <= 0:
                    # После всех рикошетов - проверяем пробивание
                    if block.type == TYPE_STONE:
                        block.kill()
                    if self.piercing and not self.has_pierced:
                        self.has_pierced = True
                        # Определяем сторону и отскакиваем
                        dx = self.rect.centerx - block.rect.centerx
                        dy = self.rect.centery - block.rect.centery
                        if abs(dx) > abs(dy):
                            self.rect.x += self.vel_x * 2
                        else:
                            self.rect.y += self.vel_y * 2
                        continue
                    self.kill()
                    return
                
                # Определяем сторону столкновения
                dx = self.rect.centerx - block.rect.centerx
                dy = self.rect.centery - block.rect.centery
                
                if abs(dx) > abs(dy):
                    self.vel_x = -self.vel_x
                    self.rect.x += self.vel_x * 2
                else:
                    self.vel_y = -self.vel_y
                    self.rect.y += self.vel_y * 2
                
                self.bounces -= 1
                break

        for ghost in list(ghosts):
            if self.rect.colliderect(ghost.rect):
                if ghost.take_damage(35 if self.explosive else 30):
                    stats.ghosts_killed[self.owner_name] += 1
                self.kill()
                return

        for p in players:
            if p.name != self.owner_name and self.rect.colliderect(p.rect):
                p.hp -= self.damage
                stats.hits[self.owner_name] += 1
                stats.damage_dealt[self.owner_name] += self.damage
                self.kill()
                return

        if self.bounces < -1 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()


class SniperProjectile(pygame.sprite.Sprite):
    """Снайперский снаряд - без гравитации, быстрый"""
    def __init__(self, x, y, angle, owner_name, explosive=False):
        super().__init__()
        self.explosive = explosive
        self.piercing = explosive
        self.has_pierced = False
        
        self.image = pygame.Surface((20, 6), pygame.SRCALPHA)
        if explosive:
            pygame.draw.rect(self.image, ORANGE, (0, 0, 20, 6))
            pygame.draw.rect(self.image, YELLOW, (0, 1, 20, 2))
        else:
            pygame.draw.rect(self.image, GREEN, (0, 0, 20, 6))
            pygame.draw.rect(self.image, (150, 255, 150), (0, 1, 20, 2))
        
        self.original_image = self.image
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        
        speed = 30
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = -math.sin(math.radians(angle)) * speed
        self.owner_name = owner_name
        self.damage = 55 if explosive else 40

    def update(self, tiles, players, ghosts, stats):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        for block in list(tiles):
            if self.rect.colliderect(block.rect):
                if block.type == TYPE_STONE:
                    block.kill()
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        for ghost in list(ghosts):
            if self.rect.colliderect(ghost.rect):
                if ghost.take_damage(60 if self.explosive else 50):
                    stats.ghosts_killed[self.owner_name] += 1
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        for p in players:
            if p.name != self.owner_name and self.rect.colliderect(p.rect):
                p.hp -= self.damage
                stats.hits[self.owner_name] += 1
                stats.damage_dealt[self.owner_name] += self.damage
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        if self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50 or \
           self.rect.top < -50 or self.rect.bottom > SCREEN_HEIGHT + 50:
            self.kill()


class ShieldProjectile(pygame.sprite.Sprite):
    """Снаряд щит-пушки"""
    def __init__(self, x, y, angle, owner_name, explosive=False):
        super().__init__()
        self.explosive = explosive
        self.piercing = explosive
        self.has_pierced = False
        
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        if explosive:
            pygame.draw.circle(self.image, ORANGE, (5, 5), 5)
            pygame.draw.circle(self.image, YELLOW, (5, 5), 3)
        else:
            pygame.draw.circle(self.image, PURPLE, (5, 5), 5)
            pygame.draw.circle(self.image, PINK, (5, 5), 3)
        
        self.rect = self.image.get_rect(center=(x, y))
        speed = 12
        self.vel_x = math.cos(math.radians(angle)) * speed
        self.vel_y = -math.sin(math.radians(angle)) * speed
        self.owner_name = owner_name
        self.gravity = 0.08
        self.damage = 15 if explosive else 10

    def update(self, tiles, players, ghosts, stats):
        self.vel_y += self.gravity
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        for block in list(tiles):
            if self.rect.colliderect(block.rect):
                if block.type == TYPE_STONE:
                    block.kill()
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        for ghost in list(ghosts):
            if self.rect.colliderect(ghost.rect):
                if ghost.take_damage(25 if self.explosive else 20):
                    stats.ghosts_killed[self.owner_name] += 1
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        for p in players:
            if p.name != self.owner_name and self.rect.colliderect(p.rect):
                p.hp -= self.damage
                stats.hits[self.owner_name] += 1
                stats.damage_dealt[self.owner_name] += self.damage
                if self.piercing and not self.has_pierced:
                    self.has_pierced = True
                    continue
                self.kill()
                return

        if self.rect.left < -50 or self.rect.right > SCREEN_WIDTH + 50 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()


# --- КЛАССЫ ---
class Ghost(pygame.sprite.Sprite):
    """Призрак, который летит к врагу"""
    def __init__(self, x, target_player, owner_name):
        super().__init__()
        self.image = pygame.Surface((30, 35), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (200, 200, 255, 200), (0, 0, 30, 25))
        pygame.draw.rect(self.image, (200, 200, 255, 200), (0, 12, 30, 15))
        for i in range(5):
            pygame.draw.ellipse(self.image, (200, 200, 255, 200), (i*6, 25, 8, 10))
        pygame.draw.circle(self.image, BLACK, (10, 10), 4)
        pygame.draw.circle(self.image, BLACK, (20, 10), 4)
        pygame.draw.circle(self.image, WHITE, (11, 9), 2)
        pygame.draw.circle(self.image, WHITE, (21, 9), 2)
        
        self.rect = self.image.get_rect(center=(x, 0))
        self.target = target_player
        self.owner_name = owner_name
        self.speed = 3.5
        self.damage = 20
        self.hp = 30
        
    def update(self, players, tiles):
        if self.hp <= 0:
            self.kill()
            return
            
        if self.target and self.target.hp > 0:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.rect.x += (dx / dist) * self.speed
                self.rect.y += (dy / dist) * self.speed
            
            if self.rect.colliderect(self.target.rect):
                self.target.hp -= self.damage
                self.kill()
        else:
            self.rect.y -= 3
        
        if self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()
    
    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            return True
        return False


class FlyingObject(pygame.sprite.Sprite):
    """Дирижабль"""
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((100, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (150, 75, 0), (0, 0, 100, 35))
        pygame.draw.ellipse(self.image, (180, 100, 30), (5, 3, 90, 29))
        pygame.draw.line(self.image, (120, 60, 0), (20, 5), (20, 30), 2)
        pygame.draw.line(self.image, (120, 60, 0), (50, 3), (50, 32), 2)
        pygame.draw.line(self.image, (120, 60, 0), (80, 5), (80, 30), 2)
        pygame.draw.line(self.image, (100, 100, 100), (30, 35), (35, 42), 2)
        pygame.draw.line(self.image, (100, 100, 100), (70, 35), (65, 42), 2)
        pygame.draw.rect(self.image, (80, 80, 80), (30, 40, 40, 10))
        pygame.draw.rect(self.image, (60, 60, 60), (32, 42, 36, 6))
        pygame.draw.ellipse(self.image, (100, 100, 100), (90, 12, 10, 12))
        
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, 70))
        self.speed = 2
        self.direction = 1
        self.last_drop_time = pygame.time.get_ticks()
        self.drop_delay = 5000  # Увеличено с 4000 до 5000 (реже на ~20%)

    def update(self, boxes_group):
        self.rect.x += self.speed * self.direction
        if self.rect.right > SCREEN_WIDTH - 30 or self.rect.left < 30:
            self.direction *= -1

        now = pygame.time.get_ticks()
        if now - self.last_drop_time > self.drop_delay:
            self.last_drop_time = now
            if random.random() > 0.40:  # Уменьшено с 0.25 до 0.40 (реже на ~20%)
                box_type = random.choices(
                    [BOX_AMMO, BOX_HEALTH, BOX_GHOST, BOX_EXPLOSIVE], 
                    weights=[40, 35, 12, 13]
                )[0]
                new_box = ItemBox(self.rect.centerx, self.rect.bottom + 10, box_type)
                boxes_group.add(new_box)


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, x, y, box_type):
        super().__init__()
        self.box_type = box_type
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        draw_box(self.image, self.box_type)
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0

    def update(self, tiles, players, ghosts_group, stats):
        self.vel_y += 0.4
        self.vel_y = min(self.vel_y, 8)
        self.rect.y += self.vel_y

        for block in tiles:
            if block.type in [TYPE_GROUND, TYPE_STONE] and self.rect.colliderect(block.rect):
                self.rect.bottom = block.rect.top
                self.vel_y = 0
                break

        for p in players:
            if self.rect.colliderect(p.rect):
                stats.boxes_collected[p.name] += 1
                
                if self.box_type == BOX_AMMO:
                    p.ammo += 20
                elif self.box_type == BOX_HEALTH:
                    p.hp = min(100, p.hp + 25)
                elif self.box_type == BOX_GHOST:
                    enemy = [pl for pl in players if pl != p]
                    if enemy:
                        ghost = Ghost(p.rect.centerx, enemy[0], p.name)
                        ghosts_group.add(ghost)
                        stats.ghosts_summoned[p.name] += 1
                elif self.box_type == BOX_EXPLOSIVE:
                    p.has_explosive = True
                    p.explosive_shots = 5  # 5 выстрелов с взрывным зарядом
                self.kill()
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, type_id):
        super().__init__()
        self.type = type_id
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        if self.type == TYPE_GROUND:
            self.image.fill((101, 67, 33))
            pygame.draw.rect(self.image, GREEN, (0, 0, BLOCK_SIZE, 8))
            pygame.draw.rect(self.image, DARK_GREEN, (0, 6, BLOCK_SIZE, 4))
            for _ in range(6):
                bx = random.randint(2, BLOCK_SIZE - 6)
                by = random.randint(12, BLOCK_SIZE - 6)
                pygame.draw.rect(self.image, (80, 50, 20), (bx, by, 4, 4))
            pygame.draw.rect(self.image, (70, 45, 15), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 2)

        elif self.type == TYPE_STONE:
            self.image.fill((140, 140, 140))
            pygame.draw.rect(self.image, (160, 160, 160), (2, 2, BLOCK_SIZE-4, BLOCK_SIZE-4))
            pygame.draw.line(self.image, (100, 100, 100), (5, 5), (15, 20), 2)
            pygame.draw.line(self.image, (100, 100, 100), (25, 10), (35, 25), 2)
            pygame.draw.line(self.image, (100, 100, 100), (10, 30), (30, 35), 2)
            pygame.draw.rect(self.image, (110, 110, 110), (0, 0, BLOCK_SIZE, BLOCK_SIZE), 3)

        elif self.type in CANNON_TYPES:
            self._draw_cannon()

    def _draw_cannon(self):
        """Рисует пушку в зависимости от типа"""
        color = CANNON_COLORS.get(self.type, RED)
        
        self.image.fill((50, 50, 50))
        pygame.draw.rect(self.image, (70, 70, 70), (3, 3, BLOCK_SIZE-6, BLOCK_SIZE-6))
        
        for pos in [(6, 6), (BLOCK_SIZE-8, 6), (6, BLOCK_SIZE-8), (BLOCK_SIZE-8, BLOCK_SIZE-8)]:
            pygame.draw.circle(self.image, (90, 90, 90), pos, 4)
            pygame.draw.circle(self.image, (60, 60, 60), pos, 2)
        
        pygame.draw.circle(self.image, (40, 40, 40), (BLOCK_SIZE//2, BLOCK_SIZE//2), 12)
        pygame.draw.circle(self.image, color, (BLOCK_SIZE//2, BLOCK_SIZE//2), 8)
        
        if self.type == TYPE_CANNON_TRIPLE:
            for offset in [-5, 0, 5]:
                pygame.draw.circle(self.image, WHITE, (BLOCK_SIZE//2 + offset, BLOCK_SIZE//2), 2)
        
        elif self.type == TYPE_CANNON_BOMB:
            pygame.draw.circle(self.image, BLACK, (BLOCK_SIZE//2, BLOCK_SIZE//2), 5)
            pygame.draw.line(self.image, ORANGE, (BLOCK_SIZE//2, BLOCK_SIZE//2 - 5), 
                           (BLOCK_SIZE//2, BLOCK_SIZE//2 - 8), 2)
        
        elif self.type == TYPE_CANNON_RICOCHET:
            pygame.draw.line(self.image, WHITE, (BLOCK_SIZE//2 - 5, BLOCK_SIZE//2), 
                           (BLOCK_SIZE//2 + 5, BLOCK_SIZE//2), 2)
            pygame.draw.line(self.image, WHITE, (BLOCK_SIZE//2, BLOCK_SIZE//2 - 5), 
                           (BLOCK_SIZE//2, BLOCK_SIZE//2 + 5), 2)
        
        elif self.type == TYPE_CANNON_SHIELD:
            pygame.draw.circle(self.image, WHITE, (BLOCK_SIZE//2, BLOCK_SIZE//2), 6, 2)
        
        elif self.type == TYPE_CANNON_SNIPER:
            pygame.draw.line(self.image, WHITE, (BLOCK_SIZE//2 - 6, BLOCK_SIZE//2), 
                           (BLOCK_SIZE//2 + 6, BLOCK_SIZE//2), 1)
            pygame.draw.line(self.image, WHITE, (BLOCK_SIZE//2, BLOCK_SIZE//2 - 6), 
                           (BLOCK_SIZE//2, BLOCK_SIZE//2 + 6), 1)
        
        pygame.draw.circle(self.image, (min(255, color[0]+50), min(255, color[1]+50), min(255, color[2]+50)), 
                          (BLOCK_SIZE//2 - 2, BLOCK_SIZE//2 - 2), 3)


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color, controls, name):
        super().__init__()
        self.base_color = color
        self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.name = name
        self.controls = controls

        self.vel_y = 0
        self.speed = 5
        self.gravity = 0.7
        self.jump_power = -14
        self.on_ground = False
        self.facing_right = name == 'p1'

        self.hp = 100
        self.ammo = 30
        self.score = 0
        
        # Взрывные заряды
        self.has_explosive = False
        self.explosive_shots = 0

        self.in_cannon = None
        self.cannon_type = TYPE_CANNON
        self.cannon_angle = 45 if name == 'p1' else 135

        self.last_shot_time = 0

        self.update_image()

    def update_image(self):
        draw_pixel_char(self.image, self.base_color, self.facing_right)

    def get_cannon_cooldown(self):
        if self.in_cannon:
            return CANNON_STATS.get(self.cannon_type, (250, 1))[0]
        return 250

    def get_cannon_ammo_cost(self):
        if self.in_cannon:
            return CANNON_STATS.get(self.cannon_type, (250, 1))[1]
        return 1

    def find_nearby_cannon(self, cannons):
        """Находит ближайшую пушку в радиусе"""
        for cannon in cannons:
            dist = math.hypot(self.rect.centerx - cannon.rect.centerx,
                              self.rect.centery - cannon.rect.centery)
            if dist < BLOCK_SIZE * 1.2:
                return cannon
        return None

    def handle_event(self, event, tiles_group, projectiles_group, cannons, players, stats):
        if event.type != pygame.KEYDOWN:
            return
        
        # Вход/Выход из пушки по одной клавише (Q или RShift)
        if event.key == self.controls['toggle_cannon']:
            if self.in_cannon:
                # Выход из пушки
                self.exit_cannon()
            elif self.on_ground:
                # Попытка войти в пушку
                cannon = self.find_nearby_cannon(cannons)
                if cannon:
                    self.in_cannon = cannon
                    self.cannon_type = cannon.type
                    self.rect.center = cannon.rect.center
                    self.cannon_angle = 90
            return
            
        if self.in_cannon:
            if event.key in [self.controls['shoot_left'], self.controls['shoot_right']]:
                now = pygame.time.get_ticks()
                if now - self.last_shot_time > self.get_cannon_cooldown():
                    if self.ammo >= self.get_cannon_ammo_cost():
                        self.shoot_cannon(projectiles_group, stats)
                        self.last_shot_time = now
            return
        
        if event.key == self.controls['down'] and not self.on_ground:
            self.place_block_below(tiles_group, stats)

    def update(self, tiles, cannons, projectiles_group, players):
        keys = pygame.key.get_pressed()

        if self.in_cannon:
            self.rect.center = self.in_cannon.rect.center
            self.vel_y = 0
            
            # Замедленное движение ствола (было 3, стало 1.5)
            if keys[self.controls['up']]:
                self.cannon_angle = min(210, self.cannon_angle + 1.5)
            if keys[self.controls['down']]:
                self.cannon_angle = max(-30, self.cannon_angle - 1.5)
            return

        dx = 0
        if keys[self.controls['left']]:
            dx = -self.speed
            if self.facing_right:
                self.facing_right = False
                self.update_image()
        if keys[self.controls['right']]:
            dx = self.speed
            if not self.facing_right:
                self.facing_right = True
                self.update_image()

        if keys[self.controls['up']] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        self.vel_y += self.gravity
        self.vel_y = min(self.vel_y, 15)

        self.rect.x += dx
        self.collide(tiles, dx, 0)
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide(tiles, 0, self.vel_y)

    def collide(self, tiles, dx, dy):
        for block in tiles:
            if block.type in CANNON_TYPES:
                continue
            if self.rect.colliderect(block.rect):
                if dx > 0:
                    self.rect.right = block.rect.left
                if dx < 0:
                    self.rect.left = block.rect.right
                if dy > 0:
                    self.rect.bottom = block.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                if dy < 0:
                    self.rect.top = block.rect.bottom
                    self.vel_y = 0

    def place_block_below(self, tiles_group, stats):
        if self.ammo < 1:
            return
            
        grid_x = (self.rect.centerx // BLOCK_SIZE) * BLOCK_SIZE
        grid_y = (self.rect.bottom // BLOCK_SIZE) * BLOCK_SIZE
        
        new_rect = pygame.Rect(grid_x, grid_y, BLOCK_SIZE, BLOCK_SIZE)
        
        if grid_y >= SCREEN_HEIGHT:
            return

        for b in tiles_group:
            if b.rect.colliderect(new_rect):
                return

        block = Block(grid_x, grid_y, TYPE_STONE)
        tiles_group.add(block)
        self.ammo -= 1
        stats.blocks_placed[self.name] += 1
        self.rect.bottom = grid_y
        self.vel_y = 0

    def shoot_cannon(self, projectiles_group, stats):
        if not self.in_cannon:
            return
            
        ammo_cost = self.get_cannon_ammo_cost()
        if self.ammo < ammo_cost:
            return
        
        # Проверяем взрывной заряд
        explosive = False
        if self.has_explosive and self.explosive_shots > 0:
            explosive = True
            self.explosive_shots -= 1
            if self.explosive_shots <= 0:
                self.has_explosive = False
            
        rad = math.radians(self.cannon_angle)
        bx = self.rect.centerx + math.cos(rad) * 50
        by = self.rect.centery - math.sin(rad) * 50
        
        if self.cannon_type == TYPE_CANNON:
            p = Projectile(bx, by, self.cannon_angle, self.name, explosive)
            projectiles_group.add(p)
            
        elif self.cannon_type == TYPE_CANNON_TRIPLE:
            for angle_offset in [-15, 0, 15]:
                angle = self.cannon_angle + angle_offset
                rad2 = math.radians(angle)
                px = self.rect.centerx + math.cos(rad2) * 50
                py = self.rect.centery - math.sin(rad2) * 50
                p = Projectile(px, py, angle, self.name, explosive)
                projectiles_group.add(p)
                
        elif self.cannon_type == TYPE_CANNON_BOMB:
            p = BombProjectile(bx, by, self.cannon_angle, self.name, explosive)
            projectiles_group.add(p)
            
        elif self.cannon_type == TYPE_CANNON_RICOCHET:
            p = RicochetProjectile(bx, by, self.cannon_angle, self.name, explosive)
            projectiles_group.add(p)
            
        elif self.cannon_type == TYPE_CANNON_SHIELD:
            for angle in range(0, 360, 45):
                rad2 = math.radians(angle)
                px = self.rect.centerx + math.cos(rad2) * 50
                py = self.rect.centery - math.sin(rad2) * 50
                p = ShieldProjectile(px, py, angle, self.name, explosive)
                projectiles_group.add(p)
                
        elif self.cannon_type == TYPE_CANNON_SNIPER:
            p = SniperProjectile(bx, by, self.cannon_angle, self.name, explosive)
            projectiles_group.add(p)
        
        self.ammo -= ammo_cost
        stats.shots_fired[self.name] += ammo_cost

    def exit_cannon(self):
        if self.in_cannon:
            rad = math.radians(self.cannon_angle)
            offset_x = math.cos(rad) * BLOCK_SIZE
            self.rect.x += offset_x if abs(offset_x) > 10 else (-BLOCK_SIZE if self.cannon_angle > 90 else BLOCK_SIZE)
            self.vel_y = -8
            self.in_cannon = None
            self.cannon_type = TYPE_CANNON

    def respawn(self, stats):
        self.rect.x = 100 if self.name == 'p1' else SCREEN_WIDTH - 140
        self.rect.y = 100
        self.vel_y = 0
        self.hp = 100
        self.in_cannon = None
        self.has_explosive = False
        self.explosive_shots = 0
        stats.deaths[self.name] += 1

    def check_death(self, stats):
        if self.rect.top > SCREEN_HEIGHT or self.hp <= 0:
            return True
        return False


# --- СИСТЕМА КАРТ ---
def get_map_list():
    maps = []
    if os.path.exists(MAPS_FOLDER):
        for f in os.listdir(MAPS_FOLDER):
            if f.endswith('.json'):
                maps.append(f[:-5])
    return maps


def save_map(tiles, filename):
    if not filename.endswith('.json'):
        filename += '.json'
    filepath = os.path.join(MAPS_FOLDER, filename)
    data = []
    for b in tiles:
        data.append({'x': b.rect.x, 'y': b.rect.y, 'type': b.type})
    with open(filepath, 'w') as f:
        json.dump(data, f)
    return True


def load_map(filename):
    group = pygame.sprite.Group()
    cannons = pygame.sprite.Group()
    
    if filename and not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join(MAPS_FOLDER, filename) if filename else None
    
    if filepath and os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
            for d in data:
                b = Block(d['x'], d['y'], d['type'])
                group.add(b)
                if d['type'] in CANNON_TYPES:
                    cannons.add(b)
    else:
        group, cannons = create_default_map()
    
    return group, cannons


def create_default_map():
    group = pygame.sprite.Group()
    cannons = pygame.sprite.Group()
    
    for i in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        for j in range(2):
            b = Block(i, SCREEN_HEIGHT - BLOCK_SIZE * (j + 1), TYPE_GROUND)
            group.add(b)
    
    for i in range(3):
        b = Block(BLOCK_SIZE * i, SCREEN_HEIGHT - BLOCK_SIZE * 3, TYPE_GROUND)
        group.add(b)
    for i in range(2):
        b = Block(BLOCK_SIZE * i, SCREEN_HEIGHT - BLOCK_SIZE * 4, TYPE_STONE)
        group.add(b)
    c1 = Block(BLOCK_SIZE * 2, SCREEN_HEIGHT - BLOCK_SIZE * 4, TYPE_CANNON)
    group.add(c1)
    cannons.add(c1)
    
    for i in range(3):
        b = Block(SCREEN_WIDTH - BLOCK_SIZE * (i + 1), SCREEN_HEIGHT - BLOCK_SIZE * 3, TYPE_GROUND)
        group.add(b)
    for i in range(2):
        b = Block(SCREEN_WIDTH - BLOCK_SIZE * (i + 1), SCREEN_HEIGHT - BLOCK_SIZE * 4, TYPE_STONE)
        group.add(b)
    c2 = Block(SCREEN_WIDTH - BLOCK_SIZE * 3, SCREEN_HEIGHT - BLOCK_SIZE * 4, TYPE_CANNON_TRIPLE)
    group.add(c2)
    cannons.add(c2)
    
    center_x = SCREEN_WIDTH // 2 - BLOCK_SIZE * 2
    for i in range(5):
        b = Block(center_x + i * BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE * 5, TYPE_STONE)
        group.add(b)
    c3 = Block(center_x + 2 * BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE * 6, TYPE_CANNON_SNIPER)
    group.add(c3)
    cannons.add(c3)
    
    for i in range(3):
        b = Block(BLOCK_SIZE * 5 + i * BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE * 7, TYPE_STONE)
        group.add(b)
    c4 = Block(BLOCK_SIZE * 6, SCREEN_HEIGHT - BLOCK_SIZE * 8, TYPE_CANNON_BOMB)
    group.add(c4)
    cannons.add(c4)
    
    for i in range(3):
        b = Block(SCREEN_WIDTH - BLOCK_SIZE * 8 + i * BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE * 7, TYPE_STONE)
        group.add(b)
    c5 = Block(SCREEN_WIDTH - BLOCK_SIZE * 7, SCREEN_HEIGHT - BLOCK_SIZE * 8, TYPE_CANNON_RICOCHET)
    group.add(c5)
    cannons.add(c5)
    
    for i in range(3):
        b = Block(SCREEN_WIDTH // 2 - BLOCK_SIZE + i * BLOCK_SIZE, SCREEN_HEIGHT - BLOCK_SIZE * 3, TYPE_STONE)
        group.add(b)
    c6 = Block(SCREEN_WIDTH // 2, SCREEN_HEIGHT - BLOCK_SIZE * 4, TYPE_CANNON_SHIELD)
    group.add(c6)
    cannons.add(c6)
    
    return group, cannons


# --- UI ЭЛЕМЕНТЫ ---
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
    draw_background(surface, clouds, mountains)
    
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


# --- РЕДАКТОР ---
def run_editor(screen, clock, selected_map):
    tiles, cannons = load_map(selected_map) if selected_map else create_default_map()
    
    editor_mode = 1
    selected_cannon_type = 0
    
    cannon_options = list(CANNON_NAMES.values())
    cannon_dropdown = DropdownMenu(
        SCREEN_WIDTH - 200, 60, 180,
        cannon_options,
        {i: CANNON_COLORS[CANNON_TYPES[i]] for i in range(len(CANNON_TYPES))}
    )
    
    input_box = InputBox(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 25, 300, 50)
    show_save_dialog = False
    
    # Для непрерывного рисования
    mouse_held = False
    last_placed_pos = None
    
    clouds = [Cloud() for _ in range(5)]
    mountains = [
        BackgroundMountain(100, 150, (100, 100, 120)),
        BackgroundMountain(400, 200, (80, 80, 100)),
        BackgroundMountain(700, 170, (90, 90, 110)),
        BackgroundMountain(1000, 190, (85, 85, 105)),
    ]
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            
            if show_save_dialog:
                result = input_box.handle_event(event)
                if result:
                    save_map(tiles, result)
                    show_save_dialog = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    show_save_dialog = False
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    show_save_dialog = True
                    input_box.text = selected_map if selected_map else "new_map"
                    input_box.active = True
                if event.key == pygame.K_1:
                    editor_mode = 0
                    cannon_dropdown.is_open = False
                if event.key == pygame.K_2:
                    editor_mode = 1
                    cannon_dropdown.is_open = False
                if event.key == pygame.K_3:
                    editor_mode = 2
                if event.key == pygame.K_4:
                    editor_mode = 3
                    cannon_dropdown.is_open = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if editor_mode == 2 and cannon_dropdown.handle_click(mouse_pos):
                    selected_cannon_type = cannon_dropdown.get_selected_value()
                    continue
                
                if event.button == 1:
                    mouse_held = True
                    last_placed_pos = None
                elif event.button == 3:
                    mouse_held = True
                    last_placed_pos = None
            
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_held = False
                last_placed_pos = None
        
        # Непрерывное рисование при зажатой кнопке мыши
        if mouse_held and not show_save_dialog and mouse_pos[1] > 100:
            gx = (mouse_pos[0] // BLOCK_SIZE) * BLOCK_SIZE
            gy = (mouse_pos[1] // BLOCK_SIZE) * BLOCK_SIZE
            current_pos = (gx, gy)
            
            # Проверяем, что мы не рисуем в том же месте
            if current_pos != last_placed_pos:
                last_placed_pos = current_pos
                
                if mouse_buttons[0]:  # ЛКМ
                    if editor_mode == 3:  # Удаление
                        for b in list(tiles):
                            if b.rect.collidepoint(mouse_pos):
                                if b in cannons:
                                    cannons.remove(b)
                                b.kill()
                    elif editor_mode in [0, 1]:  # Ground или Stone - непрерывное рисование
                        # Удаляем существующий блок
                        for b in list(tiles):
                            if b.rect.topleft == (gx, gy):
                                if b in cannons:
                                    cannons.remove(b)
                                b.kill()
                        
                        block_type = TYPE_GROUND if editor_mode == 0 else TYPE_STONE
                        new_b = Block(gx, gy, block_type)
                        tiles.add(new_b)
                    
                    elif editor_mode == 2:  # Пушки - только по клику
                        pass  # Пушки ставятся только по одиночному клику
                
                elif mouse_buttons[2]:  # ПКМ - удаление
                    for b in list(tiles):
                        if b.rect.collidepoint(mouse_pos):
                            if b in cannons:
                                cannons.remove(b)
                            b.kill()
        
        # Одиночный клик для пушек
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            if event.button == 1 and editor_mode == 2 and not show_save_dialog and mouse_pos[1] > 100:
                gx = (mouse_pos[0] // BLOCK_SIZE) * BLOCK_SIZE
                gy = (mouse_pos[1] // BLOCK_SIZE) * BLOCK_SIZE
                
                # Удаляем существующий блок
                for b in list(tiles):
                    if b.rect.topleft == (gx, gy):
                        if b in cannons:
                            cannons.remove(b)
                        b.kill()
                
                block_type = CANNON_TYPES[selected_cannon_type]
                new_b = Block(gx, gy, block_type)
                tiles.add(new_b)
                cannons.add(new_b)
        
        # Отрисовка
        draw_background(screen, clouds, mountains)
        tiles.draw(screen)
        
        for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
            pygame.draw.line(screen, (100, 100, 100, 50), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
            pygame.draw.line(screen, (100, 100, 100, 50), (0, y), (SCREEN_WIDTH, y))
        
        if mouse_pos[1] > 100:
            gx = (mouse_pos[0] // BLOCK_SIZE) * BLOCK_SIZE
            gy = (mouse_pos[1] // BLOCK_SIZE) * BLOCK_SIZE
            
            if editor_mode == 0:
                cursor_color = GREEN
            elif editor_mode == 1:
                cursor_color = GRAY
            elif editor_mode == 2:
                cursor_color = CANNON_COLORS[CANNON_TYPES[selected_cannon_type]]
            else:
                cursor_color = RED
            
            if editor_mode == 3:
                pygame.draw.line(screen, RED, (gx + 5, gy + 5), (gx + BLOCK_SIZE - 5, gy + BLOCK_SIZE - 5), 3)
                pygame.draw.line(screen, RED, (gx + BLOCK_SIZE - 5, gy + 5), (gx + 5, gy + BLOCK_SIZE - 5), 3)
            else:
                pygame.draw.rect(screen, cursor_color, (gx, gy, BLOCK_SIZE, BLOCK_SIZE), 3)
        
        ui_panel = pygame.Surface((SCREEN_WIDTH, 100), pygame.SRCALPHA)
        pygame.draw.rect(ui_panel, (0, 0, 0, 200), (0, 0, SCREEN_WIDTH, 100))
        screen.blit(ui_panel, (0, 0))
        
        modes = ["1: Ground", "2: Stone", "3: Cannon", "4: Delete"]
        mode_colors = [GREEN, GRAY, ORANGE, RED]
        
        for i, (mode_text, mode_color) in enumerate(zip(modes, mode_colors)):
            x_pos = 20 + i * 150
            is_selected = (i == editor_mode)
            
            btn_rect = pygame.Rect(x_pos, 10, 130, 35)
            pygame.draw.rect(screen, mode_color if is_selected else (60, 60, 80), btn_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE if is_selected else mode_color, btn_rect, 2, border_radius=5)
            
            text = font_small.render(mode_text, True, WHITE)
            screen.blit(text, (x_pos + 10, 18))
        
        if editor_mode == 2:
            cannon_label = font_small.render("Cannon type:", True, WHITE)
            screen.blit(cannon_label, (SCREEN_WIDTH - 200, 40))
            cannon_dropdown.draw(screen)
        
        info = font_small.render("Ctrl+S: Save | ESC: Exit | LMB: Place/Draw | RMB: Delete", True, (180, 180, 180))
        screen.blit(info, (20, 70))
        
        if show_save_dialog:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(screen, (50, 50, 70), (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 80, 360, 160), border_radius=15)
            pygame.draw.rect(screen, GOLD, (SCREEN_WIDTH//2 - 180, SCREEN_HEIGHT//2 - 80, 360, 160), 3, border_radius=15)
            
            save_title = font_medium.render("Save Map As:", True, WHITE)
            screen.blit(save_title, (SCREEN_WIDTH//2 - save_title.get_width()//2, SCREEN_HEIGHT//2 - 65))
            
            input_box.draw(screen)
            
            hint = font_small.render("Press Enter to save, ESC to cancel", True, (150, 150, 150))
            screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT//2 + 40))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    return None


# --- ОСНОВНОЙ ИГРОВОЙ ЦИКЛ ---
def run_game(screen, clock, selected_map):
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


# --- ГЛАВНАЯ ФУНКЦИЯ ---
def main():
    clouds = [Cloud() for _ in range(10)]
    mountains = [
        BackgroundMountain(0, 150, (100, 100, 120)),
        BackgroundMountain(200, 220, (80, 80, 100)),
        BackgroundMountain(450, 180, (90, 90, 110)),
        BackgroundMountain(700, 250, (75, 75, 95)),
        BackgroundMountain(950, 190, (85, 85, 105)),
    ]
    
    btn_play = Button(SCREEN_WIDTH//2 - 120, 220, 240, 50, "PLAY GAME", (50, 150, 50), (70, 200, 70))
    btn_editor = Button(SCREEN_WIDTH//2 - 120, 290, 240, 50, "MAP EDITOR", (50, 50, 150), (70, 70, 200))
    btn_quit = Button(SCREEN_WIDTH//2 - 120, 360, 240, 50, "QUIT", (150, 50, 50), (200, 70, 70))
    buttons = [btn_play, btn_editor, btn_quit]
    
    selected_map = None
    state = "MENU"
    
    running = True
    while running:
        map_list = get_map_list()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_play.is_clicked(mouse_pos, True):
                        result = run_game(screen, clock, selected_map)
                        if result == "QUIT":
                            running = False
                    elif btn_editor.is_clicked(mouse_pos, True):
                        run_editor(screen, clock, selected_map)
                    elif btn_quit.is_clicked(mouse_pos, True):
                        running = False
                    
                    for i, map_name in enumerate(map_list[:6]):
                        map_rect = pygame.Rect(SCREEN_WIDTH//2 - 130, 445 + i * 25, 260, 22)
                        if map_rect.collidepoint(mouse_pos):
                            selected_map = map_name
        
        if state == "MENU":
            for btn in buttons:
                btn.update(mouse_pos)
            draw_menu(screen, clouds, mountains, buttons, selected_map, map_list)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
