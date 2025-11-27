import pygame
import json
import os
import math
import random
from settings import *
from sprites import Block, Cloud, BackgroundMountain

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
    from sprites import Block
    
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
    from sprites import Block
    
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