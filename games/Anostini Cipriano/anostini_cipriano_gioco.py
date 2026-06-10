import pygame
import math
import sys
import random

# 1. Inizializzazione di Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Giorgi Tower Defense")
clock = pygame.time.Clock()

# Colori (RGB)
DARK_GREY = (60, 60, 60)
WHITE = (255, 255, 255)
GREEN = (34, 177, 76)
LIGHT_GREEN = (50, 255, 100) # Verde più acceso per il testo con outline
RED = (237, 28, 36)
BLUE = (0, 162, 232)
LIGHT_BLUE = (100, 200, 255) 
PURPLE = (163, 73, 164)
BLACK = (0, 0, 0)
YELLOW = (255, 242, 0)
GOLD = (218, 165, 32)
GREY = (120, 120, 120)
DARK_GREEN = (20, 120, 50)
ORANGE_BOSS = (255, 140, 0)

# Stile Sfondo Scuola
SCHOOL_FLOOR = (230, 235, 240)  
GRID_COLOR = (215, 220, 225)    
PATH_COLOR = (100, 110, 120)    
DESK_WOOD = (212, 140, 70)      
UI_PANEL = (40, 50, 60)         

PATH = [(0, 300), (250, 300), (250, 150), (550, 150), (550, 450), (800, 450)]
PATH_THICKNESS = 40

# Nuova posizione della lavagna (Sotto il primo blocco del percorso, in mezzo al gioco)
BOARD_RECT = pygame.Rect(WIDTH // 2 - 100, 360, 200, 45)

# --- FUNZIONI DI UTILITÀ ---
def draw_text_with_outline(surface, text, font, col_main, col_outline, x, y):
    """Rende qualsiasi testo leggibile disegnando un contorno attorno ad esso"""
    text_surface = font.render(text, True, col_main)
    # Genera l'outline spostando il testo nero di 1 pixel nelle 4 direzioni cardinali
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        outline_surface = font.render(text, True, col_outline)
        surface.blit(outline_surface, (x + dx, y + dy))
    # Disegna il testo principale sopra il contorno
    surface.blit(text_surface, (x, y))

def dist_point_to_segment(p, a, b):
    ap = pygame.math.Vector2(p) - pygame.math.Vector2(a)
    ab = pygame.math.Vector2(b) - pygame.math.Vector2(a)
    ab_length_sq = ab.length_squared()
    if ab_length_sq == 0:
        return ap.length()
    t = max(0, min(1, ap.dot(ab) / ab_length_sq))
    closest_point = pygame.math.Vector2(a) + ab * t
    return (pygame.math.Vector2(p) - closest_point).length()

def is_on_path(pos, path, thickness):
    for i in range(len(path) - 1):
        if dist_point_to_segment(pos, path[i], path[i+1]) < thickness / 2 + 15:
            return True
    return False

def draw_coin(surface, x, y, font):
    pygame.draw.circle(surface, GOLD, (x, y), 10)
    pygame.draw.circle(surface, YELLOW, (x, y), 8)
    symbol = font.render("$", True, BLACK)
    surface.blit(symbol, (x - symbol.get_width() // 2, y - symbol.get_height() // 2))

def draw_skull(surface, x, y):
    pygame.draw.circle(surface, BLACK, (x, y), 14)
    pygame.draw.circle(surface, WHITE, (x, y), 12)
    pygame.draw.rect(surface, WHITE, (x - 6, y + 6, 12, 10))
    pygame.draw.line(surface, BLACK, (x - 3, y + 12), (x - 3, y + 16), 1)
    pygame.draw.line(surface, BLACK, (x + 3, y + 12), (x + 3, y + 16), 1)
    pygame.draw.circle(surface, BLACK, (x - 5, y - 1), 3)
    pygame.draw.circle(surface, BLACK, (x + 5, y - 1), 3)
    pygame.draw.polygon(surface, BLACK, [(x, y + 3), (x - 2, y + 6), (x + 2, y + 6)])

def draw_school_decorations(font_mini):
    # Rendering della griglia di sfondo (effetto quaderno)
    for x in range(0, WIDTH, 30):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 30):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

    # LAVAGNA SPOSTATA QUI: Ora centrata e posizionata sotto il percorso
    pygame.draw.rect(screen, BLACK, BOARD_RECT)
    pygame.draw.rect(screen, (20, 80, 40), (BOARD_RECT.x + 4, BOARD_RECT.y + 4, BOARD_RECT.width - 8, BOARD_RECT.height - 8))
    txt_board = font_mini.render("2 + 2 = 5?", True, WHITE)
    screen.blit(txt_board, (BOARD_RECT.x + (BOARD_RECT.width - txt_board.get_width()) // 2, BOARD_RECT.y + 14))

    # Disegno Banchi + Sedie
    for pos, voto_val in banchi_posic.items():
        bx, by = pos
        # Sedia davanti al banco
        pygame.draw.rect(screen, DARK_GREY, (bx + 10, by - 8, 15, 8))
        pygame.draw.rect(screen, BLACK, (bx + 8, by - 12, 19, 4))
        # Banco
        pygame.draw.rect(screen, BLACK, (bx, by, 35, 22), 2)
        pygame.draw.rect(screen, DESK_WOOD, (bx + 2, by + 2, 31, 18))
        voto_text = font_mini.render(voto_val, True, RED)
        screen.blit(voto_text, (bx + 12, by + 3))

# Funzione per disegnare il box dei comandi nei menu
def draw_controls_ui(surface, start_y, font_obj):
    box_rect = pygame.Rect(WIDTH // 2 - 200, start_y, 400, 110)
    pygame.draw.rect(surface, (30, 40, 50), box_rect, 0, 8)
    pygame.draw.rect(surface, YELLOW, box_rect, 2, 8)
    
    titolo = font_obj.render("--- COMANDI DI GIOCO ---", True, YELLOW)
    c1 = font_obj.render("[Click Sinistro] -> Seleziona / Piazza Torre", True, WHITE)
    c2 = font_obj.render("[Click Destro] -> Fai Upgrade alla Torre", True, WHITE)
    c3 = font_obj.render("[Clicca Rotellina] -> Vendi Torre (Recuperi 50%)", True, WHITE)
    c4 = font_obj.render("[Tasto E] -> Mostra Raggi  |  [SPAZIO] -> Velocità 5X", True, LIGHT_BLUE)
    
    surface.blit(titolo, (WIDTH // 2 - titolo.get_width() // 2, start_y + 10))
    surface.blit(c1, (WIDTH // 2 - c1.get_width() // 2, start_y + 32))
    surface.blit(c2, (WIDTH // 2 - c2.get_width() // 2, start_y + 50))
    surface.blit(c3, (WIDTH // 2 - c3.get_width() // 2, start_y + 68))
    surface.blit(c4, (WIDTH // 2 - c4.get_width() // 2, start_y + 88))

# --- GENERAZIONE BANCHI ---
banchi_posic = {}
voti_lista = ["3", "4", "2", "5"]
random.seed(42)

for riga in range(4):
    for colonna in range(6):
        bx = 60 + colonna * 120
        by = 100 + riga * 100
        too_close = False
        
        # Evita il percorso
        for i in range(len(PATH) - 1):
            if dist_point_to_segment((bx + 17, by + 11), PATH[i], PATH[i+1]) < PATH_THICKNESS + 25:
                too_close = True
                break
                
        # Evita la nuova posizione centrale della lavagna
        banco_rect = pygame.Rect(bx, by, 35, 22)
        if banco_rect.colliderect(BOARD_RECT.inflate(30, 30)):
            too_close = True
            
        if not too_close and by < HEIGHT - 90:
            banchi_posic[(bx, by)] = random.choice(voti_lista)

# --- CLASSI ---
class Enemy:
    def __init__(self, max_health, boss_type=0, name="Studente", is_sub=False, sub_type="", start_pos=None):
        self.path = PATH
        self.path_index = 0
        self.boss_type = boss_type
        self.name = name
        self.is_sub = is_sub
        self.sub_type = sub_type
        self.animation_timer = 0
        
        if start_pos:
            self.x, self.y = start_pos
            min_dist = float('inf')
            for idx, pt in enumerate(PATH):
                d = math.hypot(pt[0] - self.x, pt[1] - self.y)
                if d < min_dist:
                    min_dist = d
                    self.path_index = idx
        else:
            self.x, self.y = self.path[0]
            
        if self.boss_type == 5:     
            self.speed = 0.9
            self.radius = 24
            self.color = (45, 30, 20)
        elif self.boss_type == 10:  
            self.speed = 1.0
            self.radius = 24
            self.color = (230, 170, 140)
        elif self.boss_type == 15:  
            self.speed = 0.9
            self.radius = 24
            self.color = (240, 190, 160)
        elif self.boss_type == 20:  
            self.speed = 1.1
            self.radius = 24
            self.color = (235, 180, 150)
        elif self.boss_type == 25:  
            self.speed = 0.5            
            self.radius = 32            
            self.color = (220, 190, 160)
        else:
            self.speed = 1.8 if not is_sub else 2.2
            self.radius = 12 if not is_sub else 8
            self.color = RED
            
        self.max_health = max_health
        self.health = self.max_health

    def move(self, speed_multiplier):
        effective_speed = self.speed * speed_multiplier
        
        if self.path_index < len(self.path) - 1:
            target_x, target_y = self.path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)

            if distance < effective_speed:
                self.path_index += 1
                self.x, self.y = target_x, target_y
            else:
                self.x += (dx / distance) * effective_speed
                self.y += (dy / distance) * effective_speed

    def draw(self):
        self.animation_timer += 0.1
        cx, cy = int(self.x), int(self.y)
        
        if not self.is_sub:
            pygame.draw.circle(screen, self.color, (cx, cy), self.radius)
            if self.boss_type > 0:
                pygame.draw.circle(screen, BLACK, (cx, cy), self.radius, 2)
                
            if self.boss_type == 5: 
                for _ in range(3):
                    sx = cx + random.randint(-35, 35)
                    sy = cy + random.randint(-35, 35)
                    pygame.draw.line(screen, YELLOW, (cx, cy), (sx, sy), 2)
            elif self.boss_type == 10: 
                pygame.draw.circle(screen, (200, 90, 40), (cx, cy - 10), 12)
                for i in range(2):
                    ang = self.animation_timer + (i * math.pi)
                    bx = cx + int(36 * math.cos(ang))
                    by = cy + int(36 * math.sin(ang))
                    pygame.draw.rect(screen, BLUE, (bx - 5, by - 4, 10, 8))
            elif self.boss_type == 15: 
                pygame.draw.circle(screen, (240, 230, 140), (cx, cy - 10), 12)
                simboli = ["+", "-", "x", "√"]
                for i, sim in enumerate(simboli):
                    ang = self.animation_timer + (i * (math.pi / 2))
                    sx = cx + int(38 * math.cos(ang))
                    sy = cy + int(38 * math.sin(ang))
                    txt = font_ui.render(sim, True, BLACK)
                    screen.blit(txt, (sx - 3, sy - 5))
            elif self.boss_type == 20: 
                pygame.draw.circle(screen, BLACK, (cx, cy - 10), 12)
                ang1 = self.animation_timer
                pygame.draw.rect(screen, GREY, (cx + int(38 * math.cos(ang1)) - 6, cy + int(38 * math.sin(ang1)) - 4, 12, 8))
            elif self.boss_type == 25: 
                ang = -self.animation_timer
                pygame.draw.circle(screen, BLUE, (cx + int(42 * math.cos(ang)), cy + int(42 * math.sin(ang))), 5)
                pygame.draw.circle(screen, YELLOW, (cx + int(42 * math.cos(ang + math.pi)), cy + int(42 * math.sin(ang + math.pi))), 5)
                
            if self.boss_type > 0:
                # MODIFICA: Nome del boss visibile ovunque grazie all'outline ad alto contrasto
                lbl_dummy = font_ui.render(self.name, True, WHITE)
                tx = cx - lbl_dummy.get_width() // 2
                ty = cy - self.radius - 22
                draw_text_with_outline(screen, self.name, font_ui, WHITE, BLACK, tx, ty)
        else:
            if self.sub_type == "cavo":
                pygame.draw.line(screen, BLACK, (cx - 6, cy), (cx + 6, cy), 3)
            elif self.sub_type == "libro":
                pygame.draw.rect(screen, RED, (cx - 6, cy - 4, 12, 8))
            elif self.sub_type == "formula":
                # MODIFICA: Sotto-truppe con contorno per non perdersi sul grigio
                draw_text_with_outline(screen, "x=0", font_ui, YELLOW, BLACK, cx - 8, cy - 6)
            elif self.sub_type == "mouse_pc":
                pygame.draw.circle(screen, GREY, (cx, cy), 5)
            elif self.sub_type == "codice":
                # MODIFICA: Contorno anche per il testo codice python
                draw_text_with_outline(screen, "Py", font_ui, LIGHT_GREEN, BLACK, cx - 8, cy - 6)

        hb_width = 55 if self.boss_type > 0 else 24
        health_ratio = max(0, self.health / self.max_health)
        pygame.draw.rect(screen, RED, (self.x - hb_width//2, self.y - (self.radius + 8), hb_width, 4))
        pygame.draw.rect(screen, GREEN, (self.x - hb_width//2, self.y - (self.radius + 8), hb_width * health_ratio, 4))

class Tower:
    def __init__(self, x, y, tower_type):
        self.x = x
        self.y = y
        self.type = tower_type
        self.level = 1
        self.timer = 0
        self.creation_time = pygame.time.get_ticks()

        if self.type == "FIORITO": 
            self.base_cost = 50
            self.range = 130
            self.base_cooldown = 20
            self.base_damage = 10
            self.color = BLUE
        elif self.type == "LOPEZ": 
            self.base_cost = 80
            self.range = 95
            self.base_cooldown = 0
            self.base_damage = 0
            self.color = PURPLE
        elif self.type == "QUIRINO": 
            self.base_cost = 220     
            self.range = 170
            self.base_cooldown = 45
            self.base_damage = 70    
            self.color = BLACK

        self.total_invested = self.base_cost
        self.current_cooldown = self.base_cooldown
        self.current_damage = self.base_damage

    def get_upgrade_cost(self):
        if self.level == 1:
            return self.base_cost * 2  
        elif self.level == 2:
            return int(self.base_cost * 4) 
        return 0

    def upgrade(self):
        if self.level < 3:
            cost = self.get_upgrade_cost()
            self.level += 1
            self.total_invested += cost
            self.creation_time = pygame.time.get_ticks()

            if self.level == 2:
                if self.type != "LOPEZ":
                    self.base_cooldown = int(self.base_cooldown * 0.6)
                    self.base_damage = int(self.base_damage * 1.5)
            elif self.level == 3: 
                if self.type == "FIORITO":
                    self.range = 180
                    self.base_cooldown = int(self.base_cooldown * 0.7)
                    self.base_damage = 35
                elif self.type == "LOPEZ":
                    self.range = 140 
                elif self.type == "QUIRINO":
                    self.range = 220
                    self.base_cooldown = int(self.base_cooldown * 0.8)
                    self.base_damage = 180 

    def update_buffs(self, all_towers):
        self.current_damage = self.base_damage
        self.current_cooldown = self.base_cooldown

        if self.type == "LOPEZ": return

        for other in all_towers:
            if other.type == "LOPEZ":
                distance = math.hypot(other.x - self.x, other.y - self.y)
                if distance <= other.range:
                    multiplier = 1.2 if other.level == 1 else (1.5 if other.level == 2 else 2.0)
                    self.current_damage = int(self.current_damage * multiplier)
                    self.current_cooldown = max(1, int(self.current_cooldown / multiplier))

    def attack(self, enemies, bullets, speed_multiplier):
        if self.type == "LOPEZ": return

        if self.timer > 0:
            self.timer -= 1 * speed_multiplier
            return

        for enemy in enemies:
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance <= self.range:
                can_bounce = (self.type == "FIORITO" and self.level == 3)
                bullets.append(Bullet(self.x, self.y, enemy, self.current_damage, self.color, can_ricochet=can_bounce))
                self.timer = self.current_cooldown
                break

    def draw(self, font_ui, force_show_range=False):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 18)
        
        if self.level == 2:
            pygame.draw.circle(screen, YELLOW, (self.x, self.y), 18, 2)
        elif self.level == 3:
            pygame.draw.circle(screen, RED, (self.x, self.y), 18, 3)
            
        if force_show_range or (pygame.time.get_ticks() - self.creation_time <= 5000):
            r_color = (150, 70, 150) if self.type == "LOPEZ" else (100, 100, 100)
            pygame.draw.circle(screen, r_color, (self.x, self.y), self.range, 1)

        # IMPOSTAZIONE TESTO CON OUTLINE PER LE TORRI
        if self.level < 3:
            next_cost = self.get_upgrade_cost()
            text_str = f"Lvl {self.level} (+{next_cost}$)"
            lbl_dummy = font_ui.render(text_str, True, WHITE)
            tx = self.x - lbl_dummy.get_width() // 2
            ty = self.y - 34
            draw_text_with_outline(screen, text_str, font_ui, WHITE, BLACK, tx, ty)
        else:
            if self.type == "FIORITO":
                text_str = "Lvl 3 RICOCHET"
                lbl_dummy = font_ui.render(text_str, True, WHITE)
                tx = self.x - lbl_dummy.get_width() // 2
                ty = self.y - 34
                # MODIFICA: Ora RICOCHET usa un verde brillante ad alto contrasto con outline nera
                draw_text_with_outline(screen, text_str, font_ui, LIGHT_GREEN, BLACK, tx, ty)
            else:
                text_str = "Lvl 3 MAX"
                lbl_dummy = font_ui.render(text_str, True, WHITE)
                tx = self.x - lbl_dummy.get_width() // 2
                ty = self.y - 34
                draw_text_with_outline(screen, text_str, font_ui, RED, BLACK, tx, ty)

class Bullet:
    def __init__(self, x, y, target, damage, color, can_ricochet=False, is_bounce=False):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 9
        self.damage = damage
        self.color = color
        self.active = True
        self.can_ricochet = can_ricochet
        self.is_bounce = is_bounce

    def move(self, enemies, speed_multiplier):
        if self.target not in enemies or self.target.health <= 0:
            self.active = False
            return

        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)

        effective_speed = self.speed * speed_multiplier

        if distance < effective_speed:
            self.target.health -= self.damage
            self.active = False
            
            if self.can_ricochet and not self.is_bounce:
                nearest_enemy = None
                min_dist = 80
                
                for e in enemies:
                    if e != self.target and e.health > 0:
                        d = math.hypot(e.x - self.target.x, e.y - self.target.y)
                        if d < min_dist:
                            min_dist = d
                            nearest_enemy = e
                
                if nearest_enemy:
                    reduced_damage = int(self.damage * 0.65)
                    bullets.append(Bullet(self.target.x, self.target.y, nearest_enemy, 
                                          reduced_damage, LIGHT_BLUE, can_ricochet=False, is_bounce=True))
        else:
            self.x += (dx / distance) * effective_speed
            self.y += (dy / distance) * effective_speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5 if not self.is_bounce else 4)

# --- STATO E VARIABILI ---
enemies = []
towers = []
bullets = []

gold = 600   
lives = 100  
game_speed = 1  

font = pygame.font.SysFont("Arial", 18)
font_ui = pygame.font.SysFont("Arial", 14)
title_font = pygame.font.SysFont("Arial", 40)
skeleton_font = pygame.font.SysFont("impact", 44)

game_state = "MENU"
selected_type = "FIORITO"

wave = 1
enemy_health_base = 35    
enemies_to_spawn = 5
enemies_spawned = 0
spawn_timer = 0
wave_break_timer = 0
in_wave_break = False

wave_text_timer = 240  
show_wave_text = True
show_all_ranges = False
sub_spawn_clock = 0

btn_start = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 75, 240, 50)
btn_resume = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 110, 200, 50)
btn_exit = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 45, 200, 50)

shop_y = HEIGHT - 75
icon_blue_rect = pygame.Rect(120, shop_y, 140, 60)
icon_purple_rect = pygame.Rect(330, shop_y, 140, 60)
icon_black_rect = pygame.Rect(540, shop_y, 140, 60)

# --- LOOP PRINCIPALE ---
running = True
while running:
    clock.tick(60)
    screen.fill(SCHOOL_FLOOR)

    if game_state == "MENU":
        screen.fill((50, 70, 85))
        title_text = title_font.render("GIORGI TOWER DEFENSE", True, YELLOW)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 5))
        
        pygame.draw.rect(screen, WHITE, btn_start, 0, 5)
        start_text = font.render("ENTRA IN CLASSE", True, BLACK)
        screen.blit(start_text, (btn_start.x + (btn_start.width - start_text.get_width()) // 2, btn_start.y + 13))
        
        draw_controls_ui(screen, HEIGHT // 2, font_ui)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_start.collidepoint(event.pos): game_state = "PLAYING"
        continue

    elif game_state == "PAUSE":
        screen.fill((40, 45, 50))
        pause_title = title_font.render("LEZIONE IN PAUSA", True, WHITE)
        screen.blit(pause_title, (WIDTH // 2 - pause_title.get_width() // 2, HEIGHT // 6))

        pygame.draw.rect(screen, BLUE, btn_resume)
        resume_text = font.render("RIPRENDI DIDATTICA", True, WHITE)
        screen.blit(resume_text, (btn_resume.x + (btn_resume.width - resume_text.get_width()) // 2, btn_resume.y + 13))

        pygame.draw.rect(screen, RED, btn_exit)
        exit_text = font.render("DISCONNETTITI", True, WHITE)
        screen.blit(exit_text, (btn_exit.x + (btn_exit.width - exit_text.get_width()) // 2, btn_exit.y + 13))
        
        draw_controls_ui(screen, HEIGHT // 2 + 80, font_ui)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: game_state = "PLAYING"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_resume.collidepoint(event.pos): game_state = "PLAYING"
                if btn_exit.collidepoint(event.pos): running = False
        continue

    elif game_state == "PLAYING":
        keys = pygame.key.get_pressed()
        show_all_ranges = keys[pygame.K_e]

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    game_state = "PAUSE"
                if event.key == pygame.K_SPACE:
                    game_speed = 5 if game_speed == 1 else 1
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                
                if event.button == 1: 
                    if icon_blue_rect.collidepoint((mx, my)):
                        selected_type = "FIORITO"
                    elif icon_purple_rect.collidepoint((mx, my)):
                        selected_type = "LOPEZ"
                    elif icon_black_rect.collidepoint((mx, my)):
                        selected_type = "QUIRINO"
                    else:
                        current_cost = 50 if selected_type == "FIORITO" else (80 if selected_type == "LOPEZ" else 220)
                        if my < shop_y - 10:
                            if gold >= current_cost:
                                on_path = is_on_path((mx, my), PATH, PATH_THICKNESS)
                                overlapping = False
                                for t in towers:
                                    if math.hypot(t.x - mx, t.y - my) < 35:
                                        overlapping = True
                                        break
                                for bx, by in banchi_posic.keys():
                                    if pygame.Rect(bx, by, 35, 22).collidepoint((mx, my)):
                                        overlapping = True
                                
                                if BOARD_RECT.collidepoint((mx, my)):
                                    overlapping = True
                                    
                                if not on_path and not overlapping:
                                    towers.append(Tower(mx, my, selected_type))
                                    gold -= current_cost

                elif event.button == 3:  
                    for t in towers:
                        if math.hypot(t.x - mx, t.y - my) <= 20 and t.level < 3:
                            upgrade_cost = t.get_upgrade_cost()
                            if gold >= upgrade_cost:
                                gold -= upgrade_cost
                                t.upgrade()
                            break

                elif event.button == 2:  
                    for t in towers:
                        if math.hypot(t.x - mx, t.y - my) <= 20:
                            gold += int(t.total_invested * 0.50)
                            towers.remove(t)
                            break

        if lives <= 0: game_state = "GAMEOVER"

        # --- LOGICA ONDATE ---
        if not in_wave_break:
            spawn_timer += 1 * game_speed
            sub_spawn_clock += 1 * game_speed
            
            boss_hp = enemy_health_base * 7.5
            
            if wave == 5 and enemies_spawned < 1 and spawn_timer >= 90:
                enemies.append(Enemy(max_health=int(boss_hp), boss_type=5, name="Dagnoko"))
                enemies_spawned += 1
            elif wave == 10 and enemies_spawned < 1 and spawn_timer >= 90: 
                enemies.append(Enemy(max_health=int(boss_hp), boss_type=10, name="Trioschi"))
                enemies_spawned += 1
            elif wave == 15 and enemies_spawned < 1 and spawn_timer >= 90:
                enemies.append(Enemy(max_health=int(boss_hp), boss_type=15, name="Cascone"))
                enemies_spawned += 1
            elif wave == 20 and enemies_spawned < 1 and spawn_timer >= 90:
                enemies.append(Enemy(max_health=int(boss_hp), boss_type=20, name="Mattana"))
                enemies_spawned += 1
            elif wave == 25 and enemies_spawned < 1 and spawn_timer >= 90:
                enemies.append(Enemy(max_health=int(boss_hp * 1.5), boss_type=25, name="Musci"))
                enemies_spawned += 1
            elif wave not in [5, 10, 15, 20, 25]:
                if spawn_timer >= 90 and enemies_spawned < enemies_to_spawn:
                    enemies.append(Enemy(max_health=enemy_health_base, boss_type=0))
                    enemies_spawned += 1
                    spawn_timer = 0
                    
            if sub_spawn_clock >= 90:
                for enemy in enemies[:]:
                    if not enemy.is_sub and enemy.boss_type > 0:
                        sub_hp = int(enemy_health_base * 0.4)
                        if enemy.name == "Dagnoko":
                            enemies.append(Enemy(sub_hp, is_sub=True, sub_type="cavo", start_pos=(enemy.x, enemy.y)))
                        elif enemy.name == "Trioschi":
                            enemies.append(Enemy(sub_hp, is_sub=True, sub_type="libro", start_pos=(enemy.x, enemy.y)))
                        elif enemy.name == "Cascone":
                            enemies.append(Enemy(sub_hp, is_sub=True, sub_type="formula", start_pos=(enemy.x, enemy.y)))
                        elif enemy.name == "Mattana":
                            enemies.append(Enemy(sub_hp, is_sub=True, sub_type="mouse_pc", start_pos=(enemy.x, enemy.y)))
                        elif enemy.name == "Musci":
                            enemies.append(Enemy(sub_hp, is_sub=True, sub_type="codice", start_pos=(enemy.x, enemy.y)))
                sub_spawn_clock = 0
            
            target_spawn = 1 if (wave in [5, 10, 15, 20, 25]) else enemies_to_spawn
            if enemies_spawned >= target_spawn and len(enemies) == 0:
                if wave == 25: game_state = "VICTORY"
                else:
                    in_wave_break = True
                    wave_break_timer = 0
        else:
            wave_break_timer += 1 * game_speed
            if wave_break_timer >= 240: 
                wave += 1
                enemy_health_base = int(enemy_health_base * 1.25)
                enemies_to_spawn += 1
                enemies_spawned = 0
                in_wave_break = False
                show_wave_text = True
                wave_text_timer = 240 

        if show_wave_text:
            wave_text_timer -= 1 * game_speed
            if wave_text_timer <= 0: show_wave_text = False

        # --- AGGIORNAMENTO ENTITÀ ---
        for enemy in enemies[:]:
            enemy.move(game_speed)
            if enemy.path_index >= len(PATH) - 1:
                lives -= 25 if (enemy.boss_type > 0 and not enemy.is_sub) else 4
                enemies.remove(enemy)
            elif enemy.health <= 0:
                if enemy.is_sub:
                    if enemy.sub_type == "cavo": gold += random.randint(2, 4)
                    elif enemy.sub_type == "libro": gold += random.randint(3, 6)
                    elif enemy.sub_type == "formula": gold += random.randint(5, 8)
                    elif enemy.sub_type == "mouse_pc": gold += random.randint(6, 10)
                    elif enemy.sub_type == "codice": gold += random.randint(8, 14)
                else:
                    if enemy.boss_type == 5: gold += 50
                    elif enemy.boss_type == 10: gold += 80
                    elif enemy.boss_type == 15: 
                        gold += 120
                        for _ in range(6):
                            enemies.append(Enemy(int(enemy_health_base*0.4), is_sub=True, sub_type="formula", start_pos=(enemy.x + random.randint(-15, 15), enemy.y + random.randint(-15, 15))))
                    elif enemy.boss_type == 20: 
                        gold += 180
                        for _ in range(6):
                            enemies.append(Enemy(int(enemy_health_base*0.4), is_sub=True, sub_type="mouse_pc", start_pos=(enemy.x + random.randint(-15, 15), enemy.y + random.randint(-15, 15))))
                    elif enemy.boss_type == 25: game_state = "VICTORY"
                    else: gold += 12
                enemies.remove(enemy)

        for tower in towers:
            tower.update_buffs(towers)
            tower.attack(enemies, bullets, game_speed)

        for bullet in bullets[:]:
            bullet.move(enemies, game_speed)
            if not bullet.active: bullets.remove(bullet)

        # --- RENDERING GRAFICA ---
        draw_school_decorations(font_ui)
        
        pygame.draw.lines(screen, BLACK, False, PATH, PATH_THICKNESS + 4) 
        pygame.draw.lines(screen, PATH_COLOR, False, PATH, PATH_THICKNESS)     

        for enemy in enemies: enemy.draw()
        for tower in towers: tower.draw(font_ui, force_show_range=show_all_ranges)
        for bullet in bullets: bullet.draw()

        if show_wave_text:
            if wave == 5: text_str = "BOSS: PROF DAGNOKO"
            elif wave == 10: text_str = "BOSS: PROF TRIOSCHI"
            elif wave == 15: text_str = "BOSS: PROF CASCONE"
            elif wave == 20: text_str = "BOSS: PROF MATTANA"
            elif wave == 25: text_str = "ULTIMO ESAME: PROF MUSCI"
            else: text_str = f"ONDATA {wave}"
            
            ui_wave = skeleton_font.render(text_str, True, BLACK)
            total_width = ui_wave.get_width() + 40
            start_x = WIDTH // 2 - total_width // 2
            draw_skull(screen, start_x + 15, 65)
            screen.blit(ui_wave, (start_x + 45, 45))

        # Barra dello Shop inferiore
        pygame.draw.rect(screen, UI_PANEL, (0, shop_y - 10, WIDTH, HEIGHT - shop_y + 10))
        pygame.draw.line(screen, BLACK, (0, shop_y - 10), (WIDTH, shop_y - 10), 3)

        # Menu shop
        blue_bg = DARK_GREY if selected_type == "FIORITO" else WHITE
        text_color = WHITE if selected_type == "FIORITO" else BLACK
        pygame.draw.rect(screen, blue_bg, icon_blue_rect, 0, 5)
        pygame.draw.circle(screen, BLUE, (icon_blue_rect.x + 20, icon_blue_rect.y + 30), 12)
        lbl_blue = font_ui.render("Fiorito (50$)", True, text_color)
        screen.blit(lbl_blue, (icon_blue_rect.x + 40, icon_blue_rect.y + 22))

        purple_bg = DARK_GREY if selected_type == "LOPEZ" else WHITE
        text_color = WHITE if selected_type == "LOPEZ" else BLACK
        pygame.draw.rect(screen, purple_bg, icon_purple_rect, 0, 5)
        pygame.draw.circle(screen, PURPLE, (icon_purple_rect.x + 20, icon_purple_rect.y + 30), 12)
        lbl_purple = font_ui.render("Lopez (80$)", True, text_color)
        screen.blit(lbl_purple, (icon_purple_rect.x + 40, icon_purple_rect.y + 22))

        black_bg = DARK_GREY if selected_type == "QUIRINO" else WHITE
        text_color = WHITE if selected_type == "QUIRINO" else BLACK
        pygame.draw.rect(screen, black_bg, icon_black_rect, 0, 5)
        pygame.draw.circle(screen, BLACK, (icon_black_rect.x + 20, icon_black_rect.y + 30), 12)
        lbl_black = font_ui.render("Quirino (220$)", True, text_color)
        screen.blit(lbl_black, (icon_black_rect.x + 40, icon_black_rect.y + 22))

        # --- STATISTICHE IN ALTO ---
        lbl_gold_val = font.render(f"{gold}", True, BLACK)
        screen.blit(lbl_gold_val, (15, 12))
        draw_coin(screen, 15 + lbl_gold_val.get_width() + 15, 22, font_ui)
        
        speed_text_str = "Velocità: 5X 🔥 [SPAZIO]" if game_speed == 5 else "Velocità: 1X [SPAZIO]"
        ui_speed = font.render(speed_text_str, True, ORANGE_BOSS if game_speed == 5 else DARK_GREY)
        screen.blit(ui_speed, (15 + lbl_gold_val.get_width() + 50, 12))
        
        ui_lives = font.render(f"Integrità Scuola: {lives}/100", True, RED if lives <= 30 else BLACK)
        screen.blit(ui_lives, (620, 12))

        pygame.display.flip()

    elif game_state == "GAMEOVER":
        screen.fill(BLACK)
        over_text = title_font.render("BOCCIATO!", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

    elif game_state == "VICTORY":
        screen.fill((25, 55, 30))
        vic_text = title_font.render("PROMOSSO! MATURITÀ SUPERATA!", True, GREEN)
        screen.blit(vic_text, (WIDTH // 2 - vic_text.get_width() // 2, HEIGHT // 2 - 20))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

pygame.quit()
sys.exit()
