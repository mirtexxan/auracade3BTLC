import pygame
import sys
import math
import random
import array

# Inizializzazione di Pygame e del comparto Audio
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# Finestra di gioco
WIDTH, HEIGHT = 800, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Escape From Musci - Definitive Edition")
clock = pygame.time.Clock()

# --- GENERATORE DI SUONI RETRO PROCEDURALI (Senza file esterni) ---
def generate_sound(sound_type):
    sample_rate = 22050
    duration = 0.1 if sound_type == "shoot" else (0.15 if sound_type == "hit" else 0.4)
    num_samples = int(sample_rate * duration)
    buf = array.array('h', [0] * num_samples)
    
    for i in range(num_samples):
        t = float(i) / sample_rate
        if sound_type == "shoot":
            # Frequenza che sale rapidamente (Laser beep)
            freq = 400 + (t * 2000)
            v = math.sin(2 * math.pi * freq * t)
        elif sound_type == "hit":
            # Rumore metallico corto
            freq = 150 + random.randint(-30, 30)
            v = math.sin(2 * math.pi * freq * t) * random.choice([-1, 1])
        else: # "death"
            # Frequenza che scende con distorsione (Splat/Explosion)
            freq = max(40, 300 - (t * 800))
            v = (math.sin(2 * math.pi * freq * t) + random.uniform(-0.5, 0.5)) / 1.5
            
        # Volume decrescente (Fade out)
        v *= (1.0 - (float(i) / num_samples))
        buf[i] = int(v * 16384)
        
    return pygame.mixer.Sound(buffer=buf)

# Creazione effetti sonori
snd_shoot = generate_sound("shoot")
snd_hit = generate_sound("hit")
snd_death = generate_sound("death")

# --- DEFINIZIONE COLORI ---
ROAD_COLOR = (44, 62, 80)
GRASS_START = (39, 174, 96)
GRASS_END = (46, 204, 113)
WHITE = (255, 255, 255)
BLACK = (19, 19, 19)
MENU_BG = (52, 73, 94)
TEXT_CODE_COLOR = (46, 204, 113) 

BIOMES = [
    {"bg": (20, 20, 30), "side": (39, 174, 96), "name": "Laboratorio Standard"},
    {"bg": (15, 32, 67), "side": (41, 128, 185), "name": "Server Room Crio"},
    {"bg": (44, 53, 57), "side": (230, 126, 34), "name": "Mainframe del Fuoco"}
]
current_biome_idx = 0

BTN_GREEN = (46, 204, 113)
BTN_GREEN_HOVER = (39, 174, 96)
BTN_RED = (231, 76, 60)
BTN_RED_HOVER = (192, 41, 43)

# Stati del Gioco
game_state = "MENU"
test_difficulty = "EASY" 
player_name = ""  

# Dati di gioco
voto = 0
lives = 3
player_death_timer = 0  

# Configurazione Protagonista originale e modificatori Power-up
player_radius = 18
player_x = 400
player_y = 660
base_speed = 4
player_speed = base_speed

# Sistema Power-up
coffee_timer = 0  # Velocità aumentata
shield_active = False # Scudo protettivo attivo
powerups = [] # Lista dei powerup attivi a schermo

# Sistema di Particelle ed effetti visivi complessi
particles = []
damage_popups = [] 
player_trail = [] # Effetto scia per il caffè

# Fucile e Boss
shoot_cooldown = 0
boss_phase = 1
revive_timer = 0

# Configurazione Ostacoli Livello 1 (Macchine)
cars = []
lane_ys = [100, 160, 220, 280, 340, 400, 460, 520]
car_colors = [(231, 76, 60), (52, 152, 219), (241, 196, 148), (155, 89, 182)]
for y in lane_ys:
    speed = random.choice([-4, -3, 3, 4])
    cars.append({"x": random.randint(0, WIDTH), "y": y, "w": 80, "h": 35, "speed": speed, "color": random.choice(car_colors)})

# Configurazione Ostacoli Livello 2 (Codici Python)
python_snippets = ["while True:", "print('COPIATO!')", "import os", "sys.exit()", "SyntaxError", "def __init__:", "try:", "except Exception:", "x = None"]
lvl2_codes = []
for i in range(7):
    y = 120 + i * 65
    lvl2_codes.append({"text": random.choice(python_snippets), "x": random.randint(0, WIDTH), "y": y, "speed": 3})

# Configurazione Boss (Prof. Musci)
musci = {"x": 400, "y": 80, "w": 110, "h": 110, "hp": 100, "speed": 5, "direction": 1}
player_bullets = []
boss_attacks = []
boss_attack_cooldown = 0

def spawn_powerup():
    """Genera casualmente un powerup nella zona centrale dei livelli."""
    p_type = random.choice(["COFFEE", "SHIELD"])
    px = random.randint(50, WIDTH - 50)
    py = random.randint(150, HEIGHT - 180)
    powerups.append({"x": px, "y": py, "type": p_type, "size": 15})

def trigger_particles(x, y, color, count=12, speed_range=(1, 4)):
    """Crea una fontana di particelle fisiche esplosive."""
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        spd = random.uniform(speed_range[0], speed_range[1])
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle) * spd,
            "vy": math.sin(angle) * spd,
            "color": color, "timer": random.randint(20, 45)
        })

def handle_player_damage():
    """Gestisce l'impatto del danno assorbito o letale (Spiaccicato)."""
    global shield_active, player_death_timer, lives
    if shield_active:
        shield_active = False
        trigger_particles(player_x, player_y, (241, 196, 15), count=25, speed_range=(2, 6))
        snd_hit.play()
    else:
        player_death_timer = 80  
        lives -= 1
        trigger_particles(player_x, player_y, (231, 76, 60), count=30, speed_range=(3, 7))
        snd_death.play()

def reset_player():
    global player_x, player_y, coffee_timer, player_speed
    player_x = 400
    coffee_timer = 0
    player_speed = base_speed
    player_trail.clear()
    if game_state in ["BOSS_FIGHT", "BOSS_REVIVE"]: player_y = 600
    else: player_y = 660

def set_lvl2_difficulty(difficulty):
    global test_difficulty
    test_difficulty = difficulty
    for code_obj in lvl2_codes:
        code_obj["speed"] = random.choice([-7, -5, 5, 7]) if difficulty == "HARD" else random.choice([-4, -3, 3, 4])

# Font
font_ui = pygame.font.SysFont("Courier New", 20, bold=True)
font_story = pygame.font.SysFont("Arial", 22, italic=True)
font_title = pygame.font.SysFont("Arial", 36, bold=True)
font_code_bullet = pygame.font.SysFont("Courier New", 14, bold=True)
font_alert = pygame.font.SysFont("Arial", 24, bold=True)
font_name_tag = pygame.font.SysFont("Arial", 12, bold=True)

# Rettangoli Bottoni
btn_scuola_rect = pygame.Rect(150, 520, 220, 60)
btn_balza_rect = pygame.Rect(430, 520, 220, 60)
btn_inizia_rect = pygame.Rect(290, 420, 220, 60)
btn_punta_10_rect = pygame.Rect(130, 420, 250, 60)
btn_tenta_6_rect = pygame.Rect(440, 420, 250, 60)

# --- GAME LOOP ---
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    if shoot_cooldown > 0: shoot_cooldown -= 1
    if boss_attack_cooldown > 0: boss_attack_cooldown -= 1
    
    # Aggiornamento Timers di Stato
    if coffee_timer > 0:
        coffee_timer -= 1
        player_speed = base_speed * 1.8
        if coffee_timer == 0: player_speed = base_speed
    if player_death_timer > 0:
        player_death_timer -= 1
        if player_death_timer == 0:
            if lives <= 0: game_state = "GAME_OVER"
            else: reset_player()

    # Logica particelle globali
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["timer"] -= 1
        if p["timer"] <= 0: particles.remove(p)

    # 1. GESTIONE EVENTI INPUT
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "MENU":
                if btn_scuola_rect.collidepoint(mouse_pos):
                    game_state = "NAME_INPUT"
                    player_name = "" 
                elif btn_balza_rect.collidepoint(mouse_pos):
                    running = False
            elif game_state == "ARRIVED_AT_SCHOOL":
                if btn_inizia_rect.collidepoint(mouse_pos): game_state = "CHOOSE_PATH"
            elif game_state == "CHOOSE_PATH":
                if btn_punta_10_rect.collidepoint(mouse_pos):
                    set_lvl2_difficulty("HARD")
                    game_state = "LVL2"
                    lives, voto = 3, 0
                    powerups.clear()
                    spawn_powerup()
                    reset_player()
                elif btn_tenta_6_rect.collidepoint(mouse_pos):
                    set_lvl2_difficulty("EASY")
                    game_state = "LVL2"
                    lives, voto = 3, 0
                    powerups.clear()
                    spawn_powerup()
                    reset_player()
            elif game_state == "BOSS_INTRO":
                game_state = "BOSS_FIGHT"
                boss_phase = 1
                musci["hp"] = 100 
                musci["x"], musci["y"] = 400, 80
                lives = 3
                player_bullets.clear()
                boss_attacks.clear()
                damage_popups.clear()
                reset_player()
            elif game_state == "BOSS_FIGHT" and shoot_cooldown == 0 and player_death_timer == 0:
                dx = mouse_pos[0] - player_x
                dy = mouse_pos[1] - player_y
                distance = math.sqrt(dx**2 + dy**2)
                if distance > 0:
                    vx = (dx / distance) * 10
                    vy = (dy / distance) * 10
                    bullet_text = random.choice(["del musci", "musci.hp -= 10", "import win", "kill -9"])
                    player_bullets.append({"x": player_x, "y": player_y, "vx": vx, "vy": vy, "text": bullet_text})
                    snd_shoot.play()
                    shoot_cooldown = 14

        if event.type == pygame.KEYDOWN and game_state == "NAME_INPUT":
            if event.key == pygame.K_RETURN and len(player_name.strip()) > 0:
                game_state = "LVL1"
                lives, voto = 3, 0
                powerups.clear()
                spawn_powerup()
                reset_player()
            elif event.key == pygame.K_BACKSPACE: player_name = player_name[:-1]
            else:
                if len(player_name) < 14 and (event.unicode.isalnum() or event.unicode == " "):
                    player_name += event.unicode

    # 2. LOGICA MOVEMENT & LOOP LIVELLI
    keys = pygame.key.get_pressed()
    
    if game_state in ["LVL1", "LVL2", "BOSS_FIGHT"] and player_death_timer == 0:
        if keys[pygame.K_UP] or keys[pygame.K_w]: player_y -= player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player_y += player_speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player_x -= player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player_x += player_speed

        # Confini finestra
        if player_x - player_radius < 0: player_x = player_radius
        if player_x + player_radius > WIDTH: player_x = WIDTH - player_radius
        if player_y - player_radius < 54: player_y = 54
        if player_y + player_radius > HEIGHT: player_y = HEIGHT - player_radius

        # Logica Effetto Scia del Caffè
        if coffee_timer > 0 and (pygame.time.get_ticks() % 3 == 0):
            player_trail.append({"x": player_x, "y": player_y, "alpha": 180})
            
    for t in player_trail[:]:
        t["alpha"] -= 10
        if t["alpha"] <= 0: player_trail.remove(t)

    player_rect = pygame.Rect(player_x - player_radius, player_y - player_radius, player_radius * 2, player_radius * 2)

    # Collisioni e Raccolta Power-up (Valido per Livello 1 e Livello 2)
    if game_state in ["LVL1", "LVL2"] and player_death_timer == 0:
        for pw in powerups[:]:
            pw_rect = pygame.Rect(pw["x"] - pw["size"], pw["y"] - pw["size"], pw["size"] * 2, pw["size"] * 2)
            if player_rect.colliderect(pw_rect):
                if pw["type"] == "COFFEE": coffee_timer = 300  # 5 Secondi a 60 FPS
                elif pw["type"] == "SHIELD": shield_active = True
                trigger_particles(pw["x"], pw["y"], (241, 196, 15) if pw["type"] == "SHIELD" else (52, 152, 219), count=15)
                snd_hit.play()
                powerups.remove(pw)

    # LIVELLO 1
    if game_state == "LVL1":
        if player_y <= 58 and player_death_timer == 0:
            if keys[pygame.K_SPACE]: game_state = "ARRIVED_AT_SCHOOL"; reset_player()

        for car in cars:
            car["x"] += car["speed"]
            if car["speed"] > 0 and car["x"] > WIDTH: car["x"] = -car["w"]
            if car["speed"] < 0 and car["x"] < -car["w"]: car["x"] = WIDTH

            car_hitbox = pygame.Rect(car["x"] + 5, car["y"] + 2, car["w"] - 10, car["h"] - 4)
            if player_rect.colliderect(car_hitbox) and player_death_timer == 0:
                handle_player_damage()

    # LIVELLO 2
    elif game_state == "LVL2":
        if player_y <= 58 and player_death_timer == 0:
            if keys[pygame.K_SPACE]:
                player_y = 630 
                current_biome_idx = (current_biome_idx + 1) % len(BIOMES)
                powerups.clear()
                if random.random() < 0.75: spawn_powerup() # 75% di possibilità per stanza
                
                if test_difficulty == "EASY":
                    voto += 2
                    if voto >= 6: game_state = "VICTORY"
                else:
                    voto += 4
                    if voto > 10: voto = 10  
                    if voto >= 10: game_state = "BOSS_INTRO"; reset_player()

        for code_obj in lvl2_codes:
            code_obj["x"] += code_obj["speed"]
            if code_obj["speed"] > 0 and code_obj["x"] > WIDTH: code_obj["x"] = -100
            if code_obj["speed"] < 0 and code_obj["x"] < -100: code_obj["x"] = WIDTH

            text_surface = font_ui.render(code_obj["text"], True, TEXT_CODE_COLOR)
            code_rect = pygame.Rect(code_obj["x"], code_obj["y"], text_surface.get_width(), text_surface.get_height())

            if player_rect.colliderect(code_rect) and player_death_timer == 0:
                handle_player_damage()

    # BOSS FIGHT
    elif game_state == "BOSS_FIGHT":
        for popup in damage_popups[:]:
            popup["y"] -= 1.5
            popup["timer"] -= 1
            if popup["timer"] <= 0: damage_popups.remove(popup)

        if boss_phase == 1:
            musci["x"] += musci["speed"] * musci["direction"]
            if musci["x"] <= 0 or musci["x"] + musci["w"] >= WIDTH: musci["direction"] *= -1

            if boss_attack_cooldown == 0:
                boss_attacks.append({"x": musci["x"] + musci["w"]//2, "y": musci["y"] + musci["h"], "vx": 0, "vy": 5, "text": "0"})
                boss_attack_cooldown = 30
        else:
            m_center_x = musci["x"] + musci["w"] // 2
            musci["x"] += (player_x - m_center_x) * 0.025
            musci["y"] = 110 + math.sin(pygame.time.get_ticks() * 0.003) * 25

            if boss_attack_cooldown == 0:
                combo = random.choice(["MIRATO", "SVENTAGLIATA"])
                bx, by = musci["x"] + musci["w"] // 2, musci["y"] + musci["h"]
                
                if combo == "MIRATO":
                    dx, dy = player_x - bx, player_y - by
                    dist = math.sqrt(dx**2 + dy**2) or 1
                    boss_attacks.append({"x": bx, "y": by, "vx": (dx/dist)*4, "vy": (dy/dist)*4, "text": "1"})
                elif combo == "SVENTAGLIATA":
                    boss_attacks.append({"x": bx, "y": by, "vx": -2, "vy": 3.5, "text": "0"})
                    boss_attacks.append({"x": bx, "y": by, "vx": 2, "vy": 3.5, "text": "1"})
                boss_attack_cooldown = 35

        for atk in boss_attacks[:]:
            atk["x"] += atk["vx"]
            atk["y"] += atk["vy"]
            atk_rect = pygame.Rect(atk["x"], atk["y"], 20, 25)
            
            if player_rect.colliderect(atk_rect) and player_death_timer == 0:
                handle_player_damage()
                boss_attacks.remove(atk)
            elif atk["y"] > HEIGHT or atk["x"] < 0 or atk["x"] > WIDTH:
                if atk in boss_attacks: boss_attacks.remove(atk)

        if player_death_timer == 0:
            for b in player_bullets[:]:
                b["x"] += b["vx"]
                b["y"] += b["vy"]
                b_rect = pygame.Rect(b["x"], b["y"], 15, 15)
                
                musci_rect = pygame.Rect(musci["x"], musci["y"], musci["w"], musci["h"])
                if musci_rect.colliderect(b_rect):
                    musci["hp"] -= 10
                    damage_popups.append({"x": b["x"], "y": b["y"] - 10, "timer": 40})
                    trigger_particles(b["x"], b["y"], (46, 204, 113), count=6, speed_range=(1, 3))
                    snd_hit.play()
                    player_bullets.remove(b)
                    
                    if musci["hp"] <= 0:
                        if boss_phase == 1:
                            game_state = "BOSS_REVIVE"
                            revive_timer = 140 
                            player_bullets.clear()
                            boss_attacks.clear()
                        else: game_state = "VICTORY"
                    continue
                
                # Scontro colpi contro proiettili del boss
                hit_enemy_projectile = False
                for atk in boss_attacks[:]:
                    atk_rect = pygame.Rect(atk["x"], atk["y"], 20, 25)
                    if b_rect.colliderect(atk_rect):
                        trigger_particles(atk["x"], atk["y"], (241, 196, 15), count=4)
                        boss_attacks.remove(atk)
                        hit_enemy_projectile = True
                        break 
                
                if hit_enemy_projectile: player_bullets.remove(b); continue 
                if b["x"] < 0 or b["x"] > WIDTH or b["y"] < 0 or b["y"] > HEIGHT:
                    if b in player_bullets: player_bullets.remove(b)
        else: player_bullets.clear()

    elif game_state == "BOSS_REVIVE":
        revive_timer -= 1
        if revive_timer <= 0:
            boss_phase = 2
            musci["hp"] = 150 
            lives = 3         
            game_state = "BOSS_FIGHT"
            reset_player()

    elif game_state == "VICTORY" and keys[pygame.K_SPACE]:
        pygame.time.wait(200); game_state = "MENU"

    # 3. ENGINE RENDERING GRAFICO
    def draw_custom_player(surface, x, y, mouse_pos, state):
        if player_death_timer > 0:
            pygame.draw.ellipse(surface, (231, 76, 60), (int(x - 26), int(y + 6), 52, 10))
            pygame.draw.ellipse(surface, (52, 152, 219), (int(x - 24), int(y + 2), 48, 12))
            pygame.draw.ellipse(surface, (255, 219, 172), (int(x - 16), int(y - 4), 32, 10))
            pygame.draw.ellipse(surface, (110, 64, 32), (int(x - 16), int(y - 7), 32, 6))
            if (pygame.time.get_ticks() // 200) % 2 == 0:  
                txt_perso = font_alert.render("HAI PERSO UNA VITA!", True, (231, 76, 60))
                surface.blit(txt_perso, (int(x - txt_perso.get_width() // 2), int(y - 45)))
            return 

        # Rendering Scie di Movimento del Caffè
        for trail in player_trail:
            t_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(t_surf, (52, 152, 219, trail["alpha"]), (15, 15), player_radius - 4)
            surface.blit(t_surf, (int(trail["x"] - 15), int(trail["y"] - 15)))

        # Corpo Vivo Normale
        pygame.draw.rect(surface, (44, 62, 80), (int(x - 10), int(y + 12), 8, 8))
        pygame.draw.rect(surface, (44, 62, 80), (int(x + 2), int(y + 12), 8, 8))
        pygame.draw.rect(surface, (52, 152, 219), (int(x - 15), int(y - 6), 30, 20), border_radius=4)
        pygame.draw.circle(surface, (255, 219, 172), (int(x), int(y - 14)), 11)
        pygame.draw.circle(surface, (110, 64, 32), (int(x), int(y - 20)), 8)
        pygame.draw.rect(surface, (110, 64, 32), (int(x - 10), int(y - 18), 20, 6))
        
        # Effetto Visivo Alone Scudo Dorato
        if shield_active:
            s_pulse = int(player_radius + 6 + math.sin(pygame.time.get_ticks() * 0.01) * 3)
            s_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, (241, 196, 15, 100), (30, 30), s_pulse, 3)
            surface.blit(s_surf, (int(x - 30), int(y - 30)))

        if player_name:
            name_tag = font_name_tag.render(player_name, True, WHITE)
            surface.blit(name_tag, (int(x - name_tag.get_width() // 2), int(y - 40)))

        if state == "BOSS_FIGHT":
            dx, dy = mouse_pos[0] - x, mouse_pos[1] - y
            angle = math.atan2(dy, dx)
            gun_len = 22
            gx, gy = x + math.cos(angle) * gun_len, (y - 2) + math.sin(angle) * gun_len
            pygame.draw.line(surface, (52, 73, 94), (int(x), int(y - 2)), (int(gx), int(gy)), 6) 
            pygame.draw.line(surface, (46, 204, 113), (int(x), int(y - 2)), (int(gx), int(gy)), 2) 

    def draw_custom_boss(surface, x, y, w, h, phase):
        jacket_color = (102, 51, 153) if phase == 1 else (145, 12, 32)
        pygame.draw.ellipse(surface, jacket_color, (int(x), int(y + h * 0.35), w, int(h * 0.65)))
        pygame.draw.polygon(surface, WHITE, [(int(x + w//2 - 12), int(y + h * 0.35)), (int(x + w//2 + 12), int(y + h * 0.35)), (int(x + w//2), int(y + h * 0.55))])
        pygame.draw.line(surface, (231, 76, 60), (int(x + w//2), int(y + h * 0.4)), (int(x + w//2), int(y + h * 0.55)), 3)
        hx, hy = int(x + w // 2), int(y + h * 0.3)
        pygame.draw.circle(surface, (255, 219, 172), (hx, hy), 26)
        
        # Pettinatura rimodellata Musci (Meno stempia sulla fronte + ciuffi laterali ribelli)
        pygame.draw.ellipse(surface, (84, 50, 26), (hx - 27, hy - 27, 54, 23)) 
        pygame.draw.ellipse(surface, (84, 50, 26), (hx - 30, hy - 22, 12, 16)) 
        pygame.draw.ellipse(surface, (84, 50, 26), (hx + 18, hy - 22, 12, 16)) 
        
        pygame.draw.circle(surface, (84, 50, 26), (hx, hy + 13), 16)
        pygame.draw.polygon(surface, (84, 50, 26), [(hx - 25, hy), (hx + 25, hy), (hx, hy + 28)])
        pygame.draw.circle(surface, (255, 219, 172), (hx, hy + 5), 6)
        eye_color = (0, 0, 0) if phase == 1 else (255, 0, 0) 
        pygame.draw.circle(surface, eye_color, (hx - 9, hy - 3), 4)
        pygame.draw.circle(surface, eye_color, (hx + 9, hy - 3), 4)
        pygame.draw.circle(surface, (30, 30, 30), (hx - 9, hy - 3), 8, 2)
        pygame.draw.circle(surface, (30, 30, 30), (hx + 9, hy - 3), 8, 2)
        pygame.draw.line(surface, (30, 30, 30), (hx - 2, hy - 3), (hx + 2, hy - 3), 2)

    def draw_powerups(surface):
        for pw in powerups:
            if pw["type"] == "COFFEE":
                pygame.draw.circle(surface, (139, 69, 19), (pw["x"], pw["y"]), pw["size"])
                pygame.draw.circle(surface, WHITE, (pw["x"] + 5, pw["y"] - 3), 4) # Tazzina
            elif pw["type"] == "SHIELD":
                pygame.draw.polygon(surface, (241, 196, 15), [
                    (pw["x"], pw["y"] - pw["size"]), (pw["x"] + pw["size"], pw["y"] - pw["size"]//2),
                    (pw["x"] + pw["size"]//2, pw["y"] + pw["size"]), (pw["x"] - pw["size"]//2, pw["y"] + pw["size"]),
                    (pw["x"] - pw["size"], pw["y"] - pw["size"]//2)
                ])

    # RENDERING INTERFACCE DI STATO
    if game_state == "MENU":
        screen.fill(MENU_BG)
        title = font_title.render("ESCAPE FROM MUSCI", True, (241, 196, 15))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        s1 = font_story.render("Oggi c'è la temibile verifica del Prof. Musci.", True, WHITE)
        s3 = font_story.render("Vuoi tentare l'avventura o dartela a gambe?", True, WHITE)
        screen.blit(s1, (WIDTH // 2 - s1.get_width() // 2, 240))
        screen.blit(s3, (WIDTH // 2 - s3.get_width() // 2, 300))
        p_green = BTN_GREEN_HOVER if btn_scuola_rect.collidepoint(mouse_pos) else BTN_GREEN
        p_red = BTN_RED_HOVER if btn_balza_rect.collidepoint(mouse_pos) else BTN_RED
        pygame.draw.rect(screen, p_green, btn_scuola_rect, border_radius=10)
        pygame.draw.rect(screen, p_red, btn_balza_rect, border_radius=10)
        t1, t2 = font_ui.render("VAI A SCUOLA", True, WHITE), font_ui.render("BALZA (Esci)", True, WHITE)
        screen.blit(t1, (btn_scuola_rect.x + (btn_scuola_rect.w//2 - t1.get_width()//2), btn_scuola_rect.y + 18))
        screen.blit(t2, (btn_balza_rect.x + (btn_balza_rect.w//2 - t2.get_width()//2), btn_balza_rect.y + 18))

    elif game_state == "NAME_INPUT":
        screen.fill((34, 49, 63))
        t_prompt = font_title.render("INSERISCI IL TUO NOME:", True, (241, 196, 15))
        screen.blit(t_prompt, (WIDTH//2 - t_prompt.get_width()//2, HEIGHT//2 - 120))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 220, HEIGHT//2 - 30, 440, 60), 3, border_radius=8)
        cursor = "_" if (pygame.time.get_ticks() // 400) % 2 == 0 else ""
        text_surf = font_title.render(player_name + cursor, True, TEXT_CODE_COLOR)
        screen.blit(text_surf, (WIDTH//2 - text_surf.get_width()//2, HEIGHT//2 - 16))
        t_help = font_story.render("Scrivi sulla tastiera e premi INVIO per iniziare", True, WHITE)
        screen.blit(t_help, (WIDTH//2 - t_help.get_width()//2, HEIGHT//2 + 70))

    elif game_state == "ARRIVED_AT_SCHOOL":
        screen.fill((44, 62, 80))
        title = font_title.render("SEI ARRIVATO A SCUOLA!", True, (46, 204, 113))
        info1 = font_story.render("Il cancello si chiude alle tue spalle.", True, WHITE)
        info2 = font_story.render("Il corridoio è silenzioso... la classe ti aspetta.", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(info1, (WIDTH // 2 - info1.get_width() // 2, 250))
        screen.blit(info2, (WIDTH // 2 - info2.get_width() // 2, 300))
        p_color = BTN_GREEN_HOVER if btn_inizia_rect.collidepoint(mouse_pos) else BTN_GREEN
        pygame.draw.rect(screen, p_color, btn_inizia_rect, border_radius=10)
        txt = font_ui.render("INIZIA VERIFICA", True, WHITE)
        screen.blit(txt, (btn_inizia_rect.x + (btn_inizia_rect.w//2 - txt.get_width()//2), btn_inizia_rect.y + 18))

    elif game_state == "CHOOSE_PATH":
        screen.fill((34, 49, 63))
        title = font_title.render("SCEGLI LA TUA STRATEGIA", True, (241, 196, 15))
        desc = font_story.render("Come vuoi affrontare la verifica del Prof. Musci?", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))
        screen.blit(desc, (WIDTH // 2 - desc.get_width() // 2, 240))
        p_10 = BTN_RED_HOVER if btn_punta_10_rect.collidepoint(mouse_pos) else BTN_RED
        p_6 = BTN_GREEN_HOVER if btn_tenta_6_rect.collidepoint(mouse_pos) else BTN_GREEN
        pygame.draw.rect(screen, p_10, btn_punta_10_rect, border_radius=10)
        pygame.draw.rect(screen, p_6, btn_tenta_6_rect, border_radius=10)
        t_10, t_6 = font_ui.render("PUNTA AL 10 (COPIANDO)", True, WHITE), font_ui.render("TENTA IL 6 (FORTUNA)", True, WHITE)
        screen.blit(t_10, (btn_punta_10_rect.x + (btn_punta_10_rect.w//2 - t_10.get_width()//2), btn_punta_10_rect.y + 18))
        screen.blit(t_6, (btn_tenta_6_rect.x + (btn_tenta_6_rect.w//2 - t_6.get_width()//2), btn_tenta_6_rect.y + 18))
        avviso1 = font_code_bullet.render("(Avanzamento continuo tra biomi + BOSS FIGHT)", True, (231, 76, 60))
        avviso2 = font_code_bullet.render("(Difficoltà normale, vittoria sicura)", True, (46, 204, 113))
        screen.blit(avviso1, (btn_punta_10_rect.x - 10, btn_punta_10_rect.y + 70))
        screen.blit(avviso2, (btn_tenta_6_rect.x + 15, btn_tenta_6_rect.y + 70))

    elif game_state == "LVL1":
        screen.fill(ROAD_COLOR)
        pygame.draw.rect(screen, GRASS_END, (0, 0, WIDTH, 60))
        pygame.draw.rect(screen, GRASS_START, (0, 640, WIDTH, 60))
        for y in lane_ys:
            for x in range(0, WIDTH, 50): pygame.draw.line(screen, WHITE, (x, y + 35), (x + 25, y + 35), 2)
        for car in cars: pygame.draw.rect(screen, car["color"], (car["x"], car["y"], car["w"], car["h"]), border_radius=4)
        
        draw_powerups(screen)
        draw_custom_player(screen, player_x, player_y, mouse_pos, game_state)
        for p in particles: pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), random.randint(2, 4))
        
        screen.blit(font_ui.render("ESCAPE FROM MUSCI | LINEA D'ARRIVO", True, WHITE), (20, 20))
        screen.blit(font_ui.render(f"VITE: {'X ' * lives}", True, (231, 76, 60)), (620, 20))
        if player_y <= 58 and player_death_timer == 0:
            pygame.draw.rect(screen, (0, 0, 0, 150), (WIDTH//2 - 200, HEIGHT//2 - 30, 400, 60), border_radius=8)
            lbl_space = font_alert.render("PREMI SPAZIO PER ENTRARE", True, (241, 196, 15))
            screen.blit(lbl_space, (WIDTH//2 - lbl_space.get_width()//2, HEIGHT//2 - 13))

    elif game_state == "LVL2":
        biome = BIOMES[current_biome_idx]
        screen.fill(biome["bg"])
        pygame.draw.rect(screen, biome["side"], (0, 0, WIDTH, 60))
        pygame.draw.rect(screen, biome["side"], (0, 640, WIDTH, 60))
        for code_obj in lvl2_codes:
            txt_surf = font_ui.render(code_obj["text"], True, TEXT_CODE_COLOR)
            screen.blit(txt_surf, (code_obj["x"], code_obj["y"]))
        
        draw_powerups(screen)
        draw_custom_player(screen, player_x, player_y, mouse_pos, game_state)
        for p in particles: pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), random.randint(2, 4))
        
        target_voto = "10" if test_difficulty == "HARD" else "6"
        screen.blit(font_ui.render(f"BIOMA: {biome['name']} | VOTO: {voto}/{target_voto}", True, WHITE), (20, 20))
        screen.blit(font_ui.render(f"VITE: {'X ' * lives}", True, (231, 76, 60)), (620, 20))
        if player_y <= 58 and player_death_timer == 0:
            pygame.draw.rect(screen, (0, 0, 0, 180), (WIDTH//2 - 230, HEIGHT//2 - 30, 460, 60), border_radius=8)
            lbl_space = font_alert.render("PREMI SPAZIO PER IL PROSSIMO LIVELLO", True, (46, 204, 113))
            screen.blit(lbl_space, (WIDTH//2 - lbl_space.get_width()//2, HEIGHT//2 - 13))

    elif game_state == "BOSS_INTRO":
        screen.fill(BLACK)
        txt_accusa = font_title.render("IL PROF. MUSCI TI ACCUSA!", True, (231, 76, 60))
        info1 = font_story.render(f"'{player_name.upper()}, HAI PRESO 10 MA HAI COPIATO PYTHON!'", True, WHITE)
        info2 = font_story.render("PRENDI IL FUCILE SPARA-CODICI E DIFENDITI", True, (241, 196, 15))
        info3 = font_story.render("Mira con il MOUSE e CLICCA per abbatterlo!", True, WHITE)
        info4 = font_ui.render("[ CLICCA COL MOUSE PER INIZIARE LA BATTAGLIA INFOCATA ]", True, (149, 165, 166))
        screen.blit(txt_accusa, (WIDTH//2 - txt_accusa.get_width()//2, 150))
        screen.blit(info1, (WIDTH//2 - info1.get_width()//2, 260))
        screen.blit(info2, (WIDTH//2 - info2.get_width()//2, 330))
        screen.blit(info3, (WIDTH//2 - info3.get_width()//2, 390))
        screen.blit(info4, (WIDTH//2 - info4.get_width()//2, 520))

    elif game_state == "BOSS_FIGHT":
        screen.fill((30, 30, 40))
        draw_custom_boss(screen, musci["x"], musci["y"], musci["w"], musci["h"], boss_phase)
        max_hp = 100 if boss_phase == 1 else 150
        pygame.draw.rect(screen, (192, 41, 43), (WIDTH//2 - 150, 20, 300, 20))
        if musci["hp"] > 0: pygame.draw.rect(screen, (46, 204, 113), (WIDTH//2 - 150, 20, int((musci["hp"] / max_hp) * 300), 20))
        lbl_hp = font_code_bullet.render(f"MUSCI HP: {musci['hp']}/{max_hp}", True, WHITE)
        screen.blit(lbl_hp, (WIDTH//2 - lbl_hp.get_width()//2, 23))

        draw_custom_player(screen, player_x, player_y, mouse_pos, game_state)
        for b in player_bullets:
            b_surf = font_code_bullet.render(b["text"], True, (52, 152, 219))
            screen.blit(b_surf, (b["x"], b["y"]))
        for atk in boss_attacks:
            color = (231, 76, 60) if atk["text"] == "0" else (241, 196, 15)
            num_surf = font_title.render(atk["text"], True, color)
            screen.blit(num_surf, (atk["x"], atk["y"]))
        for p in particles: pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), random.randint(2, 4))
        for popup in damage_popups:
            txt_dmg = font_code_bullet.render("-10", True, (46, 204, 113))
            screen.blit(txt_dmg, (popup["x"], popup["y"]))
        screen.blit(font_ui.render(f"VITE: {'X ' * lives}", True, (231, 76, 60)), (20, 20))

    elif game_state == "BOSS_REVIVE":
        screen.fill((15, 15, 25))
        pulse_text = abs(math.sin(revive_timer * 0.05))
        txt_an = font_title.render("COMPILAZIONE ERRORE IN CORSO...", True, (231, 76, 60))
        txt_an.set_alpha(int(pulse_text * 255))
        txt_sub = font_story.render("Il sistema si riavvia in modalità codice binario nativo.", True, WHITE)
        screen.blit(txt_an, (WIDTH//2 - txt_an.get_width()//2, HEIGHT//2 - 60))
        screen.blit(txt_sub, (WIDTH//2 - txt_sub.get_width()//2, HEIGHT//2 + 10))
        progress = (140 - revive_timer) / 140
        size = int(90 + progress * 20)
        draw_custom_boss(screen, WIDTH//2 - size//2, HEIGHT//2 + 80, size, size, phase=2)

    elif game_state == "GAME_OVER":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)); screen.blit(overlay, (0, 0))
        go_t = font_title.render("BOCCIATO / GAME OVER", True, (231, 76, 60))
        go_s = font_story.render(f"Il Prof. Musci ha preso {player_name}. Fai click per tornare al Menu.", True, WHITE)
        screen.blit(go_t, (WIDTH//2 - go_t.get_width()//2, HEIGHT//2 - 40))
        screen.blit(go_s, (WIDTH//2 - go_s.get_width()//2, HEIGHT//2 + 20))
        if pygame.mouse.get_pressed()[0]: pygame.time.wait(200); game_state = "MENU"

    elif game_state == "VICTORY":
        screen.fill((44, 62, 80))
        if test_difficulty == "EASY":
            v_t = font_title.render(f"6 PORTATO A CASA, {player_name.upper()}!", True, (46, 204, 113))
            v_s = font_story.render("Hai scelto la via onesta e della fortuna. Sei salvo!", True, WHITE)
            screen.blit(v_t, (WIDTH//2 - v_t.get_width()//2, HEIGHT//2 - 60))
            screen.blit(v_s, (WIDTH//2 - v_s.get_width() // 2, HEIGHT//2))
        else:
            v_t = font_title.render(f"VITTORIA ASSOLUTA, {player_name.upper()}!", True, (241, 196, 15))
            v_m1 = font_story.render("Il Prof. Musci si inchina davanti alla tua bravura:", True, WHITE)
            v_m2 = font_story.render(f"\"Accidenti {player_name}... quel 10 era tutto meritato! Il tuo codice è perfetto,", True, (46, 204, 113))
            v_m3 = font_story.render("elegante, ottimizzato e privo di bug. Sei un vero genio!\"", True, (46, 204, 113))
            screen.blit(v_t, (WIDTH//2 - v_t.get_width()//2, HEIGHT//2 - 100))
            screen.blit(v_m1, (WIDTH//2 - v_m1.get_width()//2, HEIGHT//2 - 30))
            screen.blit(v_m2, (WIDTH//2 - v_m2.get_width()//2, HEIGHT//2 + 15))
            screen.blit(v_m3, (WIDTH//2 - v_m3.get_width()//2, HEIGHT//2 + 50))
        v_sub = font_ui.render("Premi SPAZIO per tornare al Menu principale.", True, WHITE)
        screen.blit(v_sub, (WIDTH//2 - v_sub.get_width() // 2, HEIGHT//2 + 120))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
