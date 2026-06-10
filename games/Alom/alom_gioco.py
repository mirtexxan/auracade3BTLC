import math
import random
import sys
import time

import pygame


pygame.init()

# Robust audio management
HAS_SOUND = True
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
except pygame.error as e:
    print(f"Nota: Inizializzazione audio fallita ({e}). Il gioco funzionerà senza sonoro.")
    HAS_SOUND = False

# ── basic constants ────────────────────────────────────────────────────────────
W, H = 1024, 600
HH = H // 2
FPS = 60

FOV = math.pi / 3
HALF_FOV = FOV / 2
NUM_RAYS = 180
STEP_ANGLE = FOV / NUM_RAYS
MAX_DEPTH = 20
SCALE = W // NUM_RAYS
TILE = 1.0  

PLAYER_MOVE_SPEED = 1.5  
PLAYER_ROT_SPEED = 1.2   
MOUSE_SENS = 0.0015      

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DKRED = (120, 20, 20)
GREEN = (60, 200, 80)
BLUE = (80, 120, 220)
YELLOW = (240, 220, 80)
PURPLE = (180, 80, 200)
GREY = (120, 120, 120)
DKGREY = (40, 40, 40)
SCHOOL_GREEN = (82, 182, 154) # Custom #52b69a wall color
BOSS_WALL_COL = (80, 20, 60)  # Dark purple tint for boss arena walls

BOSS_PUNISHMENTS = [
    "Brutto Voto",
    "Nota sul Registro",
    "Chiamare i genitori",
    "C.d.C.",
]

def load_image(filename):
    try:
        return pygame.image.load(filename).convert_alpha()
    except Exception:
        return None

# ── sound generation & loading ───────────────────────────────────────────────────
def make_tone(freq, duration, volume=0.3, wave="sine"):
    if not HAS_SOUND:
        return None
    import struct
    sr = 22050
    n = int(sr * duration)
    buf = bytearray(n * 4)  
    TAU = 2 * math.pi
    for i in range(n):
        t = i / sr
        if wave == "sine":
            s = math.sin(TAU * freq * t)
        elif wave == "square":
            s = 1.0 if math.sin(TAU * freq * t) >= 0 else -1.0
        elif wave == "noise":
            s = random.uniform(-1, 1)
        else:
            s = math.sin(TAU * freq * t)
        s *= (1 - i / n)  
        sample = max(-32768, min(32767, int(s * volume * 32767)))
        struct.pack_into("<hh", buf, i * 4, sample, sample)  
    return pygame.mixer.Sound(buffer=buf)

class SoundBank:
    def __init__(self):
        self.sounds = {}
        self._build()

    def _build(self):
        # Synth generated alerts
        self.sounds["shoot"] = make_tone(1800, 0.07, 0.4, "square")
        self.sounds["hurt"] = make_tone(140, 0.18, 0.5, "noise")
        self.sounds["gameover1"] = make_tone(400, 0.25, 0.35, "sine")
        self.sounds["gameover2"] = make_tone(260, 0.25, 0.35, "sine")
        self.sounds["gameover3"] = make_tone(160, 0.4, 0.35, "sine")
        self.sounds["pc"] = make_tone(900, 0.15, 0.5, "noise")
        self.sounds["boss_loop"] = make_tone(1200, 1.2, 0.25, "square")
        self.sounds["note"] = make_tone(900, 0.1, 0.35, "sine")
        
        # External mp3 hooks
        if HAS_SOUND:
            try:
                self.sounds["attenzione"] = pygame.mixer.Sound("attenzione.mp3")
                self.sounds["allarme"] = pygame.mixer.Sound("allarme.mp3")
                self.sounds["arrabiato"] = pygame.mixer.Sound("arrabiato.mp3")
            except Exception as e:
                print(f"Nota: Impossibile caricare file musicali MP3 esterni ({e}).")

    def play(self, name, vol=1.0, loops=0):
        s = self.sounds.get(name)
        if not s:
            return
        s.set_volume(vol)
        s.play(loops=loops)

SFX = SoundBank()

# ── level layout ───────────────────────────────────────────────────────────────
LEVELS = [
    [
        "######################",
        "#P...................#",
        "#....................#",
        "#....................#",
        "#....................#",
        "#....................#",
        "#....................#",
        "#....................#",
        "#....................#",
        "#....................#",
        "######################",
    ],
    [
        "############",
        "#..........#",
        "#..........#",
        "#..........#",
        "#....B.....#",
        "############",
    ],
]

class Map:
    def __init__(self, level_index: int):
        raw = LEVELS[level_index]
        self.h = len(raw)
        self.w = len(raw[0])
        self.grid = [[1 if ch == "#" else 0 for ch in row] for row in raw]
        
        self.player_start = (1.5, 1.5)
        self.pc_positions = []
        self.boss_spawn = None

        # Find layout metrics
        floor_positions = []
        for y, row in enumerate(raw):
            for x, ch in enumerate(row):
                wx = x + 0.5
                wy = y + 0.5
                if ch == "P":
                    self.player_start = (wx, wy)
                    floor_positions.append([wx, wy])
                elif ch == "B":
                    self.boss_spawn = (wx, wy)
                elif ch == ".":
                    floor_positions.append([wx, wy])

        # Random spawn setup for 3 PCs
        if level_index == 0 and len(floor_positions) >= 3:
            spawn_pool = [pos for pos in floor_positions if pos != [self.player_start[0], self.player_start[1]]]
            chosen_pcs = random.sample(spawn_pool, 3)
            for pc_coord in chosen_pcs:
                self.pc_positions.append([pc_coord[0], pc_coord[1], False])

        self.visited = [[False] * self.w for _ in range(self.h)]

    def cell_at(self, x, y):
        gx, gy = int(x), int(y)
        if gx < 0 or gy < 0 or gx >= self.w or gy >= self.h:
            return 1
        return self.grid[gy][gx]

    def walkable(self, x, y):
        return self.cell_at(x, y) == 0


# ── enemies and projectiles ───────────────────────────────────────────────────
class EnemyProfMattana:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.8  
        self.max_hp = 2
        self.hp = self.max_hp
        self.shoot_cooldown = 1.0  # Give player an initial buffer when spawning
        self.alert_sound_cooldown = 0.0

    def update(self, game, dt):
        px, py = game.player.x, game.player.y
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        if dist < 0.0001:
            return
            
        desired_min = 2.0
        desired_max = 3.0

        # Distance alert check: 3 seconds away from shooting threshold = 3.0 + (3 * 0.8) = 5.4 units
        if self.alert_sound_cooldown > 0:
            self.alert_sound_cooldown -= dt
        if dist < 5.4 and self.alert_sound_cooldown <= 0:
            SFX.play("attenzione", 0.8)
            self.alert_sound_cooldown = 6.0 

        if dist > desired_max:
            dirx = dx / dist
            diry = dy / dist
            step = self.speed * dt
            nx = self.x + dirx * step
            ny = self.y + diry * step
            if game.map.walkable(nx, self.y):
                self.x = nx
            if game.map.walkable(self.x, ny):
                self.y = ny

        self.shoot_cooldown -= dt
        if desired_min <= dist <= desired_max and self.shoot_cooldown <= 0:
            self.shoot_cooldown = 2.0  # Increased shooting cooldown by 1 second as requested
            angle = math.atan2(py - self.y, px - self.x)
            game.enemy_projectiles.append(Projectile(self.x, self.y, angle, friendly=False))


class BossMusci:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.max_hp = 100  # Shifted to 100 Aura scale
        self.hp = self.max_hp
        self.speed = 0.7
        self.shot_cooldown = 0.5
        self.has_shouted = False
        self.state_timer = 0.0

    def update(self, game, dt):
        px, py = game.player.x, game.player.y
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        self.state_timer += dt

        STOP_DISTANCE = 3.5 

        # Approach around 2 seconds, shout, stop, then open fire
        if dist > STOP_DISTANCE and not self.has_shouted:
            if dist > 0.0001:
                dirx = dx / dist
                diry = dy / dist
                step = self.speed * dt
                nx = self.x + dirx * step
                ny = self.y + diry * step
                if game.map.walkable(nx, self.y):
                    self.x = nx
                if game.map.walkable(self.x, ny):
                    self.y = ny
        else:
            if not self.has_shouted and self.state_timer >= 2.0:
                SFX.play("arrabiato", 0.9)
                self.has_shouted = True

        self.shot_cooldown -= dt
        if self.shot_cooldown <= 0 and (self.has_shouted and self.state_timer >= 2.0):
            self.shot_cooldown = 1.8
            angle = math.atan2(py - self.y, px - self.x)
            label = random.choice(BOSS_PUNISHMENTS)
            game.enemy_projectiles.append(
                Projectile(self.x, self.y, angle, friendly=False, label=label)
            )
            SFX.play("note", 0.7)


class Projectile:
    def __init__(self, x, y, angle, friendly=True, label=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.friendly = friendly
        self.label = label
        self.speed = 3.5 if (not friendly and label) else 7.0
        self.alive = True

    def update(self, game, dt):
        step = self.speed * dt
        self.x += math.cos(self.angle) * step
        self.y += math.sin(self.angle) * step
        if not game.map.walkable(self.x, self.y):
            self.alive = False
            return

        if self.friendly:
            if game.state == "level1":
                for e in game.army[:]:
                    if math.hypot(e.x - self.x, e.y - self.y) < 0.4:
                        e.hp -= 1
                        self.alive = False
                        if e.hp <= 0:
                            game.army.remove(e)
                            game.on_army_defeated()
                        break
            elif game.state == "level2" and game.boss:
                if math.hypot(game.boss.x - self.x, game.boss.y - self.y) < 0.6:
                    game.boss.hp -= 10  # Reduced by 10 Aura units per hit
                    self.alive = False
        else:
            if math.hypot(game.player.x - self.x, game.player.y - self.y) < 0.4:
                game.hit_player(1)  # Decreased by 1 Voto point per hit
                self.alive = False


# ── player ─────────────────────────────────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0.0
        self.hp = 10  # Player metric setup to 10 Voto units
        self.max_hp = 10
        self.shoot_cooldown = 0.0


# ── core game object ──────────────────────────────────────────────────────────
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.real_display = pygame.Surface((W, H)) 
        self.clock = pygame.time.Clock()
        self.font_sm = pygame.font.SysFont("consolas", 16)
        self.font_md = pygame.font.SysFont("consolas", 24)
        self.font_lg = pygame.font.SysFont("consolas", 52, bold=True)
        self.font_xl = pygame.font.SysFont("consolas", 32, bold=True)

        self.gun_image = load_image("gun.png")
        self.pc_image = load_image("pc.png")
        self.crashed_pc_image = load_image("crashed_pc.png")
        self.enemy_image = load_image("enemy.png")
        self.musci_image = load_image("musci.png")

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

        self.reset()

    def reset(self):
        if HAS_SOUND:
            pygame.mixer.stop()
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        
        self.state = "game_start_delay"
        self.start_delay_timer = 1.2  
        
        self.cutscene_index = 0
        self.cutscene_char_index = 0
        self.cutscene_typing_timer = 0.0
        self.cutscene_typing_done = False
        self.cutscene_hold_timer = 0.0
        self.cutscene_messages = [
            "Oggi non ho proprio voglia di fare i compiti...",
            "L'unico modo per salvarmi è mandare in crash i 3 PC della scuola!",
            "Ma devo fare molta attenzione... la Prof. Mattana sta pattugliando la classe!"
        ]
        
        self.level1_end_messages = [
            "Ottimo! Tutti e 3 i PC sono andati in crash! Il Prof. Musci non potrà assegnare compiti oggi!",
            "Aspetta... cosa sta succedendo? La stanza sta girando...",
            "No no no... ti hanno beccato! Sei convocato davanti a Musci!",
        ]
        
        self.map = Map(0)
        self.player = Player(*self.map.player_start)
        self.army = []
        self.army_waves_total = 10  
        self.army_waves_spawned = 0
        self.pcs_destroyed = 0
        self.time_left = 90.0
        self.flash_timer = 0.0
        self.projectiles = []
        self.enemy_projectiles = []
        self.boss = None
        self.damage_flash = 0.0
        self.recoil = 0.0
        self.shake_time = 0.0
        
        self._graffiti = [
            (2.05, 4.5,  "Viva  l'informatica!"),         
            (18.95, 3.5, "La  A  in  Alom  sta  per  aura"),
            (10.5, 8.45, "Aura  di  Musci  +1000"),        
        ]
        self.reveal_full_minimap()
        self.spawn_next_army()

    def reveal_full_minimap(self):
        for y in range(self.map.h):
            for x in range(self.map.w):
                self.map.visited[y][x] = True

    def get_random_spawn_point(self):
        # Spawns outside a certain range of the player (at least 5.0 units away)
        candidates = []
        for y in range(self.map.h):
            for x in range(self.map.w):
                if self.map.grid[y][x] == 0:
                    wx, wy = x + 0.5, y + 0.5
                    if math.hypot(wx - self.player.x, wy - self.player.y) >= 5.0:
                        candidates.append((wx, wy))
        if candidates:
            return random.choice(candidates)
        
        # Fallback if map layout configuration constraints fail
        return self.player.x + 4.0, self.player.y + 4.0

    def spawn_next_army(self):
        if self.army_waves_spawned >= self.army_waves_total:
            return
        sx, sy = self.get_random_spawn_point()
        self.army = [EnemyProfMattana(sx, sy)]
        self.army_waves_spawned += 1

    def on_army_defeated(self):
        if self.army:
            return
        if self.army_waves_spawned < self.army_waves_total:
            self.spawn_next_army()

    def hit_player(self, damage):
        if self.state not in ("level1", "level2"):
            return
        if self.player.hp <= 0:
            return
        self.player.hp -= damage
        self.damage_flash = 0.25
        self.shake_time = 0.2  
        SFX.play("hurt", 0.8)
        if self.player.hp <= 0:
            self.player.hp = 0
            self.start_game_over()

    def start_game_over(self):
        self.state = "gameover"
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        SFX.play("gameover1", 0.6)
        SFX.play("gameover2", 0.6)
        SFX.play("gameover3", 0.6)

    def start_transition_to_level2(self):
        self.state = "transition"
        self.flash_timer = 1.5  
        self.time_left = 0.0

    def enter_level2(self):
        self.state = "level2"
        self.map = Map(1)
        self.player.x, self.player.y = self.map.player_start
        self.player.angle = 0.0
        self.projectiles.clear()
        self.enemy_projectiles.clear()
        self.boss = BossMusci(*self.map.boss_spawn)
        self.reveal_full_minimap()
        SFX.play("boss_loop", 0.3, loops=-1)

    def win(self):
        self.state = "victory"
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)
        if HAS_SOUND:
            pygame.mixer.stop()

    def handle_movement(self, dt):
        keys = pygame.key.get_pressed()
        mx, _ = pygame.mouse.get_rel()
        self.player.angle += mx * MOUSE_SENS

        if keys[pygame.K_LEFT]:
            self.player.angle -= PLAYER_ROT_SPEED * dt
        if keys[pygame.K_RIGHT]:
            self.player.angle += PLAYER_ROT_SPEED * dt

        move_dir_x = 0.0
        move_dir_y = 0.0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_dir_x += math.cos(self.player.angle)
            move_dir_y += math.sin(self.player.angle)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_dir_x -= math.cos(self.player.angle)
            move_dir_y -= math.sin(self.player.angle)
        if keys[pygame.K_a]:
            move_dir_x += math.cos(self.player.angle - math.pi / 2)
            move_dir_y += math.sin(self.player.angle - math.pi / 2)
        if keys[pygame.K_d]:
            move_dir_x += math.cos(self.player.angle + math.pi / 2)
            move_dir_y += math.sin(self.player.angle + math.pi / 2)

        length = math.hypot(move_dir_x, move_dir_y)
        if length > 0:
            move_dir_x /= length
            move_dir_y /= length
            step = PLAYER_MOVE_SPEED * dt
            nx = self.player.x + move_dir_x * step
            ny = self.player.y + move_dir_y * step

            if self.map.walkable(nx, ny):
                self.player.x, self.player.y = nx, ny
            else:
                if self.map.walkable(nx, self.player.y):
                    self.player.x = nx
                if self.map.walkable(self.player.x, ny):
                    self.player.y = ny

        gx, gy = int(self.player.x), int(self.player.y)
        if 0 <= gx < self.map.w and 0 <= gy < self.map.h:
            self.map.visited[gy][gx] = True

    # ── raycasting ────────────────────────────────────────────────────────────
    def cast_rays(self, boss_mode=False):
        zbuf = []
        for ray in range(NUM_RAYS):
            ray_angle = self.player.angle - HALF_FOV + ray * STEP_ANGLE
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            depth = 0.03
            while depth < MAX_DEPTH:
                tx = self.player.x + cos_a * depth
                ty = self.player.y + sin_a * depth
                if self.map.cell_at(tx, ty) == 1:
                    break
                depth += 0.03

            corrected = depth * math.cos(self.player.angle - ray_angle)
            zbuf.append(corrected)

            if corrected <= 0:
                wall_h = H
            else:
                wall_h = min(H, int(H / corrected))

            wall_top = HH - wall_h // 2
            x_start = int(ray * (W / NUM_RAYS))
            x_end = int((ray + 1) * (W / NUM_RAYS))
            current_scale = x_end - x_start

            # Well-lit roof and floor surfaces
            pygame.draw.rect(self.real_display, (220, 220, 220), (x_start, 0, current_scale, max(0, wall_top)))
            pygame.draw.rect(self.real_display, (70, 75, 80), (x_start, wall_top + wall_h, current_scale, H - wall_top - wall_h))

            # Render logic for bi-color school walls
            if not boss_mode:
                green_height = int(wall_h * 0.40)
                white_height = wall_h - green_height
                pygame.draw.rect(self.real_display, (245, 245, 245), (x_start, wall_top, current_scale, white_height))
                pygame.draw.rect(self.real_display, SCHOOL_GREEN, (x_start, wall_top + white_height, current_scale, green_height))
            else:
                shade = max(0.4, 1 - corrected / MAX_DEPTH)
                b_col = (int(BOSS_WALL_COL[0] * shade), int(BOSS_WALL_COL[1] * shade), int(BOSS_WALL_COL[2] * shade))
                pygame.draw.rect(self.real_display, b_col, (x_start, wall_top, current_scale, wall_h))

        return zbuf

    # ── drawing helpers ───────────────────────────────────────────────────────
    def draw_world_sprite(self, wx, wy, zbuf, image=None, fallback_color=(200, 60, 60),
                          label=None, hp=None, max_hp=None):
        dx = wx - self.player.x
        dy = wy - self.player.y
        dist = math.hypot(dx, dy)
        if dist < 0.1:
            return
        angle = math.atan2(dy, dx) - self.player.angle
        while angle < -math.pi: angle += 2 * math.pi
        while angle > math.pi: angle -= 2 * math.pi
        if abs(angle) > HALF_FOV * 1.1:
            return

        screen_x = int((angle / FOV + 0.5) * W)
        size = int(H / dist)
        ray_idx = int(screen_x / SCALE)
        if 0 <= ray_idx < NUM_RAYS and zbuf[ray_idx] < dist:
            return

        sprite_h = max(20, min(H, size))
        sprite_w = sprite_h
        x0 = screen_x - sprite_w // 2
        y0 = HH - sprite_h // 2

        if image:
            scaled = pygame.transform.smoothscale(image, (sprite_w, sprite_h))
            self.real_display.blit(scaled, (x0, y0))
        else:
            pygame.draw.rect(self.real_display, fallback_color, (x0, y0, sprite_w, sprite_h))

        if hp is not None and max_hp is not None and max_hp > 0 and sprite_h > 15:
            ratio = max(0.0, hp / max_hp)
            bw = max(20, sprite_w)
            bx = screen_x - bw // 2
            by = y0 - 12
            pygame.draw.rect(self.real_display, DKRED, (bx, by, bw, 6))
            pygame.draw.rect(self.real_display, GREEN, (bx, by, int(bw * ratio), 6))

        if label and sprite_h > 25:
            txt = self.font_sm.render(label, True, BLACK)
            bar_offset = 20 if (hp is not None and max_hp is not None and sprite_h > 15) else 4
            self.real_display.blit(txt, (screen_x - txt.get_width() // 2, y0 - bar_offset - txt.get_height()))

    def draw_graffiti(self, wx, wy, text, zbuf):
        dx = wx - self.player.x
        dy = wy - self.player.y
        dist = math.hypot(dx, dy)
        if dist < 0.3 or dist > 16:
            return
        angle = math.atan2(dy, dx) - self.player.angle
        while angle < -math.pi: angle += 2 * math.pi
        while angle > math.pi: angle -= 2 * math.pi
        if abs(angle) > HALF_FOV * 1.05:
            return
        ray_idx = int((angle / FOV + 0.5) * NUM_RAYS)
        
        # Z-Layering adjustment: graffiti always renders closely integrated into wall boundaries
        if 0 <= ray_idx < NUM_RAYS and (zbuf[ray_idx] + 0.01) < dist:
            return
            
        screen_x = int((angle / FOV + 0.5) * W)
        size = max(18, min(54, int(32 / dist * 4.5)))
        
        fnt = pygame.font.SysFont("arial", size, bold=True)
        graffiti_color = (235, 30, 30)
        
        surf = fnt.render(text, True, graffiti_color)
        shadow = fnt.render(text, True, (0, 0, 0))
        
        sx = screen_x - surf.get_width() // 2
        
        wall_h = min(H, int(H / dist)) if dist > 0 else H
        white_zone_center = HH - (wall_h // 2) + int(wall_h * 0.30)
        sy = white_zone_center - surf.get_height() // 2
        
        for ox, oy in ((-2, 2), (2, 2), (-2, -2), (2, -2)):
            self.real_display.blit(shadow, (sx + ox, sy + oy))
        self.real_display.blit(surf, (sx, sy))

    def draw_minimap(self):
        cell_px = 11
        mw = self.map.w * cell_px
        mh = self.map.h * cell_px
        ox, oy = 10, 10

        surf = pygame.Surface((mw, mh), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 170))

        for y in range(self.map.h):
            for x in range(self.map.w):
                if not self.map.visited[y][x]:
                    continue
                c = self.map.grid[y][x]
                col = (110, 115, 120) if c == 0 else (150, 140, 120)
                pygame.draw.rect(surf, col, (x * cell_px, y * cell_px, cell_px, cell_px))

        for pc in self.map.pc_positions:
            pcx, pcy, destroyed = pc
            cx = int(pcx) * cell_px + cell_px // 4
            cy = int(pcy) * cell_px + cell_px // 4
            col = GREEN if not destroyed else (30, 80, 30)
            pygame.draw.rect(surf, col, (cx, cy, cell_px // 2, cell_px // 2))

        if self.state in ("level1", "game_start_delay", "intro_cutscene"):
            for e in self.army:
                ex = int(e.x * cell_px)
                ey = int(e.y * cell_px)
                pygame.draw.rect(surf, RED, (ex - 3, ey - 3, 6, 6))
        elif self.state == "level2" and self.boss:
            ex = int(self.boss.x * cell_px)
            ey = int(self.boss.y * cell_px)
            pygame.draw.rect(surf, PURPLE, (ex - 4, ey - 4, 8, 8))

        px = int(self.player.x * cell_px)
        py = int(self.player.y * cell_px)
        pygame.draw.circle(surf, BLUE, (px, py), 4)
        fx = px + int(math.cos(self.player.angle) * 8)
        fy = py + int(math.sin(self.player.angle) * 8)
        pygame.draw.line(surf, BLUE, (px, py), (fx, fy), 2)

        self.real_display.blit(surf, (ox, oy))
        pygame.draw.rect(self.real_display, WHITE, (ox, oy, mw, mh), 1)

    def draw_hud(self):
        sw, sh = self.screen.get_size()

        # Voto Health Bar mapping
        bw, bh = 220, 20
        x, y = 10, sh - 40
        pygame.draw.rect(self.real_display, DKGREY, (x, y, bw, bh))
        ratio = max(0.0, self.player.hp / self.player.max_hp)
        pygame.draw.rect(self.real_display, GREEN if ratio > 0.4 else RED, (x, y, int(bw * ratio), bh))
        pygame.draw.rect(self.real_display, WHITE, (x, y, bw, bh), 1)
        txt = self.font_md.render(f"Voto: {self.player.hp}/{self.player.max_hp}", True, WHITE)
        self.real_display.blit(txt, (x + 6, y - 26))

        if self.state in ("level1", "game_start_delay"):
            # Dynamic Countdown Timer layout color switching
            if self.time_left <= 10.0:
                tcol = RED
            elif self.time_left <= 20.0:
                tcol = YELLOW
            else:
                tcol = BLACK
                
            ttxt = self.font_md.render(f"Tempo: {int(self.time_left)}s", True, tcol)
            self.real_display.blit(ttxt, (sw // 2 - ttxt.get_width() // 2 + 80, 8))

            # Updated text lines to bright clear Red
            obj = self.font_sm.render(
                f"PC in crash: {self.pcs_destroyed}/3   |   Ondate Mattana: {min(self.army_waves_spawned, self.army_waves_total)}/{self.army_waves_total}",
                True,
                RED,
            )
            self.real_display.blit(obj, (sw // 2 - obj.get_width() // 2 + 80, 36))

            close_pc = any(
                (not pc[2]) and math.hypot(self.player.x - pc[0], self.player.y - pc[1]) < 1.0
                for pc in self.map.pc_positions
            )
            if close_pc and self.state == "level1":
                hint = self.font_xl.render("Premi 'F' per causare la Blue Screen!", True, RED)
                self.real_display.blit(hint, (sw // 2 - hint.get_width() // 2, sh // 2 - 80))

        elif self.state == "level2" and self.boss:
            # Boss Aura UI configuration
            bw, bh = 320, 18
            x, y = sw // 2 - bw // 2, 10
            pygame.draw.rect(self.real_display, DKGREY, (x, y, bw, bh))
            ratio = max(0.0, self.boss.hp / self.boss.max_hp)
            pygame.draw.rect(self.real_display, PURPLE, (x, y, int(bw * ratio), bh))
            pygame.draw.rect(self.real_display, WHITE, (x, y, bw, bh), 1)
            label = self.font_md.render(f"Prof. Musci (Aura: {self.boss.hp})", True, RED)
            self.real_display.blit(label, (sw // 2 - label.get_width() // 2, y + bh + 4))

        cx, cy = sw // 2, sh // 2
        pygame.draw.line(self.real_display, RED, (cx - 8, cy), (cx + 8, cy), 1)
        pygame.draw.line(self.real_display, RED, (cx, cy - 8), (cx, cy + 8), 1)
        
        if self.gun_image:
            img = self.gun_image
            gx = sw - img.get_width() - 20
            base_gy = sh - img.get_height() + 10
            gy = base_gy + int(self.recoil * 15)
            self.real_display.blit(img, (gx, gy))
        else:
            gun_w, gun_h = 40, 60
            gx = sw - gun_w - 30
            gy = sh - gun_h - 20 + int(self.recoil * 15)
            pygame.draw.rect(self.real_display, GREY, (gx, gy, gun_w, gun_h))
            pygame.draw.rect(self.real_display, BLACK, (gx + 8, gy + 8, gun_w - 16, gun_h - 24))

        instr = self.font_sm.render(
            "F = Difenditi dai Prof  |  F vicino al PC = Blue Screen",
            True,
            RED,
        )
        self.real_display.blit(instr, (sw // 2 - instr.get_width() // 2, sh - 24))

    def run(self):
        running = True
        while running:
            dt_ms = self.clock.tick(FPS)
            dt = dt_ms / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_r, pygame.K_RETURN) and self.state in ("gameover", "victory"):
                        self.reset()
                    elif self.state in ("intro_cutscene", "end_cutscene"):
                        self.advance_cutscene()
                    elif self.state in ("level1", "level2") and event.key == pygame.K_f:
                        if self.state == "level1" and self.try_infect_pc():
                            pass
                        else:
                            self.try_shoot()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and self.state in ("gameover", "victory"):
                        mx, my = event.pos
                        sw, sh = self.screen.get_size()
                        
                        # Match the exact button positions from draw screens
                        y_offset = 70 if self.state == "gameover" else 50
                        btn_rect = pygame.Rect(sw // 2 - 110, sh // 2 + y_offset, 220, 44)
                        
                        if btn_rect.collidepoint(mx, my):
                            self.reset()


            if self.state in ("level1", "level2"):
                self.handle_movement(dt)
                self.update_shooting(dt)

            if self.state == "level1":
                self.update_level1(dt)
            elif self.state == "game_start_delay":
                self.start_delay_timer -= dt
                if self.start_delay_timer <= 0:
                    self.state = "intro_cutscene"
            elif self.state in ("intro_cutscene", "end_cutscene"):
                self.update_cutscene(dt)
            elif self.state == "transition":
                self.update_transition(dt)
            elif self.state == "level2":
                self.update_level2(dt)

            self.draw()

        pygame.quit()
        sys.exit()

    def try_shoot(self):
        if self.player.shoot_cooldown > 0:
            return
        self.player.shoot_cooldown = 0.18
        px, py = self.player.x, self.player.y
        angle = self.player.angle
        self.projectiles.append(Projectile(px, py, angle, friendly=True))
        self.recoil = 1.0
        self.shake_time = 0.15  
        SFX.play("shoot", 0.7)

    def update_shooting(self, dt):
        self.player.shoot_cooldown = max(0.0, self.player.shoot_cooldown - dt)
        self.recoil = max(0.0, self.recoil - dt * 6.0)

        for p in self.projectiles[:]:
            p.update(self, dt)
            if not p.alive:
                self.projectiles.remove(p)

        for p in self.enemy_projectiles[:]:
            p.update(self, dt)
            if not p.alive:
                self.enemy_projectiles.remove(p)

    def update_level1(self, dt):
        self.time_left -= dt
        if self.time_left <= 0 and self.state == "level1":
            self.start_game_over()

        for e in self.army:
            e.update(self, dt)

        if self.pcs_destroyed >= 3 and self.state == "level1":
            self.state = "end_cutscene"
            self.cutscene_index = 0
            self.cutscene_char_index = 0
            self.cutscene_typing_timer = 0.0
            self.cutscene_typing_done = False
            self.cutscene_hold_timer = 0.0
            self.cutscene_messages = self.level1_end_messages

    def update_transition(self, dt):
        self.flash_timer -= dt
        if self.flash_timer <= 0:
            self.enter_level2()

    def update_cutscene(self, dt):
        if self.cutscene_index >= len(self.cutscene_messages):
            if self.state == "intro_cutscene":
                self.state = "level1"
            else:
                self.start_transition_to_level2()
            return

        if not self.cutscene_typing_done:
            self.cutscene_typing_timer += dt
            msg = self.cutscene_messages[self.cutscene_index]
            chars_per_sec = 45.0
            target = int(self.cutscene_typing_timer * chars_per_sec)
            self.cutscene_char_index = min(len(msg), target)
            if self.cutscene_char_index >= len(msg):
                self.cutscene_typing_done = True
                self.cutscene_hold_timer = 0.0
        else:
            self.cutscene_hold_timer += dt
            if self.cutscene_hold_timer >= 2.5:
                self.advance_cutscene()

    def advance_cutscene(self):
        if self.cutscene_index >= len(self.cutscene_messages):
            if self.state == "intro_cutscene":
                self.state = "level1"
            else:
                self.start_transition_to_level2()
            return

        msg = self.cutscene_messages[self.cutscene_index]
        if not self.cutscene_typing_done:
            self.cutscene_char_index = len(msg)
            self.cutscene_typing_done = True
            self.cutscene_hold_timer = 0.0
            return

        self.cutscene_index += 1
        self.cutscene_char_index = 0
        self.cutscene_typing_timer = 0.0
        self.cutscene_typing_done = False
        self.cutscene_hold_timer = 0.0
        if self.cutscene_index >= len(self.cutscene_messages):
            if self.state == "intro_cutscene":
                self.state = "level1"
            else:
                self.start_transition_to_level2()

    def update_level2(self, dt):
        if self.boss:
            self.boss.update(self, dt)
            if self.boss.hp <= 0:
                self.boss = None
                self.win()

    def try_infect_pc(self):
        if self.state != "level1":
            return False
        for pc in self.map.pc_positions:
            if pc[2]:
                continue
            if math.hypot(self.player.x - pc[0], self.player.y - pc[1]) < 1.0:
                pc[2] = True
                self.pcs_destroyed += 1
                
                if self.pcs_destroyed < 3:
                    SFX.play("allarme", 0.8)
                else:
                    SFX.play("pc", 0.9)
                return True
        return False

    def draw(self):
        boss_mode = self.state in ("level2", "victory")
        zbuf = self.cast_rays(boss_mode=boss_mode)

        render_queue = []

        if self.state in ("level1", "game_start_delay", "intro_cutscene", "end_cutscene"):
            # Z-Layering rules: Graffiti base distance offset applied so it remains behind active assets
            for gx, gy, gtxt in self._graffiti:
                dist = math.hypot(gx - self.player.x, gy - self.player.y)
                render_queue.append((dist + 0.05, "graffiti", (gx, gy, gtxt)))

            for pc in self.map.pc_positions:
                dist = math.hypot(pc[0] - self.player.x, pc[1] - self.player.y)
                render_queue.append((dist, "pc", pc))

            for e in self.army:
                dist = math.hypot(e.x - self.player.x, e.y - self.player.y)
                render_queue.append((dist - 0.05, "enemy", e))

        if self.state in ("level2", "victory") and self.boss:
            dist = math.hypot(self.boss.x - self.player.x, self.boss.y - self.player.y)
            render_queue.append((dist, "boss", self.boss))

        for proj in self.projectiles:
            dist = math.hypot(proj.x - self.player.x, proj.y - self.player.y)
            render_queue.append((dist, "player_proj", proj))

        for proj in self.enemy_projectiles:
            dist = math.hypot(proj.x - self.player.x, proj.y - self.player.y)
            render_queue.append((dist, "enemy_proj", proj))

        # Sorted strictly by descending depth order sequence
        render_queue.sort(key=lambda item: item[0], reverse=True)

        for dist, obj_type, data in render_queue:
            if obj_type == "graffiti":
                self.draw_graffiti(data[0], data[1], data[2], zbuf)
            elif obj_type == "pc":
                pc_img = self.crashed_pc_image if data[2] else self.pc_image
                self.draw_world_sprite(
                    data[0], data[1], zbuf,
                    image=pc_img,
                    fallback_color=(40, 220, 40) if not data[2] else (30, 80, 180),
                    label="PC" if not data[2] else "CRASHED",
                )
            elif obj_type == "enemy":
                self.draw_world_sprite(
                    data.x, data.y, zbuf,
                    image=self.enemy_image,
                    fallback_color=(200, 60, 60),
                    label="Prof. Mattana",
                    hp=data.hp,
                    max_hp=data.max_hp,
                )
            elif obj_type == "boss":
                self.draw_world_sprite(
                    data.x, data.y, zbuf,
                    image=self.musci_image,
                    fallback_color=(200, 40, 220),
                    label="Musci",
                    hp=data.hp,
                    max_hp=data.max_hp,
                )
            elif obj_type == "player_proj":
                angle = math.atan2(data.y - self.player.y, data.x - self.player.x) - self.player.angle
                if abs(angle) <= HALF_FOV:
                    sx = int((angle / FOV + 0.5) * W)
                    size = max(3, int(18 / dist))
                    pygame.draw.circle(self.real_display, YELLOW, (sx, HH), size)
            elif obj_type == "enemy_proj":
                angle = math.atan2(data.y - self.player.y, data.x - self.player.x) - self.player.angle
                if abs(angle) <= HALF_FOV:
                    sx = int((angle / FOV + 0.5) * W)
                    size = max(4, int(22 / dist))
                    pygame.draw.circle(self.real_display, PURPLE, (sx, HH), size)
                    if data.label and size > 8:
                        lbl = self.font_sm.render(data.label, True, YELLOW)
                        self.real_display.blit(lbl, (sx - lbl.get_width() // 2, HH - size - 18))

        if self.state in ("level1", "level2", "game_start_delay"):
            self.draw_minimap()
            self.draw_hud()
        elif self.state in ("intro_cutscene", "end_cutscene"):
            self.draw_minimap() 
            self.draw_cutscene_messages()
        elif self.state == "gameover":
            self.draw_game_over_screen()
        elif self.state == "victory":
            self.draw_victory_screen()

        if self.damage_flash > 0.0:
            self.damage_flash -= 1.0 / FPS
            alpha = int(200 * self.damage_flash)
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((200, 0, 0, max(0, alpha)))
            self.real_display.blit(flash, (0, 0))

        if self.state == "transition":
            alpha = int(255 * (1.0 - self.flash_timer / 1.5))
            flash = pygame.Surface((W, H), pygame.SRCALPHA)
            flash.fill((255, 255, 255, max(0, min(255, alpha))))
            self.real_display.blit(flash, (0, 0))

        # ── Screen Shake Calculations ─────────────────────────────────
        self.screen.fill(BLACK)
        if self.shake_time > 0.0:
            self.shake_time -= 1.0 / FPS
            shake_x = random.randint(-4, 4)
            shake_y = random.randint(-4, 4)
            self.screen.blit(self.real_display, (shake_x, shake_y))
        else:
            self.screen.blit(self.real_display, (0, 0))

        pygame.display.flip()

    def draw_restart_button(self, y_offset=70):
        sw, sh = self.screen.get_size()
        btn = pygame.Rect(sw // 2 - 110, sh // 2 + y_offset, 220, 44)
        pygame.draw.rect(self.real_display, GREEN, btn, border_radius=6)
        pygame.draw.rect(self.real_display, WHITE, btn, 2, border_radius=6)
        label = self.font_md.render("RICOMINCIA", True, BLACK)
        self.real_display.blit(label, (btn.centerx - label.get_width() // 2, btn.centery - label.get_height() // 2))
        hint = self.font_sm.render("[R] oppure clicca RICOMINCIA", True, GREY)
        self.real_display.blit(hint, (sw // 2 - hint.get_width() // 2, btn.bottom + 10))

    def draw_game_over_screen(self):
        self.real_display.fill(BLACK)
        title = self.font_lg.render("BOCCIATO!", True, RED)
        sw, sh = self.screen.get_size()
        self.real_display.blit(title, (sw // 2 - title.get_width() // 2, sh // 2 - 60))
        msg = self.font_md.render("Debito Totale in Informatica", True, WHITE)
        self.real_display.blit(msg, (sw // 2 - msg.get_width() // 2, sh // 2 + 10))
        self.draw_restart_button()

    def draw_victory_screen(self):
        t = time.time()
        col = (int(80 + 50 * math.sin(t * 6)), int(200 + 30 * math.sin(t * 4)), 80)
        self.real_display.fill(col)
        title = self.font_lg.render("MISSIONE COMPIUTA!", True, WHITE)
        sw, sh = self.screen.get_size()
        self.real_display.blit(title, (sw // 2 - title.get_width() // 2, sh // 2 - 40))
        sub = self.font_md.render("SI GODE! Niente compiti oggi!", True, BLACK)
        self.real_display.blit(sub, (sw // 2 - sub.get_width() // 2, sh // 2 + 30))
        self.draw_restart_button(90)

    def draw_cutscene_messages(self):
        if self.cutscene_index >= len(self.cutscene_messages):
            return

        sw, sh = self.screen.get_size()
        box_w, box_h = 860, 160
        bx = sw // 2 - box_w // 2
        by = sh // 2 - box_h // 2

        pygame.draw.rect(self.real_display, WHITE, (bx, by, box_w, box_h))
        pygame.draw.rect(self.real_display, BLACK, (bx, by, box_w, box_h), 3)

        msg = self.cutscene_messages[self.cutscene_index]
        visible = msg[: self.cutscene_char_index]
        text = self.font_md.render(visible, True, (20, 20, 20))
        text_rect = text.get_rect(center=(sw // 2, sh // 2))

        if text.get_width() > box_w - 40:
            words = visible.split()
            lines, line = [], []
            for word in words:
                test = " ".join(line + [word])
                if self.font_md.size(test)[0] > box_w - 40 and line:
                    lines.append(" ".join(line))
                    line = [word]
                else:
                    line.append(word)
            if line:
                lines.append(" ".join(line))
            y = by + 30
            for ln in lines:
                surf = self.font_md.render(ln, True, (20, 20, 20))
                self.real_display.blit(surf, (bx + 20, y))
                y += surf.get_height() + 8
        else:
            self.real_display.blit(text, text_rect)

        if self.cutscene_typing_done:
            hint = self.font_sm.render("Premi un tasto per continuare...", True, GREY)
            self.real_display.blit(hint, (sw // 2 - hint.get_width() // 2, by + box_h - 28))


# ── entry point ────────────────────────────────────────────────────────────────
def main():
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Dungeon di Musci - Progetto Informatica")
    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
