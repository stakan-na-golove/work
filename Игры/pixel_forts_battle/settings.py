import pygame
import os

# --- КОНСТАНТЫ И НАСТРОЙКИ ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
BLOCK_SIZE = 40
FPS = 60
MAPS_FOLDER = "maps"

# Создаём папку для карт
if not os.path.exists(MAPS_FOLDER):
    os.makedirs(MAPS_FOLDER)

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

# Шрифты
pygame.init()
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