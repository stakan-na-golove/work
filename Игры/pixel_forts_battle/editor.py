import pygame
import math
import random
from settings import *
from sprites import Block, Cloud, BackgroundMountain
from utils import draw_background, load_map, create_default_map, save_map
from ui import Button, DropdownMenu, InputBox

def run_editor(screen, clock, selected_map):
    from utils import load_map, create_default_map, save_map
    
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