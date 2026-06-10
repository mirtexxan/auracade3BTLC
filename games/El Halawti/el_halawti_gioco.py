import pygame
import random
import sys
import os
import math
import struct

# --- INIZIALIZZAZIONE ---
pygame.init()
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.mixer.init()

WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("No Sleep Run: Cobweb Edition")
clock = pygame.time.Clock()

# --- SINTETIZZATORE AUDIO INTERNO ---
def genera_suono_salto():
    sample_rate = 22050; duration = 0.15 
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 150 + (550 - 150) * (t / duration)
        v = int(math.sin(2 * math.pi * freq * t) * 12000)
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

def genera_suono_scivolata():
    sample_rate = 22050; duration = 0.22
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = max(150, 450 - (270 * (t / duration)))
        fade = max(0.0, 1.0 - (t / duration))
        v = int(math.sin(2 * math.pi * freq * t) * 9000 * fade)
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

def genera_suono_caduta():
    sample_rate = 22050; duration = 1.0
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = max(50, 600 - (550 * (t / duration)))
        fade = max(0.0, 1.0 - (t / duration))
        v = int(math.sin(2 * math.pi * freq * t) * 11000 * fade)
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

def genera_suono_jumpscare():
    sample_rate = 22050; duration = 1.2
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        noise = random.randint(-28000, 28000)
        rumble = math.sin(2 * math.pi * 60 * t) * 4000
        fade = max(0.0, 1.0 - (t / duration))
        v = int((noise + rumble) * fade)
        v = max(-32768, min(32767, v)) 
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

def genera_musica_ambiente():
    sample_rate = 22050; duration = 5.0 
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        f1 = math.sin(2 * math.pi * 55 * t)
        f2 = math.sin(2 * math.pi * 65 * t)
        f3 = math.sin(2 * math.pi * 110 * t * (1 + 0.01 * math.sin(2 * math.pi * 0.5 * t)))
        v = int(((f1 + f2 + f3) / 3) * 9000)
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

def genera_suono_moneta():
    sample_rate = 22050; duration = 0.12
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 1500 + math.sin(2 * math.pi * 20 * t) * 200 
        fade = max(0.0, 1.0 - (t / duration)**2)
        v = int(math.sin(2 * math.pi * freq * t) * 8000 * fade)
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

def genera_suono_powerup():
    sample_rate = 22050; duration = 0.35
    buf = bytearray()
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 300 + (int(t * 15) * 100) 
        fade = max(0.0, 1.0 - (t / duration))
        v = int(math.sin(2 * math.pi * freq * t) * 9000 * fade)
        buf.extend(struct.pack('<h', v))
    return pygame.mixer.Sound(buffer=buf)

jump_sound = genera_suono_salto()
slide_sound = genera_suono_scivolata()
fall_sound = genera_suono_caduta()
jumpscare_sound = genera_suono_jumpscare()
coin_sound = genera_suono_moneta()
powerup_sound = genera_suono_powerup()
ambient_music = genera_musica_ambiente()
ambient_music.play(-1)

# --- FILE DI SALVATAGGIO ---
HS_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE, "r") as f: return int(f.read().strip())
        except: return 0
    return 0

def save_high_score(new_score):
    try:
        with open(HS_FILE, "w") as f: f.write(str(int(new_score)))
    except: pass

high_score = load_high_score()

# --- COLORI ---
WHITE = (255, 255, 255)
SKY_DARK = (4, 6, 16)
SKY_LIGHT = (20, 30, 60)
STARS_COLOR = (230, 235, 255)
MOON_COLOR = (255, 245, 180)
YELLOW_COIN = (255, 200, 0)
RED = (255, 30, 30)
ORANGE = (255, 130, 0)
CYAN = (0, 255, 255)
GREEN = (50, 255, 100)
GRAY_WEB = (180, 190, 200, 180)

COLOR_BG_BUILDINGS = (12, 16, 28)   
COLOR_MID_BUILDINGS = (22, 26, 42)  
COLOR_FOREGROUND = (34, 38, 58)     
COLOR_LEDGE = (50, 56, 84)          
COLOR_EXTRA_ROOF = (44, 48, 72)     
WINDOW_ON = (255, 220, 100)          
WINDOW_OFF = (20, 24, 36)           

# --- FONT ---
font_title = pygame.font.SysFont("impact", 65)
font_ui = pygame.font.SysFont("impact", 24)        # Rimesso standard
font_sub = pygame.font.SysFont("consolas", 18, bold=True) 
font_recap = pygame.font.SysFont("consolas", 14, bold=True) 
font_massive = pygame.font.SysFont("impact", 130)

# --- FRASI MORTE DA CADUTA ---
fall_phrases = ["Hai dimenticato come si vola?", "Un salto nel buio totale...", "Non c'era il pavimento lì.", "La gravità non perdona.", "Oops. Manca un gradino.", "Salto della fede?"]

gradient_bg = pygame.Surface((1, 2))
gradient_bg.set_at((0, 0), SKY_DARK)
gradient_bg.set_at((0, 1), SKY_LIGHT)
gradient_bg = pygame.transform.smoothscale(gradient_bg, (WIDTH, HEIGHT))

particles = [] 
def spawn_dust(x, y, color=(100, 106, 136, 150), amount=5, spread_v=0.5):
    for _ in range(amount):
        particles.append({
            "x": x, "y": y, "vx": random.uniform(-4, -1), "vy": random.uniform(-spread_v, spread_v),
            "radius": random.uniform(2, 4), "color": color, "life": 1.0
        })

# --- HELPER DISEGNO ---
def draw_bat(surface, ox, oy, ow, oh, timer_offset):
    fly_y = oy + math.sin(timer_offset) * 15
    pygame.draw.circle(surface, (30, 30, 30), (int(ox + ow//2), int(fly_y + oh//2)), 12)
    wing_y = fly_y + math.sin(timer_offset * 5) * 15
    pygame.draw.polygon(surface, (20, 20, 20), [(ox+ow//2, fly_y+oh//2), (ox-15, wing_y), (ox-5, fly_y+oh)])
    pygame.draw.polygon(surface, (20, 20, 20), [(ox+ow//2, fly_y+oh//2), (ox+ow+15, wing_y), (ox+ow+5, fly_y+oh)])
    pygame.draw.circle(surface, RED, (int(ox + ow//2 - 4), int(fly_y + oh//2 - 2)), 2)
    pygame.draw.circle(surface, RED, (int(ox + ow//2 + 4), int(fly_y + oh//2 - 2)), 2)
    return fly_y

def draw_cobweb(surface, ox, oy, ow, oh):
    web_surf = pygame.Surface((ow, oh), pygame.SRCALPHA)
    pygame.draw.line(web_surf, GRAY_WEB, (0, 0), (ow, oh), 2)
    pygame.draw.line(web_surf, GRAY_WEB, (ow, 0), (0, oh), 2)
    pygame.draw.line(web_surf, GRAY_WEB, (ow//2, 0), (ow//2, oh), 2)
    pygame.draw.line(web_surf, GRAY_WEB, (0, oh//2), (ow, oh//2), 2)
    for r in range(1, 4): pygame.draw.rect(web_surf, GRAY_WEB, (ow//2 - r*5, oh//2 - r*5, r*10, r*10), 1)
    surface.blit(web_surf, (ox, oy))

def draw_powerup(surface, p_type, px, py):
    if p_type == "BRIDGE":
        pygame.draw.circle(surface, WHITE, (int(px-8), int(py+4)), 10)
        pygame.draw.circle(surface, WHITE, (int(px+8), int(py+4)), 10)
        pygame.draw.circle(surface, WHITE, (int(px), int(py-4)), 12)
        pygame.draw.circle(surface, CYAN, (int(px), int(py+2)), 6)
    elif p_type == "SPEED":
        pygame.draw.circle(surface, YELLOW_COIN, (int(px), int(py)), 12)
        pygame.draw.polygon(surface, WHITE, [(px+3, py-6), (px-4, py+2), (px+2, py+2), (px-3, py+8)])
    elif p_type == "MEGA_JUMP":
        pygame.draw.circle(surface, GREEN, (int(px), int(py)), 12)
        pygame.draw.polygon(surface, WHITE, [(px, py-6), (px-6, py+2), (px+6, py+2)])
    elif p_type == "SLOW_GHOST":
        pygame.draw.circle(surface, CYAN, (int(px), int(py)), 12)
        pygame.draw.circle(surface, WHITE, (int(px), int(py)), 8, 2)

# --- CLASSE GIOCATORE ---
class Player:
    def __init__(self):
        self.x, self.y = 350, 200
        self.width, self.height = 50, 75
        self.vy = 0
        self.is_jumping = self.double_jumped = False 
        self.is_flipping = False
        self.flip_angle = 0
        self.flip_style = "NORMAL"
        self.is_sliding = False
        self.slide_timer = 0
        self.anim_timer = 0.0
        self.jump_power = -13.5
        self.mega_jump_active = False
        self.is_dead_falling = False
        self.hat_x = self.hat_y = self.hat_vx = self.hat_vy = 0

    def jump(self):
        if self.is_sliding or self.is_dead_falling: return
        if not self.is_jumping:
            self.vy = self.jump_power
            self.is_jumping = True
            self.double_jumped = False
            self.is_flipping = False
            self.flip_angle = 0
            jump_sound.play() 
            spawn_dust(self.x + 10, self.y + self.height)
            if self.mega_jump_active:
                self.jump_power = -13.5
                self.mega_jump_active = False
                spawn_dust(self.x + 25, self.y + self.height, GREEN, 15)
        elif not self.double_jumped:
            self.vy = -10.5 
            self.double_jumped = True
            self.is_flipping = True
            self.flip_angle = 0
            self.flip_style = random.choice(["FORWARD", "DOUBLE_BACK", "SPIN_FAST", "FLOAT_TWIST"])
            jump_sound.play() 
            spawn_dust(self.x + 25, self.y + self.height, CYAN, 12)

    def slide(self):
        if not self.is_jumping and not self.is_sliding and not self.is_dead_falling:
            self.is_sliding = True
            self.slide_timer = 30 
            self.height = 40      
            self.y += 35          
            slide_sound.play() 

    def update(self, platforms, current_speed, bridge_active):
        if self.is_dead_falling: return

        if self.is_sliding:
            self.slide_timer -= 1
            # SCINTILLE DALLA MANO A TERRA DURANTE LA SCIVOLATA
            if random.random() < 0.4: 
                spawn_dust(self.x + 15, self.y + self.height, ORANGE, 2, 1.5)
            if self.slide_timer <= 0:
                self.is_sliding = False; self.height = 75; self.y -= 35

        self.vy += 0.58 
        self.y += self.vy
        self.anim_timer += current_speed * 0.05 if not self.is_jumping else 0.12

        if self.is_flipping:
            if self.flip_style == "FORWARD":
                self.flip_angle -= 15
                if self.flip_angle <= -360: self.flip_angle = 0; self.is_flipping = False
            elif self.flip_style == "DOUBLE_BACK":
                self.flip_angle += 22
                if self.flip_angle >= 720: self.flip_angle = 0; self.is_flipping = False
            elif self.flip_style == "SPIN_FAST":
                self.flip_angle -= 30
                if self.flip_angle <= -720: self.flip_angle = 0; self.is_flipping = False
            elif self.flip_style == "FLOAT_TWIST":
                self.flip_angle -= 8
                if self.flip_angle <= -360: self.flip_angle = 0; self.is_flipping = False

        on_ground = False
        
        if bridge_active and self.vy >= 0 and self.y + self.height >= HEIGHT - 30:
            self.y = HEIGHT - 30 - self.height; self.vy = 0; on_ground = True

        for plat in platforms:
            if (plat['x'] <= self.x + self.width - 15 and plat['x'] + plat['w'] >= self.x + 15):
                if self.y + self.height >= plat['y'] and self.y + self.height - self.vy <= plat['y'] + 18:
                    self.y = plat['y'] - self.height; self.vy = 0; on_ground = True; break
            
            if plat['has_extra']:
                ex, ey, ew = plat['x'] + plat['extra_x'], plat['y'] - plat['extra_h'], plat['extra_w']
                if (ex <= self.x + self.width - 15 and ex + ew >= self.x + 15):
                    if self.y + self.height >= ey and self.y + self.height - self.vy <= ey + 18:
                        self.y = ey - self.height; self.vy = 0; on_ground = True; break

            for obs in plat['obstacles']:
                if obs['type'] == "CRATE":
                    ox, oy = plat['x'] + obs['rel_x'], obs['y']
                    if (ox <= self.x + self.width - 12 and ox + obs['w'] >= self.x + 12):
                        if self.y + self.height >= oy and self.y + self.height - self.vy <= oy + 18:
                            self.y = oy - self.height; self.vy = 0; on_ground = True; break
            if on_ground: break

        if on_ground:
            self.is_jumping = self.double_jumped = self.is_flipping = False
            self.flip_angle = 0
        elif self.vy > 0:
            self.is_jumping = True

    def draw(self, surface, is_speeding=False):
        if self.is_dead_falling:
            ts = pygame.Surface((150, 150), pygame.SRCALPHA)
            bx, by = 75, 75
            pygame.draw.rect(ts, (65, 105, 225), (bx - 25, by - 12, 50, 24), border_radius=6)
            hx, hy = bx + 32, by
            pygame.draw.circle(ts, (244, 194, 144), (int(hx), int(hy)), 11)
            pygame.draw.circle(ts, (90, 50, 30), (int(hx), int(hy - 3)), 11) 
            rotated = pygame.transform.rotate(ts, -25) 
            rect = rotated.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            surface.blit(rotated, rect.topleft)
            return

        ts = pygame.Surface((150, 150), pygame.SRCALPHA)
        t = self.anim_timer
        bx = 75 
        
        # --- ANIMAZIONE SCIVOLATA "FREE FLOW" CON 3 FASI ---
        if self.is_sliding:
            by = 75
            t_slide = 30 - self.slide_timer
            
            if t_slide < 10: # FASE 1: Inizio scivolata (Parkour)
                # Braccio Sinistro (A terra dietro)
                pygame.draw.line(ts, (40, 50, 80), (bx - 5, by - 5), (bx - 22, by + 18), 6)
                pygame.draw.circle(ts, (244, 194, 144), (bx - 22, by + 18), 4)
                
                # Gambe piegate sotto
                pygame.draw.line(ts, (30, 34, 54), (bx - 10, by + 5), (bx - 18, by + 16), 7)
                pygame.draw.line(ts, (30, 34, 54), (bx - 18, by + 16), (bx + 5, by + 20), 7)
                
                # Busto inclinato dietro
                pygame.draw.polygon(ts, (65, 105, 225), [(bx-12, by-10), (bx+6, by-15), (bx+6, by+8), (bx-12, by+4)])
                
                # Testa
                hx, hy = bx + 8, by - 22
                
                # Braccio Destro (Tiene cappello)
                pygame.draw.line(ts, (85, 125, 245), (bx + 2, by - 8), (hx - 4, hy - 9), 5)
                pygame.draw.circle(ts, (244, 194, 144), (int(hx - 4), int(hy - 9)), 3)

            elif t_slide < 20: # FASE 2: Transizione bassa (Low Crawl)
                by = 82 # Più basso
                # Busto orizzontale
                pygame.draw.rect(ts, (65, 105, 225), pygame.Rect(bx - 20, by - 8, 40, 16), border_radius=5)
                
                # Testa avanti bassa
                hx, hy = bx + 18, by - 8
                
                # Braccio Sinistro (A terra dritto dietro)
                pygame.draw.line(ts, (40, 50, 80), (bx - 15, by - 2), (bx - 35, by + 10), 6)
                pygame.draw.circle(ts, (244, 194, 144), (bx - 35, by + 10), 4)
                
                # Gambe stese dietro basse
                pygame.draw.line(ts, (50, 60, 90), (bx - 18, by + 4), (bx - 45, by + 12), 8)
                
                # Braccio Destro (Tiene cappello avanti basso)
                pygame.draw.line(ts, (85, 125, 245), (bx + 5, by - 4), (hx - 4, hy - 5), 5)
                pygame.draw.circle(ts, (244, 194, 144), (int(hx - 4), int(hy - 5)), 3)

            else: # FASE 3: Fine scivolata (Ritorno posa parkour estesa)
                # Braccio Sinistro (A terra dietro/basso)
                pygame.draw.line(ts, (40, 50, 80), (bx - 5, by - 5), (bx - 22, by + 18), 6)
                pygame.draw.circle(ts, (244, 194, 144), (bx - 22, by + 18), 4)
                
                # Gamba Anteriore (Estesa avanti)
                pygame.draw.line(ts, (50, 60, 90), (bx - 5, by + 5), (bx + 35, by + 18), 8)
                pygame.draw.rect(ts, WHITE, (bx + 25, by + 14, 12, 6), border_radius=2)
                
                # Busto inclinato dietro
                pygame.draw.polygon(ts, (65, 105, 225), [(bx-12, by-10), (bx+6, by-15), (bx+6, by+8), (bx-12, by+4)])
                
                # Testa
                hx, hy = bx + 8, by - 22
                
                # Braccio Destro (Tiene cappello)
                pygame.draw.line(ts, (85, 125, 245), (bx + 2, by - 8), (hx - 4, hy - 9), 5)
                pygame.draw.circle(ts, (244, 194, 144), (int(hx - 4), int(hy - 9)), 3)

            # --- DISEGNO COMUNE TESTA E CAPPELLO ---
            pygame.draw.circle(ts, (244, 194, 144), (int(hx), int(hy)), 10) 
            pygame.draw.circle(ts, (90, 50, 30), (int(hx), int(hy - 4)), 11) # Capelli
            hat_tip_x, hat_tip_y = hx - 5, hy - 18
            pygame.draw.polygon(ts, (40, 100, 200), [(hx-8, hy-10), (hx+8, hy-10), (hat_tip_x, hat_tip_y)])
            pygame.draw.circle(ts, WHITE, (int(hat_tip_x), int(hat_tip_y)), 4) 

        elif not is_speeding:
            # Animazione di corsa normale (copy old code here)
            bobbing = abs(math.sin(t * 2)) * 6 if not self.is_jumping else 0
            leg1 = math.sin(t) * 40 if not self.is_jumping else (20 if self.vy < 0 else -10)
            leg2 = math.sin(t + math.pi) * 40 if not self.is_jumping else (-30 if self.vy < 0 else 40)
            arm1 = math.sin(t + math.pi - 0.5) * 35 if not self.is_jumping else -45 
            arm2 = math.sin(t - 0.5) * 35 if not self.is_jumping else 45            

            by = 65 + bobbing
            rad2, rad_arm1 = math.radians(90 + leg2), math.radians(90 + arm1)
            pygame.draw.line(ts, (30, 34, 54), (bx, by + 15), (bx + math.cos(rad2)*25, (by + 20) + math.sin(rad2)*25), 7) 
            pygame.draw.line(ts, (40, 50, 80), (bx, by-5), (bx + math.cos(rad_arm1)*20, by-5 + math.sin(rad_arm1)*20), 6)
            
            pygame.draw.rect(ts, (65, 105, 225), pygame.Rect(bx - 12, by - 10, 24, 30), border_radius=6) 
            
            hx, hy = bx + 4, by - 22
            pygame.draw.circle(ts, (244, 194, 144), (int(hx), int(hy)), 10) 
            pygame.draw.circle(ts, (90, 50, 30), (int(hx), int(hy - 4)), 11)   
            
            hat_tip_x = hx - 15 - math.sin(t)*3
            hat_tip_y = hy - 18 + math.cos(t)*3
            pygame.draw.polygon(ts, (40, 100, 200), [(hx-8, hy-10), (hx+8, hy-10), (hat_tip_x, hat_tip_y)])
            pygame.draw.circle(ts, WHITE, (int(hat_tip_x), int(hat_tip_y)), 5) 

            rad1, rad_arm2 = math.radians(90 + leg1), math.radians(90 + arm2)
            pygame.draw.line(ts, (50, 60, 90), (bx, by + 15), (bx + math.cos(rad1)*25, (by + 20) + math.sin(rad1)*25), 8)  
            hand_x, hand_y = bx - 2 + math.cos(rad_arm2)*20, by-5 + math.sin(rad_arm2)*20
            pygame.draw.line(ts, (85, 125, 245), (bx - 2, by-5), (hand_x, hand_y), 5) 
            pygame.draw.circle(ts, (244, 194, 144), (int(hand_x), int(hand_y)), 3)

            if self.mega_jump_active: pygame.draw.circle(ts, (50, 255, 100, 100), (int(bx), int(by)), 35, 2)
        else:
            # --- NUOVA ANIMAZIONE SUPER VELOCITÀ (Hat logic corretto) ---
            bobbing = abs(math.sin(t * 4)) * 3 # Faster bobbing
            leg1 = math.sin(t * 2) * 50 # Wider stride leg1
            leg2 = math.sin(t * 2 + math.pi) * 50
            by = 68 + bobbing # Leaning forward slightly
            
            # Leg2 (Dietro)
            pygame.draw.line(ts, (30, 34, 54), (bx, by + 15), (bx + leg2*0.5, by + 45 - leg2*0.2), 7)
            
            # Busto inclinato avanti (Rimosso border_radius per evitare il crash)
            pygame.draw.polygon(ts, (65, 105, 225), [(bx-8, by-10), (bx+12, by-14), (bx+12, by+8), (bx-8, by+4)])
            
            # Braccio Destro Dritto Dietro
            pygame.draw.line(ts, (85, 125, 245), (bx - 5, by - 5), (bx - 30, by + 15), 6)
            pygame.draw.circle(ts, (244, 194, 144), (bx - 30, by + 15), 3)

            # Leg1 (Avanti dritto)
            pygame.draw.line(ts, (50, 60, 90), (bx, by + 15), (bx + leg1*0.6, by + 45 + leg1*0.1), 8)

            # Testa inclinato avanti
            hx, hy = bx + 12, by - 24
            pygame.draw.circle(ts, (244, 194, 144), (int(hx), int(hy)), 10)
            pygame.draw.circle(ts, (90, 50, 30), (int(hx), int(hy - 4)), 11)

            # Cappello
            hat_tip_x, hat_tip_y = hx - 5, hy - 18
            pygame.draw.polygon(ts, (40, 100, 200), [(hx-8, hy-10), (hx+8, hy-10), (hat_tip_x, hat_tip_y)])
            pygame.draw.circle(ts, WHITE, (int(hat_tip_x), int(hat_tip_y)), 4)

            # Braccio Sinistro Tiene cappello (dritto rivolto avanti alzata)
            pygame.draw.line(ts, (40, 50, 80), (bx + 8, by - 12), (hx - 4, hy - 9), 6)
            pygame.draw.circle(ts, (244, 194, 144), (int(hx - 4), int(hy - 9)), 3) # Mano sul cappello

        if self.is_flipping or self.flip_angle != 0:
            rotated = pygame.transform.rotate(ts, self.flip_angle)
            rect = rotated.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
            surface.blit(rotated, rect.topleft)
        else:
            surface.blit(ts, (self.x + self.width//2 - 75, self.y + self.height//2 - 65))

# --- CLASSE FANTASMA ---
class Ghost:
    def __init__(self):
        self.x, self.y = 40, 200
        self.width, self.height = 110, 110
        self.float_timer = 0.0
        self.particles = []

    def update(self, player_y):
        self.float_timer += 0.05
        self.y += ((player_y - 25 + math.sin(self.float_timer) * 15) - self.y) * 0.04
        if random.random() < 0.6:
            self.particles.append({"x": self.x + random.randint(20, 80), "y": self.y + self.height - random.randint(0, 30), "radius": random.uniform(8, 22), "alpha": 200})

    def draw(self, surface):
        for p in self.particles[:]:
            p["alpha"] -= 5; p["x"] -= 0.5; p["y"] -= random.uniform(1, 3); p["radius"] += 0.2
            if p["alpha"] <= 0: self.particles.remove(p)
            else:
                ts = pygame.Surface((p["radius"]*2, p["radius"]*2), pygame.SRCALPHA)
                pygame.draw.circle(ts, (240, 245, 255, p["alpha"]), (int(p["radius"]), int(p["radius"])), int(p["radius"]))
                surface.blit(ts, (p["x"] - p["radius"], p["y"] - p["radius"]))

        gx, gy = self.x, self.y
        b1, b2 = math.sin(self.float_timer * 2.5) * 4, math.cos(self.float_timer * 2) * 5
        for px, py, pr in [(30, 60+b1, 35+b1), (60, 45-b2, 45+b2), (90, 65+b1, 30+b1), (50, 85+b2, 35+b2), (75, 85-b1, 30+b1)]:
            pygame.draw.circle(surface, WHITE, (int(gx+px), int(gy+py)), pr)
        eye_y = gy + 50
        pygame.draw.ellipse(surface, (20, 20, 30), (gx + 55, eye_y - 5, 10, 16))
        pygame.draw.ellipse(surface, (20, 20, 30), (gx + 75, eye_y - 5, 10, 16))
        pygame.draw.circle(surface, RED, (int(gx + 58), int(eye_y + 3)), 3)
        pygame.draw.circle(surface, RED, (int(gx + 78), int(eye_y + 3)), 3)

# --- GENERATORE MONDO ---
def create_foreground_platform(x_pos, is_start=False):
    if is_start:
        w, y = 1200, 360
        return {'x': x_pos, 'y': y, 'w': w, 'windows': [], 'has_extra': False, 'extra_x': 0, 'extra_w': 0, 'extra_h': 0, 'obstacles': [], 'coins': [], 'powerups': []}

    w, y = random.randint(350, 520), random.randint(330, 410)
    windows = [(c * 40 - 15, r * 40, random.random() < 0.3) for r in range(1, (500 - y) // 50) for c in range(1, w // 40)]
            
    has_extra = random.random() < 0.40 
    extra_x = extra_w = extra_h = 0
    if has_extra:
        extra_w, extra_h = random.randint(120, 180), random.randint(55, 75)
        extra_x = random.randint(40, w - extra_w - 40)

    obstacles = []
    if x_pos > 800 and random.random() < 0.70: 
        obs_type = random.choice(["SIGN", "DRONE", "BARRIER", "CRATE", "BAT", "COBWEB"]) 
        obs_rel_x = random.randint(60, w - 80)
        if has_extra and (extra_x - 40 < obs_rel_x < extra_x + extra_w + 40):
            obs_rel_x = extra_x + extra_w + 30 if extra_x + extra_w + 90 < w else extra_x - 50

        if obs_type in ["SIGN", "DRONE", "BAT"]: obstacles.append({"rel_x": obs_rel_x, "y": y - 75, "w": 35, "h": 25, "type": obs_type, "anim_offset": random.random()*10})
        elif obs_type == "COBWEB": obstacles.append({"rel_x": obs_rel_x, "y": y - 65, "w": 45, "h": 65, "type": obs_type, "anim_offset": 0})
        else: obstacles.append({"rel_x": obs_rel_x, "y": y - 35, "w": 35, "h": 35, "type": obs_type, "anim_offset": 0})

    coins = []
    if random.random() < 0.65:
        num_coins, coin_y = random.randint(2, 4), (y - extra_h - 40) if has_extra else (y - 35)
        for i in range(num_coins): coins.append({"rel_x": random.randint(45, w-45) if not has_extra else (extra_x + 20 + i*25), "y": coin_y, "collected": False})

    powerups = []
    if random.random() < 0.15 and len(obstacles) <= 1:
        powerups.append({"rel_x": random.randint(50, w-50), "y": (y - extra_h - 50) if has_extra else (y - 50), "type": random.choice(["BRIDGE", "SPEED", "MEGA_JUMP", "SLOW_GHOST"]), "collected": False})

    return {'x': x_pos, 'y': y, 'w': w, 'windows': windows, 'has_extra': has_extra, 'extra_x': extra_x, 'extra_w': extra_w, 'extra_h': extra_h, 'obstacles': obstacles, 'coins': coins, 'powerups': powerups}

def fill_platforms(plat_list):
    while len(plat_list) == 0 or plat_list[-1]['x'] + plat_list[-1]['w'] < WIDTH + 1000:
        last_x = plat_list[-1]['x'] + plat_list[-1]['w'] if plat_list else 0
        plat_list.append(create_foreground_platform(last_x + random.randint(100, 180)))

stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, 260), "r": random.uniform(0.8, 2.5), "phase": random.uniform(0, 5)} for _ in range(70)]
bg_buildings = [{"x": i * 160, "w": random.randint(120, 220), "h": random.randint(200, 380)} for i in range(8)]
mid_buildings = [{"x": i * 220, "w": random.randint(150, 260), "h": random.randint(260, 420)} for i in range(6)]

platforms = [create_foreground_platform(0, True)]
fill_platforms(platforms)

player, ghost = Player(), Ghost()
state = "MENU" 
base_speed, current_speed = 4.5, 4.5
subway_score, coins_collected = 0.0, 0
score_multiplier = 1 
distance_to_ghost, max_distance = 320, 320
active_bridge_timer = active_speed_timer = countdown_timer = jumpscare_timer = death_timer = gameover_timer = global_time = 0
death_msg = ""

# --- MAIN LOOP ---
while True:
    screen.blit(gradient_bg, (0, 0)) 
    events = pygame.event.get()
    global_time += 1

    for event in events:
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if state == "MENU": state = "RECAP" 
                elif state == "RECAP":
                    player, ghost = Player(), Ghost()
                    base_speed, subway_score, coins_collected = 4.5, 0, 0
                    score_multiplier = 1 
                    distance_to_ghost = max_distance
                    active_bridge_timer = active_speed_timer = 0
                    particles.clear()
                    platforms = [create_foreground_platform(0, True)]
                    fill_platforms(platforms)
                    ambient_music.stop(); ambient_music.play(-1)
                    state, countdown_timer = "COUNTDOWN", 180 
                elif state == "PLAYING": player.jump()
                elif state == "GAMEOVER" and gameover_timer > 40: state = "MENU"
            if event.key == pygame.K_DOWN and state == "PLAYING": player.slide()

    for star in stars:
        star["phase"] += 0.03
        star["x"] -= (current_speed * 0.01) if state == "PLAYING" else 0.1
        if star["x"] < 0: star["x"] = WIDTH
        pygame.draw.circle(screen, STARS_COLOR, (int(star["x"]), int(star["y"])), float(star["r"] + math.sin(star["phase"])*0.7))
    pygame.draw.circle(screen, MOON_COLOR, (740, 90), 32)
    pygame.draw.circle(screen, SKY_LIGHT, (728, 82), 30)

    # --- STATO: MENU INIZIALE ---
    if state == "MENU":
        draw_bat(screen, 150, 100, 35, 25, global_time * 0.05)
        title = font_title.render("NO SLEEP RUN", True, RED)
        txt_hs = font_ui.render(f"TOP RECORD: {high_score} PUNTI", True, YELLOW_COIN)
        pulse_val = int(130 + 125 * math.sin(global_time * 0.09))
        sub = font_sub.render("Premi SPAZIO per visualizzare i comandi", True, (pulse_val, pulse_val, pulse_val))
        
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        screen.blit(txt_hs, (WIDTH//2 - txt_hs.get_width()//2, 170))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 430))
        
        ghost.x, ghost.y = WIDTH // 4 - ghost.width // 2 - 50, 230
        ghost.update(250); ghost.draw(screen)
        player.x, player.y = 3 * WIDTH // 4 - player.width // 2 + 50, 250
        player.anim_timer += 0.08; player.draw(screen)

    # --- STATO: GUIDA ---
    elif state == "RECAP":
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 26, 235))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, COLOR_LEDGE, (40, 20, WIDTH - 80, HEIGHT - 40), 3, border_radius=16)
        
        t_head = font_title.render("MANUALE DI GIOCO", True, RED)
        screen.blit(t_head, (WIDTH//2 - t_head.get_width()//2, 35))
        
        x_left = 60
        screen.blit(font_ui.render("🕹️ COMANDI REATTIVI", True, CYAN), (x_left, 115))
        screen.blit(font_recap.render("- [SPAZIO]: Salto normale / Muro", True, WHITE), (x_left + 15, 155))
        screen.blit(font_recap.render("- [SPAZIO] x2: Doppio Salto Acrobatico", True, WHITE), (x_left + 15, 185))
        screen.blit(font_recap.render("- [FRECCIA GIÙ]: Scivolata Parkour", True, WHITE), (x_left + 15, 215))
        
        screen.blit(font_ui.render("⚠️ PERICOLI CITTADINI", True, RED), (x_left, 265))
        screen.blit(font_recap.render("- Ragnatele: Ti rallentano drasticamente!", True, ORANGE), (x_left + 15, 305))
        screen.blit(font_recap.render("- Pipistrelli/Muri: Scivola o Salta", True, WHITE), (x_left + 15, 335))
        screen.blit(font_recap.render("- Il Vuoto: Cadere spegne la musica...", True, RED), (x_left + 15, 365))
        
        x_right = 460
        screen.blit(font_ui.render("✨ POTENZIAMENTI DISPONIBILI", True, GREEN), (x_right, 115))
        draw_powerup(screen, "BRIDGE", x_right + 15, 160)
        screen.blit(font_recap.render("   Ponte Spaziale: Copre il vuoto sul fondo", True, WHITE), (x_right + 25, 152))
        draw_powerup(screen, "SPEED", x_right + 15, 195)
        screen.blit(font_recap.render("   Hyper Dash: Velocità + Allontana Spettro", True, YELLOW_COIN), (x_right + 25, 187))
        draw_powerup(screen, "MEGA_JUMP", x_right + 15, 230)
        screen.blit(font_recap.render("   Mega Salto: Spinta di salto amplificata", True, WHITE), (x_right + 25, 222))
        draw_powerup(screen, "SLOW_GHOST", x_right + 15, 265)
        screen.blit(font_recap.render("   Esorcismo: Allontana lo Spettro", True, WHITE), (x_right + 25, 257))
        
        screen.blit(font_ui.render("🪙 ECONOMIA E RECORD", True, YELLOW_COIN), (x_right, 310))
        screen.blit(font_recap.render("Raccogli i gettoni d'oro per aumentare i", True, WHITE), (x_right + 15, 350))
        screen.blit(font_recap.render("punti (+100) e scalare la classifica.", True, WHITE), (x_right + 15, 375))
        
        pulse_b = int(130 + 125 * math.sin(global_time * 0.1))
        t_start = font_sub.render("PREMI SPAZIO PER INIZIARE LA FUGA DALL'INCUBO", True, (pulse_b, pulse_b, 40))
        screen.blit(t_start, (WIDTH//2 - t_start.get_width()//2, 440))

    # --- STATO: GIOCO / COUNTDOWN ---
    elif state in ["COUNTDOWN", "PLAYING"]:
        if state == "PLAYING":
            if active_bridge_timer > 0: active_bridge_timer -= 1
            if active_speed_timer > 0: active_speed_timer -= 1

            current_speed = base_speed
            if active_speed_timer > 0:
                current_speed = base_speed * 1.15
                score_multiplier = (1 + int(subway_score // 1000)) * 2
                
                # MODIFICA LOGICA VELOCITÀ: Allontana piano piano il fantasma frame dopo frame
                distance_to_ghost = min(max_distance, distance_to_ghost + 0.6)
                
                if random.random() < 0.3:
                    particles.append({"x": player.x, "y": player.y + random.randint(10, player.height - 10), "vx": -current_speed * 0.4, "vy": random.uniform(-0.5, 0.5), "radius": random.uniform(2, 5), "color": YELLOW_COIN, "life": 0.7})
            else:
                score_multiplier = 1 + int(subway_score // 1000)

            if base_speed < 9.0: base_speed += 0.0006 

            is_blocked = is_stuck_in_web = False
            for plat in platforms:
                if plat['x'] < player.x + player.width and plat['x'] > player.x:
                    if player.y + player.height > plat['y'] + 12: is_blocked = True
                
                for obs in plat['obstacles']:
                    obs_abs_x = plat['x'] + obs['rel_x']
                    if (player.x + 12 < obs_abs_x + obs['w'] and player.x + player.width - 12 > obs_abs_x):
                        if obs['type'] == "COBWEB":
                            if (player.y < obs['y'] + obs['h'] and player.y + player.height > obs['y']): is_stuck_in_web = True
                        elif obs['type'] == "CRATE":
                            if player.y + player.height > obs['y'] + 14 and player.y + 10 < obs['y'] + obs['h']: is_blocked = True
                        else:
                            if (player.y + 10 < obs['y'] + obs['h'] and player.y + player.height - 10 > obs['y']): is_blocked = True

            player.update(platforms, current_speed, active_bridge_timer > 0)
            ghost.update(player.y)
            ghost.x = player.x - distance_to_ghost

            if is_blocked:
                distance_to_ghost -= 6.0 
                if random.random() < 0.4: spawn_dust(player.x + player.width, player.y + player.height//2, RED, 2)
            else:
                speed_multiplier = 0.35 if is_stuck_in_web else 1.0
                actual_speed = current_speed * speed_multiplier
                
                subway_score += (actual_speed * 0.05) * score_multiplier
                distance_to_ghost -= 1.5 if is_stuck_in_web else 0.03
                
                if is_stuck_in_web and random.random() < 0.3: spawn_dust(player.x + player.width//2, player.y + player.height, GRAY_WEB, 2)

                for b in bg_buildings:
                    b["x"] -= actual_speed * 0.12
                    if b["x"] + b["w"] < 0: b["x"] = WIDTH + random.randint(0, 50)
                for b in mid_buildings:
                    b["x"] -= actual_speed * 0.35
                    if b["x"] + b["w"] < 0: b["x"] = WIDTH + random.randint(10, 90)

                for plat in platforms: plat['x'] -= actual_speed
                if platforms[0]['x'] + platforms[0]['w'] < -100: platforms.pop(0)
                fill_platforms(platforms)

            for p in particles[:]:
                if not is_blocked: p["x"] -= current_speed * 0.2 * (0.35 if is_stuck_in_web else 1.0)
                p["life"] -= 0.03
                if p["life"] <= 0: particles.remove(p)

            # SCONFITTE
            if pygame.Rect(ghost.x + 20, ghost.y + 20, ghost.width - 40, ghost.height - 40).colliderect(pygame.Rect(player.x, player.y, player.width, player.height)):
                state, jumpscare_timer = "JUMPSCARE", 0
                ambient_music.stop(); jumpscare_sound.play()    
            elif player.y > HEIGHT - 45:
                state, death_timer = "DYING_FALL", 0
                player.is_dead_falling = True
                player.hat_x, player.hat_y, player.hat_vx, player.hat_vy = player.x + 15, player.y - 15, -3.5, -8.5
                ambient_music.stop(); fall_sound.play()          

        elif state == "COUNTDOWN":
            countdown_timer -= 1
            if countdown_timer <= 0: state = "PLAYING"

        # DISEGNO
        for b in bg_buildings: pygame.draw.rect(screen, COLOR_BG_BUILDINGS, (b["x"], HEIGHT - b["h"], b["w"], b["h"]))
        for b in mid_buildings: pygame.draw.rect(screen, COLOR_MID_BUILDINGS, (b["x"], HEIGHT - b["h"], b["w"], b["h"]))

        if active_bridge_timer > 0:
            bs = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
            for i in range(-20, WIDTH + 40, 35): pygame.draw.circle(bs, (240, 245, 255, min(255, active_bridge_timer * 4)), (i, 25 + int(math.sin(global_time * 0.05 + i) * 5)), 20)
            screen.blit(bs, (0, HEIGHT - 35))

        for plat in platforms:
            pygame.draw.rect(screen, COLOR_FOREGROUND, (plat['x'], plat['y'], plat['w'], HEIGHT - plat['y']))
            pygame.draw.rect(screen, COLOR_LEDGE, (plat['x'], plat['y'], plat['w'], 12))
            
            for wx, wy, is_on in plat['windows']: pygame.draw.rect(screen, WINDOW_ON if is_on else WINDOW_OFF, (plat['x'] + wx, plat['y'] + wy, 16, 22), border_radius=2)
            if plat['has_extra']:
                ex, ey, ew, eh = plat['x'] + plat['extra_x'], plat['y'] - plat['extra_h'], plat['extra_w'], plat['extra_h']
                pygame.draw.rect(screen, COLOR_EXTRA_ROOF, (ex, ey, ew, eh)); pygame.draw.rect(screen, COLOR_LEDGE, (ex, ey, ew, 10)) 

            for obs in plat['obstacles']:
                ox, oy, ow, oh = plat['x'] + obs['rel_x'], obs['y'], obs['w'], obs['h']
                if obs['type'] == "BARRIER": pygame.draw.rect(screen, (220, 60, 40), (ox, oy, ow, oh), border_radius=3)
                elif obs['type'] == "CRATE": pygame.draw.rect(screen, (139, 69, 19), (ox, oy, ow, oh)); pygame.draw.rect(screen, (80, 40, 10), (ox, oy, ow, oh), 3)
                elif obs['type'] == "COBWEB": draw_cobweb(screen, ox, oy, ow, oh)
                elif obs['type'] == "SIGN": pygame.draw.rect(screen, (60, 60, 70), (ox + ow//2 - 3, oy + oh, 6, 70)); pygame.draw.rect(screen, (30, 30, 40), (ox-5, oy, ow+10, oh), border_radius=3) 
                elif obs['type'] == "DRONE": pygame.draw.rect(screen, (100, 100, 115), (ox, oy, ow, oh), border_radius=8)
                elif obs['type'] == "BAT": obs['y'] = draw_bat(screen, ox, oy, ow, oh, global_time * 0.1 + obs['anim_offset'])

            for coin in plat['coins']:
                if not coin['collected']:
                    cx, cy = plat['x'] + coin['rel_x'], coin['y']
                    if state == "PLAYING" and (player.x < cx + 18 and player.x + player.width > cx - 18 and player.y < cy + 18 and player.y + player.height > cy - 18):
                        coin['collected'] = True; coins_collected += 1; subway_score += 100
                        coin_sound.play() 
                    else: pygame.draw.circle(screen, YELLOW_COIN, (cx, cy), 9)

            for pu in plat['powerups']:
                if not pu['collected']:
                    px, py = plat['x'] + pu['rel_x'], pu['y']
                    if state == "PLAYING" and (player.x < px + 20 and player.x + player.width > px - 20 and player.y < py + 20 and player.y + player.height > py - 20):
                        pu['collected'] = True
                        powerup_sound.play() 
                        if pu['type'] == "BRIDGE": active_bridge_timer = 300 
                        elif pu['type'] == "SPEED": active_speed_timer = 240 
                        elif pu['type'] == "MEGA_JUMP": player.mega_jump_active = True; player.jump_power = -18.5
                        elif pu['type'] == "SLOW_GHOST": distance_to_ghost = min(max_distance, distance_to_ghost + 60)
                    else: draw_powerup(screen, pu['type'], px, py)

        for p in particles:
            ps = pygame.Surface((p["radius"]*2, p["radius"]*2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (p["color"][0], p["color"][1], p["color"][2], int(p["life"]*255)), (int(p["radius"]), int(p["radius"])), int(p["radius"]))
            screen.blit(ps, (p["x"]-p["radius"], p["y"]-p["radius"]))
            
        # Passo lo stato velocità al player per l'animazione
        player.draw(screen, active_speed_timer > 0); ghost.draw(screen)

        screen.blit(font_ui.render(f"x{score_multiplier}", True, YELLOW_COIN if active_speed_timer > 0 else ORANGE), (30, 20))
        screen.blit(font_ui.render(f"{int(subway_score):06d}", True, WHITE), (85, 20))
        screen.blit(font_ui.render(f"🪙 {coins_collected}", True, YELLOW_COIN), (WIDTH - 150, 20))

        if state == "COUNTDOWN":
            secs = math.ceil(countdown_timer / 60)
            txt_cd = font_massive.render(str(secs) if secs > 0 else "SCAPPA!", True, YELLOW_COIN)
            screen.blit(txt_cd, (WIDTH//2 - txt_cd.get_width()//2, HEIGHT//2 - txt_cd.get_height()//2 - 50))

    # --- STATO: CADUTA / JUMPSCARE / GAMEOVER ---
    elif state == "DYING_FALL":
        death_timer += 1
        for b in bg_buildings: pygame.draw.rect(screen, COLOR_BG_BUILDINGS, (b["x"], HEIGHT - b["h"], b["w"], b["h"]))
        for b in mid_buildings: pygame.draw.rect(screen, COLOR_MID_BUILDINGS, (b["x"], HEIGHT - b["h"], b["w"], b["h"]))
        for plat in platforms:
            pygame.draw.rect(screen, COLOR_FOREGROUND, (plat['x'], plat['y'], plat['w'], HEIGHT - plat['y'])); pygame.draw.rect(screen, COLOR_LEDGE, (plat['x'], plat['y'], plat['w'], 12))
        player.y += 4.2; player.hat_x += player.hat_vx; player.hat_y += player.hat_vy; player.hat_vy += 0.35 
        player.draw(screen)
        
        hs = pygame.Surface((40, 40), pygame.SRCALPHA); pygame.draw.polygon(hs, (40, 100, 200), [(5, 25), (35, 25), (15, 5)]); pygame.draw.circle(hs, WHITE, (15, 5), 4)
        screen.blit(pygame.transform.rotate(hs, global_time * 6), (player.hat_x, player.hat_y))
        
        if death_timer >= 65:
            state, gameover_timer = "GAMEOVER", 0
            if int(subway_score) > high_score: high_score = int(subway_score); save_high_score(high_score)
            death_msg = random.choice(fall_phrases)

    elif state == "JUMPSCARE":
        jumpscare_timer += 1
        screen.fill((0, 0, 0) if jumpscare_timer % 4 < 2 else (35, 0, 0))
        cx, cy = WIDTH // 2 + random.randint(-25, 25), HEIGHT // 2 + random.randint(-25, 25)
        
        pygame.draw.circle(screen, (235, 235, 245), (cx, cy), 230); pygame.draw.circle(screen, (190, 190, 210), (cx - 90, cy + 30), 150); pygame.draw.circle(screen, (190, 190, 210), (cx + 90, cy + 30), 150)
        pygame.draw.ellipse(screen, (10, 10, 20), (cx - 140, cy - 90, 100, 140)); pygame.draw.ellipse(screen, (10, 10, 20), (cx + 40, cy - 90, 100, 140))
        pygame.draw.circle(screen, RED, (cx - 90, cy - 20), 28); pygame.draw.circle(screen, RED, (cx + 90, cy - 20), 28); pygame.draw.circle(screen, WHITE, (cx - 90, cy - 20), 8); pygame.draw.circle(screen, WHITE, (cx + 90, cy - 20), 8)
        pygame.draw.ellipse(screen, (5, 5, 10), (cx - 170, cy + 40, 340, 150))
        for tx in range(cx - 150, cx + 170, 28):
            pygame.draw.polygon(screen, WHITE, [(tx, cy + 50), (tx + 14, cy + 95), (tx + 28, cy + 50)]); pygame.draw.polygon(screen, WHITE, [(tx, cy + 180), (tx + 14, cy + 135), (tx + 28, cy + 180)])
        for _ in range(10):
            ly = random.randint(0, HEIGHT); pygame.draw.line(screen, RED, (0, ly), (WIDTH, ly), random.randint(1, 3))
            
        if jumpscare_timer >= 50: 
            state, gameover_timer = "GAMEOVER", 0
            if int(subway_score) > high_score: high_score = int(subway_score); save_high_score(high_score)
            death_msg = "L'INCUBO TI HA INGOIATO!"

    elif state == "GAMEOVER":
        gameover_timer += 1
        for b in bg_buildings: pygame.draw.rect(screen, COLOR_BG_BUILDINGS, (b["x"], HEIGHT - b["h"], b["w"], b["h"]))
        for b in mid_buildings: pygame.draw.rect(screen, COLOR_MID_BUILDINGS, (b["x"], HEIGHT - b["h"], b["w"], b["h"]))
        for plat in platforms: pygame.draw.rect(screen, COLOR_FOREGROUND, (plat['x'], plat['y'], plat['w'], HEIGHT - plat['y'])); pygame.draw.rect(screen, COLOR_LEDGE, (plat['x'], plat['y'], plat['w'], 12))
            
        progress = min(1.0, gameover_timer / 75.0) 
        sw, sh = int(font_massive.render("SEI MORTO", True, RED).get_width() * (0.35 + 0.65 * progress)), int(font_massive.render("SEI MORTO", True, RED).get_height() * (0.35 + 0.65 * progress))
        if sw > 0 and sh > 0:
            scaled_text = pygame.transform.smoothscale(font_massive.render("SEI MORTO", True, RED), (sw, sh)); scaled_text.set_alpha(int(255 * progress)); screen.blit(scaled_text, (WIDTH//2 - sw//2, 130 - sh//2))
            
        if gameover_timer > 55:
            sub_alpha = int(255 * min(1.0, (gameover_timer - 55) / 25.0))
            go_t, go_s, go_hint = font_ui.render(death_msg, True, WHITE), font_sub.render(f"Punteggio: {int(subway_score)}  |  Monete: {coins_collected}", True, (200, 200, 200)), font_sub.render("Premi SPAZIO per tornare al Menu", True, YELLOW_COIN)
            for t in [go_t, go_s, go_hint]: t.set_alpha(sub_alpha)
            screen.blit(go_t, (WIDTH//2 - go_t.get_width()//2, 240)); screen.blit(go_s, (WIDTH//2 - go_s.get_width()//2, 300)); screen.blit(go_hint, (WIDTH//2 - go_hint.get_width()//2, 370))

    pygame.display.flip()
    clock.tick(60)
