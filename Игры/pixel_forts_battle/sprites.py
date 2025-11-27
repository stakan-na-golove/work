import pygame
import math
import random
from settings import *

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
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, self.base_color, (10, 0, 20, 20))
        body_color = (int(self.base_color[0] * 0.7), int(self.base_color[1] * 0.7), int(self.base_color[2] * 0.7))
        pygame.draw.rect(self.image, body_color, (5, 20, 30, 20))
        pygame.draw.rect(self.image, self.base_color, (8, 22, 24, 16))
        pygame.draw.rect(self.image, (50, 50, 50), (10, 40, 8, 10))
        pygame.draw.rect(self.image, (50, 50, 50), (22, 40, 8, 10))
        pygame.draw.rect(self.image, (min(255, self.base_color[0]+30), min(255, self.base_color[1]+30), min(255, self.base_color[2]+30)), 
                         (12, 2, 16, 16))
        eye_x = 22 if self.facing_right else 12
        pygame.draw.rect(self.image, WHITE, (eye_x, 5, 6, 6))
        pygame.draw.rect(self.image, BLACK, (eye_x + 2 if self.facing_right else eye_x, 7, 2, 2))
    
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
        from projectiles import Projectile, BombProjectile, RicochetProjectile, SniperProjectile, ShieldProjectile
        
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
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = 0
        
        # Рисуем коробку
        self.image.fill(BROWN)
        pygame.draw.rect(self.image, (180, 100, 60), (2, 2, 26, 8))
        pygame.draw.rect(self.image, BLACK, (0, 0, 30, 30), 2)
        if box_type == BOX_AMMO:
            pygame.draw.rect(self.image, GOLD, (12, 10, 6, 12))
            pygame.draw.polygon(self.image, GOLD, [(12, 10), (18, 10), (15, 5)])
        elif box_type == BOX_HEALTH:
            pygame.draw.rect(self.image, RED, (13, 8, 4, 16))
            pygame.draw.rect(self.image, RED, (7, 14, 16, 4))
        elif box_type == BOX_GHOST:
            pygame.draw.ellipse(self.image, (200, 200, 255), (8, 8, 14, 12))
            pygame.draw.rect(self.image, (200, 200, 255), (8, 14, 14, 8))
            pygame.draw.circle(self.image, BLACK, (12, 12), 2)
            pygame.draw.circle(self.image, BLACK, (18, 12), 2)
        elif box_type == BOX_EXPLOSIVE:
            # Взрывной заряд - оранжевая звезда/взрыв
            pygame.draw.circle(self.image, ORANGE, (15, 15), 8)
            pygame.draw.circle(self.image, YELLOW, (15, 15), 5)
            # Лучи взрыва
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                x1 = 15 + math.cos(rad) * 6
                y1 = 15 + math.sin(rad) * 6
                x2 = 15 + math.cos(rad) * 10
                y2 = 15 + math.sin(rad) * 10
                pygame.draw.line(self.image, YELLOW, (x1, y1), (x2, y2), 2)
    
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