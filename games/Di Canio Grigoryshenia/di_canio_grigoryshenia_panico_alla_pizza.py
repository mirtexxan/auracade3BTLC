"""
🎮 SOFIA & GIULIA: Panico Alla Pizza! 🍕
===================================
Progetto scolastico di Sofia Grygoryshena & Giulia Dicanio
Realizzato con Python + Pygame

COME SI GIOCA:
  - Scegli il tuo personaggio (Sofia o Giulia)
  - Muoviti a SINISTRA / DESTRA con i tasti freccia
  - Prendi le pizze 🍕 per guadagnare punti
  - Evita le bombe 💣 (perdi una vita!)
  - Raccogli le stelle ⭐ per punti bonus
  - Hai 3 vite. Sopravvivi il più a lungo possibile!
  - Premi ESC per uscire, R per ricominciare
"""

import pygame
import random
import math
import sys

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()

# Inizializzazione Mixer Audio protetta da try/except (per evitare crash se mancano casse/driver)
AUDIO_ENABLED = False
try:
    # Inizializziamo a 22050Hz, 8-bit unsigned, 1 canale mono
    pygame.mixer.init(frequency=22050, size=8, channels=1)
    AUDIO_ENABLED = True
except Exception as e:
    print(f"[AUDIO INFO] Nessun dispositivo audio rilevato: {e}. Il gioco funzionerà senza sonoro.")

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Sofia & Giulia: Pizza Panic! 🍕 - Progetto Scolastico")
clock = pygame.time.Clock()
FPS = 60

# ── Colors ────────────────────────────────────────────────────────────────────
WHITE      = (255, 255, 255)
BLACK      = (10,  10,  10)
RED        = (230,  60,  60)
ORANGE     = (255, 140,   0)
YELLOW     = (255, 220,  50)
GREEN      = ( 80, 200, 120)
PINK       = (255, 105, 180)
PURPLE     = (160,  32, 240)
CYAN       = ( 50, 220, 220)
DARK_BLUE  = ( 20,  20,  60)
SKY        = ( 30,  30,  80)
GOLD       = (255, 215,   0)
GRAY       = (160, 160, 160)
LIGHT_PINK = (255, 182, 193)
LAVENDER   = (200, 162, 200)

# ── Fonts ─────────────────────────────────────────────────────────────────────
try:
    font_big   = pygame.font.SysFont("comicsansms", 52, bold=True)
    font_med   = pygame.font.SysFont("comicsansms", 30, bold=True)
    font_small = pygame.font.SysFont("comicsansms", 20)
    font_tiny  = pygame.font.SysFont("comicsansms", 16)
except:
    font_big   = pygame.font.SysFont(None, 52)
    font_med   = pygame.font.SysFont(None, 30)
    font_small = pygame.font.SysFont(None, 22)
    font_tiny  = pygame.font.SysFont(None, 18)

# ── Generazione Suoni Via Codice (Sintesi Procedurale 8-Bit) ──────────────────
snd_pizza = None
snd_star  = None
snd_bomb  = None
bg_music  = None

if AUDIO_ENABLED:
    try:
        sample_rate = 22050

        # 1. Effetto CATTURA PIZZA (Tono ascendente veloce)
        duration = 0.15
        n_samples = int(sample_rate * duration)
        buf_pizza = bytearray(n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            freq = 400 + (i / n_samples) * 400
            val = int(128 + 30 * math.sin(2 * math.pi * freq * t))
            buf_pizza[i] = max(0, min(255, val))
        snd_pizza = pygame.mixer.Sound(buffer=buf_pizza)
        snd_pizza.set_volume(0.6)

        # 2. Effetto STELLA (Doppio tono magico squillante)
        duration = 0.3
        n_samples = int(sample_rate * duration)
        buf_star = bytearray(n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            freq = 900 if i < (n_samples // 2) else 1300
            val = int(128 + 25 * math.sin(2 * math.pi * freq * t))
            buf_star[i] = max(0, min(255, val))
        snd_star = pygame.mixer.Sound(buffer=buf_star)
        snd_star.set_volume(0.5)

        # 3. Effetto ESPLOSIONE BOMBA (Rumore bianco / Tono discendente distorto)
        duration = 0.4
        n_samples = int(sample_rate * duration)
        buf_bomb = bytearray(n_samples)
        for i in range(n_samples):
            t = i / sample_rate
            freq = max(60, 300 - (i / n_samples) * 260)
            noise = random.randint(-40, 40) * (1.0 - (i / n_samples))
            val = int(128 + 40 * math.sin(2 * math.pi * freq * t) + noise)
            buf_bomb[i] = max(0, min(255, val))
        snd_bomb = pygame.mixer.Sound(buffer=buf_bomb)
        snd_bomb.set_volume(0.8)

        # 4. NUOVA MUSICA DI SOTTOFONDO DOLCE E LENTA 🎵
        # Creiamo un loop più lungo (8 secondi) con onde sinusoidali morbide (tipo carillon/ninna nanna)
        duration_bg = 8.0
        n_samples_bg = int(sample_rate * duration_bg)
        buf_bg = bytearray(n_samples_bg)
        
        # Una progressione di note dolce e rilassante (Do, Sol, Lam, Fa) suonate lentamente
        melody = [261.63, 392.00, 440.00, 349.23, 261.63, 392.00, 523.25, 392.00]
        
        for i in range(n_samples_bg):
            t = i / sample_rate
            # Cambia nota lentamente, ogni 1.0 secondo
            note_idx = int(t / 1.0) % len(melody)
            freq = melody[note_idx]
            
            # Crea un effetto "Arpa/Carillon": la nota colpisce forte all'inizio del secondo e sfuma (decay)
            time_in_note = t % 1.0
            decay = max(0.0, 1.0 - (time_in_note / 1.0))
            
            # Onda sinusoidale pura (molto più dolce rispetto all'onda quadra metallica)
            val = int(128 + (20 * decay) * math.sin(2 * math.pi * freq * t))
            buf_bg[i] = max(0, min(255, val))
        
        bg_music = pygame.mixer.Sound(buffer=buf_bg)
        bg_music.set_volume(0.2) # Volume soffuso
        bg_music.play(loops=-1)   # Loop continuo

    except Exception as e:
        print(f"[AUDIO INFO] Errore nella generazione della musica dolce: {e}")

# Funzioni di riproduzione sicure
def play_sound(sound_obj):
    if AUDIO_ENABLED and sound_obj:
        try:
            sound_obj.play()
        except Exception:
            pass

# ── Helpers Grafici ───────────────────────────────────────────────────────────

def draw_text(surf, text, font, color, cx, cy, shadow=True):
    if shadow:
        s = font.render(text, True, BLACK)
        surf.blit(s, s.get_rect(center=(cx+2, cy+2)))
    img = font.render(text, True, color)
    surf.blit(img, img.get_rect(center=(cx, cy)))

def draw_rounded_rect(surf, color, rect, radius=12, alpha=255):
    tmp = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(tmp, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(tmp, (rect[0], rect[1]))

def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

# ── Disegno Personaggi ────────────────────────────────────────────────────────

def draw_sofia(surf, x, y, w=56, h=72, blink=False, moving=0):
    """Disegna Sofia: capelli biondi, vestito blu 🇺🇦"""
    pygame.draw.ellipse(surf, (70, 130, 200), (x - w//2, y - h//3, w, h//2 + 10))
    pts = [
        (x - w//2 - 6, y + h//4),
        (x + w//2 + 6, y + h//4),
        (x + w//2 + 14, y + h//2 + 10),
        (x - w//2 - 14, y + h//2 + 10),
    ]
    pygame.draw.polygon(surf, (100, 170, 255), pts)
    pygame.draw.rect(surf, (255, 200, 170), (x - 14, y + h//2 + 8, 11, 18))
    pygame.draw.rect(surf, (255, 200, 170), (x + 3,  y + h//2 + 8, 11, 18))
    pygame.draw.ellipse(surf, RED, (x - 18, y + h//2 + 22, 16, 8))
    pygame.draw.ellipse(surf, RED, (x + 3,  y + h//2 + 22, 16, 8))
    arm_off = int(math.sin(pygame.time.get_ticks() * 0.01) * 6) if moving else 0
    pygame.draw.line(surf, (255, 200, 170), (x - w//2, y - h//5), (x - w//2 - 10, y + arm_off), 7)
    pygame.draw.line(surf, (255, 200, 170), (x + w//2, y - h//5), (x + w//2 + 10, y - arm_off), 7)
    pygame.draw.rect(surf, (255, 200, 170), (x - 8, y - h//2 - 5, 16, 14))
    pygame.draw.circle(surf, (255, 210, 180), (x, y - h//2 - 18), 22)
    pygame.draw.circle(surf, YELLOW,  (x, y - h//2 - 18), 24)
    pygame.draw.circle(surf, (255, 210, 180), (x, y - h//2 - 18), 18)
    for i in range(4):
        pygame.draw.circle(surf, YELLOW, (x - 22, y - h//2 - 10 + i * 9), 5)
    for i in range(4):
        pygame.draw.circle(surf, YELLOW, (x + 22, y - h//2 - 10 + i * 9), 5)
    pygame.draw.polygon(surf, PINK, [(x - 14, y - h//2 - 38), (x, y - h//2 - 32), (x - 14, y - h//2 - 26)])
    pygame.draw.polygon(surf, PINK, [(x + 14, y - h//2 - 38), (x, y - h//2 - 32), (x + 14, y - h//2 - 26)])
    pygame.draw.circle(surf, RED, (x, y - h//2 - 32), 4)
    ey = y - h//2 - 20
    if blink:
        pygame.draw.line(surf, BLACK, (x - 8, ey), (x - 2, ey), 3)
        pygame.draw.line(surf, BLACK, (x + 2, ey), (x + 8, ey), 3)
    else:
        pygame.draw.circle(surf, (50, 80, 200), (x - 6, ey), 5)
        pygame.draw.circle(surf, (50, 80, 200), (x + 6, ey), 5)
        pygame.draw.circle(surf, WHITE, (x - 5, ey - 1), 2)
        pygame.draw.circle(surf, WHITE, (x + 7, ey - 1), 2)
    pygame.draw.arc(surf, (180, 60, 60), (x - 8, y - h//2 - 12, 16, 8), math.pi, 2*math.pi, 2)
    pygame.draw.circle(surf, LIGHT_PINK, (x - 14, y - h//2 - 14), 5)
    pygame.draw.circle(surf, LIGHT_PINK, (x + 14, y - h//2 - 14), 5)
    draw_text(surf, "Sofia", font_tiny, WHITE, x, y + h//2 + 36, shadow=True)


def draw_giulia(surf, x, y, w=56, h=72, blink=False, moving=0):
    """Disegna Giulia: capelli ricci scuri, vestito verde 🇮🇹"""
    pygame.draw.ellipse(surf, (40, 140, 70), (x - w//2, y - h//3, w, h//2 + 10))
    pts = [
        (x - w//2 - 6, y + h//4),
        (x + w//2 + 6, y + h//4),
        (x + w//2 + 16, y + h//2 + 10),
        (x - w//2 - 16, y + h//2 + 10),
    ]
    pygame.draw.polygon(surf, (80, 200, 100), pts)
    pygame.draw.rect(surf, (200, 150, 120), (x - 14, y + h//2 + 8, 11, 18))
    pygame.draw.rect(surf, (200, 150, 120), (x + 3,  y + h//2 + 8, 11, 18))
    pygame.draw.ellipse(surf, (80, 50, 30), (x - 18, y + h//2 + 22, 16, 8))
    pygame.draw.ellipse(surf, (80, 50, 30), (x + 3,  y + h//2 + 22, 16, 8))
    arm_off = int(math.sin(pygame.time.get_ticks() * 0.01) * 6) if moving else 0
    pygame.draw.line(surf, (200, 150, 120), (x - w//2, y - h//5), (x - w//2 - 10, y + arm_off), 7)
    pygame.draw.line(surf, (200, 150, 120), (x + w//2, y - h//5), (x + w//2 + 10, y - arm_off), 7)
    pygame.draw.rect(surf, (200, 150, 120), (x - 8, y - h//2 - 5, 16, 14))
    pygame.draw.circle(surf, (210, 160, 130), (x, y - h//2 - 18), 22)
    for angle in range(0, 360, 30):
        hx = x + int(26 * math.cos(math.radians(angle)))
        hy = (y - h//2 - 18) + int(22 * math.sin(math.radians(angle)))
        pygame.draw.circle(surf, (60, 30, 10), (hx, hy), 9)
    pygame.draw.circle(surf, (60, 30, 10), (x, y - h//2 - 38), 12)
    pygame.draw.circle(surf, (210, 160, 130), (x, y - h//2 - 18), 19)
    ey = y - h//2 - 20
    if blink:
        pygame.draw.line(surf, BLACK, (x - 8, ey), (x - 2, ey), 3)
        pygame.draw.line(surf, BLACK, (x + 2, ey), (x + 8, ey), 3)
    else:
        pygame.draw.circle(surf, (100, 60, 20), (x - 6, ey), 5)
        pygame.draw.circle(surf, (100, 60, 20), (x + 6, ey), 5)
        pygame.draw.circle(surf, WHITE, (x - 5, ey - 1), 2)
        pygame.draw.circle(surf, WHITE, (x + 7, ey - 1), 2)
    pygame.draw.arc(surf, (160, 50, 50), (x - 10, y - h//2 - 12, 20, 10), math.pi, 2*math.pi, 3)
    pygame.draw.circle(surf, LAVENDER, (x - 14, y - h//2 - 14), 5)
    pygame.draw.circle(surf, LAVENDER, (x + 14, y - h//2 - 14), 5)
    pygame.draw.circle(surf, GREEN, (x - 20, y - h//2 - 16), 3)
    pygame.draw.circle(surf, RED,   (x + 20, y - h//2 - 16), 3)
    draw_text(surf, "Giulia", font_tiny, WHITE, x, y + h//2 + 36, shadow=True)


def draw_pizza(surf, x, y, r=18, angle=0):
    pygame.draw.circle(surf, (240, 200, 100), (x, y), r)
    pygame.draw.circle(surf, (200, 60, 30), (x, y), int(r * 0.78))
    pygame.draw.circle(surf, (255, 230, 80), (x, y), int(r * 0.55))
    for tx, ty in [(-5, -4), (4, -6), (0, 5), (-6, 5), (6, 4)]:
        pygame.draw.circle(surf, RED, (x + tx, y + ty), 3)
    pygame.draw.circle(surf, (200, 150, 60), (x, y), r, 3)

def draw_bomb(surf, x, y, r=16, t=0):
    pygame.draw.circle(surf, (30, 30, 30), (x, y), r)
    pygame.draw.circle(surf, (70, 70, 70), (x - 4, y - 4), 5)
    fuse_y = y - r
    for i in range(5):
        fx = x + int(4 * math.sin(t * 0.2 + i))
        pygame.draw.circle(surf, (150, 100, 50), (fx, fuse_y - i * 3), 2)
    spark_col = YELLOW if (pygame.time.get_ticks() // 150) % 2 == 0 else ORANGE
    pygame.draw.circle(surf, spark_col, (x + int(4 * math.sin(t * 0.2)), fuse_y - 14), 4)

def draw_star(surf, x, y, r=16, color=GOLD, angle=0):
    pts = []
    for i in range(10):
        a = math.radians(angle + i * 36 - 90)
        ri = r if i % 2 == 0 else r * 0.45
        pts.append((x + ri * math.cos(a), y + ri * math.sin(a)))
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, WHITE, pts, 2)

def draw_arrows(surf, x, y):
    pygame.draw.polygon(surf, CYAN, [(x - 14, y), (x - 4, y - 8), (x - 4, y + 8)])
    pygame.draw.rect(surf, CYAN, (x - 4, y - 4, 8, 8))
    pygame.draw.polygon(surf, CYAN, [(x + 14, y), (x + 4, y - 8), (x + 4, y + 8)])
    pygame.draw.rect(surf, CYAN, (x - 4, y - 4, 8, 8))

def draw_background(surf, t):
    for row in range(H):
        ratio = row / H
        c = lerp_color(DARK_BLUE, (50, 20, 80), ratio)
        pygame.draw.line(surf, c, (0, row), (W, row))
    random.seed(42)
    for _ in range(60):
        sx = random.randint(0, W)
        sy = random.randint(0, H // 2)
        flicker = 0.5 + 0.5 * math.sin(t * 0.003 + sx * 0.1)
        br = int(100 + 155 * flicker)
        pygame.draw.circle(surf, (br, br, br), (sx, sy), 1 if flicker < 0.7 else 2)
    random.seed()
    pygame.draw.rect(surf, (60, 40, 20), (0, H - 70, W, 70))
    pygame.draw.rect(surf, (80, 55, 25), (0, H - 70, W, 8))
    for i in range(0, W, 60):
        pygame.draw.rect(surf, (70, 47, 22), (i, H - 70, 60, 70), 1)
    cloud_x = int(t * 0.03) % (W + 200) - 100
    for cx, cy, cw in [(cloud_x, 80, 90), (cloud_x + 250, 50, 70), (cloud_x + 500, 100, 110)]:
        for dx, dy, cr in [(0, 0, 22), (24, -8, 28), (48, 0, 22), (72, 4, 18)]:
            pygame.draw.circle(surf, (80, 70, 110), (cx + dx, cy + dy), cr)

# ── Sistema Particelle ────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color, text=None):
        self.x = x + random.randint(-20, 20)
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, -1)
        self.color = color
        self.life = 60
        self.text = text

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1

    def draw(self, surf):
        alpha = max(0, self.life / 60)
        if self.text:
            img = font_small.render(self.text, True, self.color)
            img.set_alpha(int(alpha * 255))
            surf.blit(img, (int(self.x) - img.get_width()//2, int(self.y)))
        else:
            size = max(2, int(6 * alpha))
            pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), size)

# ── Oggetti che cadono ────────────────────────────────────────────────────────

class FallingObj:
    PIZZA = "pizza"
    BOMB  = "bomb"
    STAR  = "star"

    def __init__(self, kind, level):
        self.kind = kind
        self.x = random.randint(40, W - 40)
        self.y = -30
        
        base_speed = 2.5 + level * 0.3
        if self.kind == self.BOMB:
            base_speed += (level - 1) * 0.5
            
        self.speed = random.uniform(base_speed, base_speed + 2)
        self.angle = 0
        self.wobble = random.uniform(0, math.pi * 2)
        self.t = 0

    def update(self):
        self.y += self.speed
        self.angle = (self.angle + 3) % 360
        self.t += 1
        self.x += math.sin(self.wobble + self.t * 0.04) * 1.2

    def draw(self, surf):
        ix, iy = int(self.x), int(self.y)
        if self.kind == self.PIZZA:
            draw_pizza(surf, ix, iy, angle=self.angle)
        elif self.kind == self.BOMB:
            draw_bomb(surf, ix, iy, t=self.t)
        elif self.kind == self.STAR:
            draw_star(surf, ix, iy, angle=self.angle, color=GOLD)

    def rect(self):
        return pygame.Rect(self.x - 18, self.y - 18, 36, 36)

    def off_screen(self):
        return self.y > H

# ── Player ────────────────────────────────────────────────────────────────────

class Player:
    SPEED = 5

    def __init__(self, char):
        self.char = char
        self.x = W // 2
        self.y = H - 70 - 50
        self.lives = 3
        self.score = 0
        self.moving = 0
        self.blink = False
        self.blink_timer = 0
        self.hurt_timer = 0
        self.caught_timer = 0
        self.caught_text = ""

    def move(self, keys):
        self.moving = 0
        if keys[pygame.K_LEFT]:
            self.x = max(30, self.x - self.SPEED)
            self.moving = -1
        if keys[pygame.K_RIGHT]:
            self.x = min(W - 30, self.x + self.SPEED)
            self.moving = 1

    def update(self):
        self.blink_timer += 1
        if self.blink_timer >= 90:
            self.blink = True
        if self.blink_timer >= 95:
            self.blink = False
            self.blink_timer = 0
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        if self.caught_timer > 0:
            self.caught_timer -= 1

    def draw(self, surf):
        flash = (self.hurt_timer // 5) % 2 == 1
        if flash:
            return
        if self.char == "sofia":
            draw_sofia(surf, self.x, self.y, blink=self.blink, moving=self.moving)
        else:
            draw_giulia(surf, self.x, self.y, blink=self.blink, moving=self.moving)

    def rect(self):
        return pygame.Rect(self.x - 28, self.y - 50, 56, 100)

# ── Stati di Gioco ────────────────────────────────────────────────────────────

STATE_SELECT  = "select"
STATE_PLAY    = "play"
STATE_DEAD    = "dead"

# ── Game Loop Principale ──────────────────────────────────────────────────────

def main():
    state = STATE_SELECT
    player = None
    objects = []
    particles = []
    spawn_timer = 0
    level = 1
    t = 0
    high_score = 0
    select_hover = None

    heart_surf = font_med.render("❤", True, RED)

    def spawn_object():
        r = random.random()
        if r < 0.60:
            return FallingObj(FallingObj.PIZZA, level)
        elif r < 0.85:
            return FallingObj(FallingObj.BOMB, level)
        else:
            return FallingObj(FallingObj.STAR, level)

    def restart(char):
        nonlocal objects, particles, spawn_timer, level, player
        player = Player(char)
        objects = []
        particles = []
        spawn_timer = 0
        level = 1

    while True:
        dt = clock.tick(FPS)
        t += 1
        keys = pygame.key.get_pressed()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if state == STATE_SELECT:
                    if ev.key == pygame.K_1:
                        restart("sofia"); state = STATE_PLAY
                    if ev.key == pygame.K_2:
                        restart("giulia"); state = STATE_PLAY
                if state == STATE_DEAD:
                    if ev.key == pygame.K_r:
                        state = STATE_SELECT
            if ev.type == pygame.MOUSEBUTTONDOWN and state == STATE_SELECT:
                mx, my = ev.pos
                if 180 < mx < 380 and 240 < my < 460:
                    restart("sofia"); state = STATE_PLAY
                if 420 < mx < 630 and 240 < my < 460:
                    restart("giulia"); state = STATE_PLAY
            if ev.type == pygame.MOUSEMOTION and state == STATE_SELECT:
                mx, my = ev.pos
                if 180 < mx < 380 and 240 < my < 460:
                    select_hover = "sofia"
                elif 420 < mx < 630 and 240 < my < 460:
                    select_hover = "giulia"
                else:
                    select_hover = None

        draw_background(screen, t)

        # ── STATO: SELEZIONE PERSONAGGIO ──────────────────────────────────────
        if state == STATE_SELECT:
            title_y = 80 + int(math.sin(t * 0.04) * 6)
            draw_text(screen, "🍕 PIZZA PANIC! 🍕", font_big, YELLOW, W//2, title_y)
            draw_text(screen, "L'Avventura Epica di Sofia & Giulia", font_small, CYAN, W//2, 130)
            draw_text(screen, "Scegli il tuo personaggio!", font_med, WHITE, W//2, 200)

            s_hover = select_hover == "sofia"
            draw_rounded_rect(screen, (100, 160, 255), (170, 240, 210, 220), radius=18, alpha=180 if not s_hover else 220)
            pygame.draw.rect(screen, YELLOW if s_hover else WHITE, (170, 240, 210, 220), 3, border_radius=18)
            draw_sofia(screen, 275, 370, blink=(t // 90) % 2 == 0)
            draw_text(screen, "Sofia", font_med, LIGHT_PINK, 275, 476)
            draw_text(screen, "[ Premi 1 ]", font_small, YELLOW, 275, 503)

            g_hover = select_hover == "giulia"
            draw_rounded_rect(screen, (60, 160, 90), (420, 240, 210, 220), radius=18, alpha=180 if not g_hover else 220)
            pygame.draw.rect(screen, YELLOW if g_hover else WHITE, (420, 240, 210, 220), 3, border_radius=18)
            draw_giulia(screen, 525, 370, blink=(t // 90) % 2 == 0)
            draw_text(screen, "Giulia", font_med, GREEN, 525, 476)
            draw_text(screen, "[ Premi 2 ]", font_small, YELLOW, 525, 503)

            draw_rounded_rect(screen, (20, 20, 50), (40, 525, 720, 50), radius=10, alpha=160)
            
            draw_pizza(screen, 65, 550, r=10)
            text_p = font_tiny.render("Prendi le pizze!", True, GRAY)
            screen.blit(text_p, (85, 540))
            
            draw_bomb(screen, 235, 550, r=9, t=t)
            text_b = font_tiny.render("Evita le bombe!", True, GRAY)
            screen.blit(text_b, (255, 540))

            draw_star(screen, 405, 550, r=9, color=GOLD)
            text_s = font_tiny.render("Raccogli le stelle!", True, GRAY)
            screen.blit(text_s, (425, 540))

            draw_arrows(screen, 600, 550)
            text_m = font_tiny.render("Muoviti", True, GRAY)
            screen.blit(text_m, (625, 540))

            draw_text(screen, f"🏆 Record: {high_score}", font_small, GOLD, W//2, 582)

        # ── STATO: IN PARTITA ─────────────────────────────────────────────────
        elif state == STATE_PLAY:
            new_level = 1
            if player.score >= 1000:   new_level = 6
            elif player.score >= 600:  new_level = 5
            elif player.score >= 400:  new_level = 4
            elif player.score >= 250:  new_level = 3
            elif player.score >= 100:  new_level = 2
            
            if new_level > level:
                level = new_level
                for _ in range(10):
                    particles.append(Particle(W//2, 200, GOLD, f"LIVELLO {level}!"))

            spawn_timer += 1
            spawn_rate = max(30, 75 - level * 4)
            if spawn_timer >= spawn_rate:
                objects.append(spawn_object())
                spawn_timer = 0

            player.move(keys)
            player.update()

            to_remove = []
            for obj in objects:
                obj.update()
                if obj.off_screen():
                    to_remove.append(obj)
                    continue
                if player.rect().colliderect(obj.rect()):
                    to_remove.append(obj)
                    if obj.kind == FallingObj.PIZZA:
                        play_sound(snd_pizza)
                        points = 10 * level
                        player.score += points
                        player.caught_timer = 30
                        player.caught_text = f"+{points}"
                        for _ in range(8):
                            particles.append(Particle(player.x, player.y - 40, ORANGE))
                        particles.append(Particle(player.x, player.y - 60, YELLOW, f"+{points}"))
                    elif obj.kind == FallingObj.BOMB:
                        play_sound(snd_bomb)
                        player.lives -= 1
                        player.hurt_timer = 60
                        for _ in range(12):
                            particles.append(Particle(player.x, player.y - 40, RED))
                        particles.append(Particle(player.x, player.y - 70, RED, "AHI! 💣"))
                        if player.lives <= 0:
                            high_score = max(high_score, player.score)
                            state = STATE_DEAD
                    elif obj.kind == FallingObj.STAR:
                        play_sound(snd_star)
                        bonus = 50 * level
                        player.score += bonus
                        for _ in range(14):
                            particles.append(Particle(player.x, player.y - 40, GOLD))
                        particles.append(Particle(player.x, player.y - 70, GOLD, f"+{bonus} ⭐"))

            for obj in to_remove:
                objects.remove(obj)

            for obj in objects:
                obj.draw(screen)

            player.draw(screen)

            for p in particles[:]:
                p.update()
                p.draw(screen)
                if p.life <= 0:
                    particles.remove(p)

            draw_rounded_rect(screen, (20, 20, 50), (0, 0, W, 52), radius=0, alpha=160)
            draw_text(screen, f"Punti: {player.score}", font_med, YELLOW, 120, 26)
            draw_text(screen, "Vite:", font_small, WHITE, W//2 - 60, 26)
            for i in range(player.lives):
                screen.blit(heart_surf, (W//2 - 10 + i * 30, 10))

            draw_text(screen, f"Livello: {level}", font_med, GREEN, W - 110, 26)

            if player.hurt_timer > 40:
                s = pygame.Surface((W, H), pygame.SRCALPHA)
                s.fill((255, 0, 0, 60))
                screen.blit(s, (0, 0))

        # ── STATO: SCONFITTA ──────────────────────────────────────────────────
        elif state == STATE_DEAD:
            draw_rounded_rect(screen, (20, 10, 40), (150, 130, 500, 340), radius=24, alpha=220)
            pygame.draw.rect(screen, GOLD, (150, 130, 500, 340), 3, border_radius=24)

            draw_text(screen, "GAME OVER! 😭", font_big, RED, W//2, 200)
            draw_text(screen, f"Punteggio finale: {player.score}", font_med, YELLOW, W//2, 270)
            draw_text(screen, f"🏆 Record: {high_score}", font_med, GOLD, W//2, 315)
            char_name = "Sofia 🇺🇦" if player.char == "sofia" else "Giulia 🇮🇹"
            draw_text(screen, f"Personaggio: {char_name}", font_small, CYAN, W//2, 360)
            draw_text(screen, "Premi R per tornare al menu", font_small, WHITE, W//2, 420)

            if player.char == "sofia":
                draw_sofia(screen, W//2, 530, blink=True)
            else:
                draw_giulia(screen, W//2, 530, blink=True)

        pygame.display.flip()


if __name__ == "__main__":
    main()
