import pygame
import math
import random
from settings import *
from sprites import Block

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
    
    def get_neighbor_stones(self, block, tiles):
        """Возвращает соседние камни"""
        neighbors = []
        for b in tiles:
            if b.type == TYPE_STONE and b != block:
                dx = abs(b.rect.centerx - block.rect.centerx)
                dy = abs(b.rect.centery - block.rect.centery)
                if dx <= BLOCK_SIZE and dy <= BLOCK_SIZE:
                    neighbors.append(b)
        return neighbors
    
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
                neighbors = self.get_neighbor_stones(hit_block, tiles)
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