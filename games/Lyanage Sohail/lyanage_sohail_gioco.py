import pygame
import sys
import random
import math

pygame.init()

WIDTH, HEIGHT = 1000, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Divines & Darklings: Fight to the Death!")
clock = pygame.time.Clock()

WHITE       = (255, 255, 255)
BLACK       = (15, 15, 20)
GOLD        = (255, 215, 0)
PURPLE      = (120, 40, 140)
DARK_PURPLE = (40, 20, 60)
LIGHT_PINK  = (255, 220, 225)
SKIN_TONE   = (255, 218, 185)
HAIR_GOLD   = (245, 222, 179)
HAIR_BLACK  = (25, 25, 30)
RED         = (230, 40, 40)
GREEN       = (40, 220, 80)
CYAN        = (0, 235, 235)

STATE_THEME     = "theme_reveal"
STATE_SELECTION = "character_selection"
STATE_DRESSUP   = "dressup"
STATE_RUNWAY    = "runway"
STATE_RESULTS   = "results"
STATE_FIGHT     = "fight"
current_state = STATE_THEME

THEMES = [
    {"name": "GOTHIC ROYAL MET GALA", "hint": "Darklings love dark velvets; Divines need deep gold!", "best_angel": 2, "best_witch": 0},
    {"name": "NEON CYBERPUNK BLITZ", "hint": "Bright neon accents will drive the crowds wild!", "best_angel": 1, "best_witch": 1},
    {"name": "ANGELIC DIVINE LIGHT", "hint": "Purest whites and cosmic obsidian match this vibe!", "best_angel": 0, "best_witch": 2}
]
active_theme = random.choice(THEMES)

angel_options = [
    {"name": "Divine White Gown", "color": (250, 250, 250), "accent": (220, 240, 255)},
    {"name": "Neon Cyan Petal Dress", "color": (10, 200, 230), "accent": (255, 105, 180)},
    {"name": "Midnight Gold Robe", "color": (212, 175, 55), "accent": (40, 40, 60)}
]

witch_options = [
    {"name": "Nightshade Royal Velvet", "color": (45, 15, 65), "accent": (130, 0, 180)},
    {"name": "Acid Green Techno Cape", "color": (25, 25, 30), "accent": (50, 255, 50)},
    {"name": "Obsidian Thorn Armor", "color": (15, 15, 15), "accent": (100, 110, 120)}
]

angel_choice, witch_choice = 0, 0
player_role = None  
voted_winner = None  
animation_timer, robot_timer = 0, 0
score_angel, score_witch = 0, 0

angel_hp = 100
witch_hp = 100
game_over = False

angel_fight_x, angel_fight_y = 300, 250
witch_fight_x, witch_fight_y = 700, 250
current_action = ""
action_timer = 0
active_attacker = None  

audience_dots = [{"x": random.randint(0, WIDTH), "y": random.randint(430, 610), "base_y": 0, "size": random.randint(4, 7)} for _ in range(90)]
for d in audience_dots: d["base_y"] = d["y"]

font_sm = pygame.font.SysFont(None, 24)
font_md = pygame.font.SysFont(None, 32)
font_lg = pygame.font.SysFont(None, 64, bold=True)

class Button:
    def __init__(self, x, y, w, h, text, color, text_color=BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=10)
        txt = font_sm.render(self.text, True, self.text_color)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, pos): return self.rect.collidepoint(pos)

btn_play_game     = Button(400, 440, 200, 50, "PLAY GAME", GOLD)
btn_choose_divine = Button(190, 300, 240, 60, "CHOOSE DIVINE (ANGEL)", GOLD)
btn_choose_dark   = Button(570, 300, 240, 60, "CHOOSE DARKLING", PURPLE, WHITE)

btn_next_angel    = Button(125, 480, 150, 40, "Change Outfit", GOLD)
btn_next_witch    = Button(725, 480, 150, 40, "Change Outfit", PURPLE, WHITE)
btn_start         = Button(415, 540, 170, 50, "LAUNCH RAMP SHOW", (50, 220, 90))
btn_go_to_fight   = Button(400, 140, 200, 45, "START BRAWL!", RED, WHITE)

btn_a_beam   = Button(50, 550, 130, 40, "Light Beam", CYAN)
btn_a_stars  = Button(190, 550, 140, 40, "Star Storm", GOLD)
btn_w_curse  = Button(670, 550, 130, 40, "Dark Curse", PURPLE, WHITE)
btn_w_orbs   = Button(810, 550, 140, 40, "Shadow Orbs", RED, WHITE)
btn_reset    = Button(435, 550, 130, 40, "Reset Game", WHITE)

def draw_human(surface, x, y, is_witch, dress_config, pose="normal"):
    offset_x, offset_y = 0, 0
    tilt_angle = 0
    
    if pose == "dead":
        offset_y = 110  
        tilt_angle = 90 if not is_witch else -90  
    elif pose in ("beam", "stars", "curse", "orbs"):
        offset_y = int(math.sin(animation_timer * 0.2) * 10) - 15  
    elif pose == "hurt":
        offset_x = -25 if not is_witch else 25  
        tilt_angle = 15 if not is_witch else -15

    char_surf = pygame.Surface((200, 300), pygame.SRCALPHA)
    cx, cy = 100, 50

    if not is_witch:
        pygame.draw.ellipse(char_surf, (230, 240, 255), (cx - 60, cy + 20, 80, 120))
        pygame.draw.ellipse(char_surf, (230, 240, 255), (cx + 20, cy + 20, 80, 120))
    else:
        pygame.draw.polygon(char_surf, (30, 15, 45), [(cx - 45, cy + 55), (cx, cy + 15), (cx + 45, cy + 55)])
        pygame.draw.circle(char_surf, HAIR_BLACK, (cx - 16, cy + 25), 18)
        pygame.draw.circle(char_surf, HAIR_BLACK, (cx + 16, cy + 25), 18)
        pygame.draw.rect(char_surf, HAIR_BLACK, (cx - 16, cy + 25, 32, 50))

    pygame.draw.rect(char_surf, SKIN_TONE, (cx - 10, cy + 35, 20, 20)) 
    pygame.draw.ellipse(char_surf, SKIN_TONE, (cx - 25, cy + 50, 50, 40)) 

    pygame.draw.polygon(char_surf, dress_config["color"], [(cx - 22, cy + 55), (cx + 22, cy + 55), (cx + 48, cy + 220), (cx - 48, cy + 220)])
    pygame.draw.polygon(char_surf, dress_config["accent"], [(cx - 12, cy + 55), (cx + 12, cy + 55), (cx + 18, cy + 220), (cx - 18, cy + 220)]) 

    pygame.draw.circle(char_surf, SKIN_TONE, (cx, cy + 15), 20) 
    
    if not is_witch:
        pygame.draw.circle(char_surf, HAIR_GOLD, (cx - 14, cy + 12), 12)
        pygame.draw.circle(char_surf, HAIR_GOLD, (cx + 14, cy + 12), 12)
        if pose != "dead": pygame.draw.arc(char_surf, GOLD, (cx - 15, cy - 5, 30, 15), 0, 3.14, 3) 
    else:
        pygame.draw.polygon(char_surf, PURPLE, [(cx - 12, cy - 2), (cx + 12, cy - 2), (cx, cy - 12)])

    if pose == "dead":
        pygame.draw.line(char_surf, RED, (cx-6, cy+6), (cx-2, cy+10), 2)
        pygame.draw.line(char_surf, RED, (cx-2, cy+6), (cx-6, cy+10), 2)
        pygame.draw.line(char_surf, RED, (cx+2, cy+6), (cx+6, cy+10), 2)
        pygame.draw.line(char_surf, RED, (cx+6, cy+6), (cx+2, cy+10), 2)
        pygame.draw.line(char_surf, BLACK, (cx - 6, cy + 16), (cx + 6, cy + 16), 2)
    elif pose == "hurt":
        pygame.draw.line(char_surf, RED, (cx-6, cy+8), (cx-2, cy+12), 2)
        pygame.draw.line(char_surf, RED, (cx-2, cy+8), (cx-6, cy+12), 2)
        pygame.draw.line(char_surf, RED, (cx+2, cy+8), (cx+6, cy+12), 2)
        pygame.draw.line(char_surf, RED, (cx+6, cy+8), (cx+2, cy+12), 2)
        pygame.draw.arc(char_surf, RED, (cx - 6, cy + 16, 12, 8), 0, 3.14, 2)
    elif pose != "normal":
        pygame.draw.line(char_surf, BLACK, (cx - 10, cy + 5), (cx - 3, cy + 9), 3)
        pygame.draw.line(char_surf, BLACK, (cx + 10, cy + 5), (cx + 3, cy + 9), 3)
        pygame.draw.arc(char_surf, BLACK, (cx - 6, cy + 16, 12, 10), 0, 3.14, 2)
    else:
        pygame.draw.circle(char_surf, BLACK, (cx - 5, cy + 10), 2) 
        pygame.draw.circle(char_surf, BLACK, (cx + 5, cy + 10), 2) 
        pygame.draw.arc(char_surf, BLACK, (cx - 6, cy + 12, 12, 8), 3.14, 0, 2) 

    if tilt_angle != 0:
        char_surf = pygame.transform.rotate(char_surf, tilt_angle)
    surface.blit(char_surf, (x - 100 + offset_x, y - 50 + offset_y))

angel_x, witch_x = -150, 1150
ramp_speed = 3

while True:
    mx, my = pygame.mouse.get_pos()
    animation_timer += 1
    
    if action_timer > 0: 
        action_timer -= 1
        if action_timer == 1: 
            if active_attacker == "angel":
                witch_hp -= random.randint(20, 35)
                if witch_hp <= 0: witch_hp, game_over = 0, True
            elif active_attacker == "witch":
                angel_hp -= random.randint(20, 35)
                if angel_hp <= 0: angel_hp, game_over = 0, True
    else: 
        current_action = ""

    if current_state == STATE_FIGHT and action_timer == 0 and not game_over:
        robot_timer += 1
        if robot_timer > 70:  
            robot_timer = 0
            if player_role == "witch":  
                current_action = random.choice(["beam", "stars"])
                action_timer, active_attacker = (30 if current_action == "beam" else 40), "angel"
            elif player_role == "angel":  
                current_action = random.choice(["curse", "orbs"])
                action_timer, active_attacker = (30 if current_action == "curse" else 40), "witch"

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == STATE_THEME:
                if btn_play_game.clicked((mx, my)): current_state = STATE_SELECTION
                
            elif current_state == STATE_SELECTION:
                if btn_choose_divine.clicked((mx, my)):
                    player_role = "angel"
                    witch_choice = random.randint(0, len(witch_options) - 1) 
                    current_state = STATE_DRESSUP
                elif btn_choose_dark.clicked((mx, my)):
                    player_role = "witch"
                    angel_choice = random.randint(0, len(angel_options) - 1) 
                    current_state = STATE_DRESSUP
                    
            elif current_state == STATE_DRESSUP:
                if player_role == "angel" and btn_next_angel.clicked((mx, my)): 
                    angel_choice = (angel_choice + 1) % len(angel_options)
                elif player_role == "witch" and btn_next_witch.clicked((mx, my)): 
                    witch_choice = (witch_choice + 1) % len(witch_options)
                elif btn_start.clicked((mx, my)): 
                    current_state = STATE_RUNWAY
                    angel_x, witch_x = -150, 1150
                    
            elif current_state == STATE_RESULTS:
                if btn_go_to_fight.clicked((mx, my)): 
                    angel_hp, witch_hp, game_over = 100, 100, False 
                    current_state = STATE_FIGHT
                
            elif current_state == STATE_FIGHT:
                if btn_reset.clicked((mx, my)):
                    active_theme = random.choice(THEMES)
                    player_role = None
                    current_state = STATE_THEME
                elif action_timer == 0 and not game_over:  
                    if player_role == "angel":
                        if btn_a_beam.clicked((mx, my)): current_action, action_timer, active_attacker = "beam", 30, "angel"
                        elif btn_a_stars.clicked((mx, my)): current_action, action_timer, active_attacker = "stars", 40, "angel"
                    elif player_role == "witch":
                        if btn_w_curse.clicked((mx, my)): current_action, action_timer, active_attacker = "curse", 30, "witch"
                        elif btn_w_orbs.clicked((mx, my)): current_action, action_timer, active_attacker = "orbs", 40, "witch"

    if current_state == STATE_THEME:
        screen.fill(DARK_PURPLE)
        pygame.draw.rect(screen, BLACK, (150, 100, 700, 420), border_radius=20)
        pygame.draw.rect(screen, GOLD, (150, 100, 700, 420), width=3, border_radius=20)
        
        lbl1 = font_md.render("✨ WELCOME TO ✨", True, CYAN)
        lbl2 = font_lg.render("DIVINES & DARKLINGS", True, GOLD)
        lbl3 = font_sm.render(f"Tonight's Random Runway Theme: {active_theme['name']}", True, WHITE)
        
        screen.blit(lbl1, lbl1.get_rect(center=(WIDTH//2, 170)))
        screen.blit(lbl2, lbl2.get_rect(center=(WIDTH//2, 250)))
        screen.blit(lbl3, lbl3.get_rect(center=(WIDTH//2, 340)))
        btn_play_game.draw(screen)

    elif current_state == STATE_SELECTION:
        screen.fill(DARK_PURPLE)
        pygame.draw.rect(screen, BLACK, (100, 80, 800, 460), border_radius=20)
        
        lbl_sel = font_lg.render("CHOOSE YOUR FACTION", True, WHITE)
        lbl_bot = font_sm.render("The character you do not choose will be controlled by a Robot AI!", True, LIGHT_PINK)
        screen.blit(lbl_sel, lbl_sel.get_rect(center=(WIDTH//2, 150)))
        screen.blit(lbl_bot, lbl_bot.get_rect(center=(WIDTH//2, 220)))
        
        btn_choose_divine.draw(screen)
        btn_choose_dark.draw(screen)

    elif current_state == STATE_DRESSUP:
        screen.fill(LIGHT_PINK)
        pygame.draw.rect(screen, WHITE, (50, 20, 900, 60), border_radius=10)
        lbl_t = font_md.render(f"MATCH THE THEME: {active_theme['name']}", True, BLACK)
        screen.blit(lbl_t, lbl_t.get_rect(center=(WIDTH//2, 50)))

        pygame.draw.rect(screen, WHITE, (70, 100, 260, 360), border_radius=15)
        pygame.draw.rect(screen, BLACK, (670, 100, 260, 360), border_radius=15)
        
        draw_human(screen, 200, 170, False, angel_options[angel_choice])
        draw_human(screen, 800, 170, True, witch_options[witch_choice])

        if player_role == "angel":
            btn_next_angel.draw(screen)
            lbl_r = font_md.render("🤖 ROBOT SELECTED", True, WHITE)
            screen.blit(lbl_r, lbl_r.get_rect(center=(800, 490)))
        else:
            btn_next_witch.draw(screen)
            lbl_r = font_md.render("🤖 ROBOT SELECTED", True, BLACK)
            screen.blit(lbl_r, lbl_r.get_rect(center=(200, 490)))
            
        btn_start.draw(screen)

    elif current_state == STATE_RUNWAY or current_state == STATE_RESULTS:
        screen.fill(BLACK)
        if current_state == STATE_RUNWAY:
            if angel_x < 350: angel_x += ramp_speed
            if witch_x > 650: witch_x -= ramp_speed
            if angel_x >= 350 and witch_x <= 650:
                current_state = STATE_RESULTS
                score_angel = random.randint(60, 75) + (25 if angel_choice == active_theme["best_angel"] else 0)
                score_witch = random.randint(60, 75) + (25 if witch_choice == active_theme["best_witch"] else 0)
                voted_winner = "angel" if score_angel >= score_witch else "witch"

        for d in audience_dots:
            color = (random.randint(180, 255), random.randint(150, 220), 100) if current_state == STATE_RESULTS else (60, 55, 75)
            pygame.draw.circle(screen, color, (d["x"], d["y"]), d["size"])

        pygame.draw.polygon(screen, (60, 60, 80), [(200, 650), (400, 200), (600, 200), (800, 650)])
        draw_human(screen, angel_x, 200, False, angel_options[angel_choice], pose="normal")
        draw_human(screen, witch_x, 200, True, witch_options[witch_choice], pose="normal")

        if current_state == STATE_RESULTS:
            pygame.draw.rect(screen, (25, 20, 35), (200, 20, 600, 180), border_radius=15)
            p1_tag = " (YOU)" if player_role == "angel" else " (ROBOT)"
            p2_tag = " (YOU)" if player_role == "witch" else " (ROBOT)"
            
            w_msg = f"DIVINE WINS{p1_tag} ({score_angel} vs {score_witch})!" if voted_winner == "angel" else f"DARKLING WINS{p2_tag} ({score_witch} vs {score_angel})!"
            lbl_res = font_md.render(w_msg, True, GOLD if voted_winner == "angel" else PURPLE)
            screen.blit(lbl_res, lbl_res.get_rect(center=(WIDTH//2, 70)))
            btn_go_to_fight.draw(screen)

    elif current_state == STATE_FIGHT:
        screen.fill((45, 15, 30)) 
        pygame.draw.rect(screen, BLACK, (0, 480, WIDTH, 170))
        pygame.draw.line(screen, RED, (0, 480), (WIDTH, 480), 4)

        angel_pose = "dead" if angel_hp <= 0 else "normal"
        witch_pose = "dead" if witch_hp <= 0 else "normal"

        if action_timer > 0:
            if active_attacker == "angel":
                angel_pose = current_action
                if action_timer < 16: witch_pose = "hurt"
            elif active_attacker == "witch":
                witch_pose = current_action
                if action_timer < 16: angel_pose = "hurt"

        draw_human(screen, angel_fight_x, angel_fight_y, False, angel_options[angel_choice], pose=angel_pose)
        draw_human(screen, witch_fight_x, witch_fight_y, True, witch_options[witch_choice], pose=witch_pose)

        pygame.draw.rect(screen, RED, (100, 80, 250, 20), border_radius=5)
        pygame.draw.rect(screen, GREEN, (100, 80, int(2.5 * angel_hp), 20), border_radius=5)
        lbl_ahp = font_sm.render(f"Divine Angel: {angel_hp} HP", True, WHITE)
        screen.blit(lbl_ahp, (100, 55))

        pygame.draw.rect(screen, RED, (650, 80, 250, 20), border_radius=5)
        pygame.draw.rect(screen, GREEN, (650, 80, int(2.5 * witch_hp), 20), border_radius=5)
        lbl_whp = font_sm.render(f"Darkling Witch: {witch_hp} HP", True, WHITE)
        screen.blit(lbl_whp, (650, 55))

        if action_timer > 0:
            if current_action == "beam": 
                pygame.draw.line(screen, CYAN, (angel_fight_x + 30, angel_fight_y + 30), (witch_fight_x - 30, witch_fight_y + 30), 8)
                pygame.draw.circle(screen, WHITE, (witch_fight_x - 30, witch_fight_y + 30), 20)
            elif current_action == "curse": 
                pygame.draw.line(screen, PURPLE, (witch_fight_x - 30, witch_fight_y + 30), (angel_fight_x + 30, angel_fight_y + 30), 8)
                pygame.draw.circle(screen, RED, (angel_fight_x + 30, angel_fight_y + 30), 20)
            elif current_action == "stars": 
                for i in range(4):
                    star_x = witch_fight_x - 40 + (i * 25)
                    star_y = (HEIGHT - 170) - (action_timer * 8) + (i * 15)
                    if star_y < witch_fight_y + 100: pygame.draw.circle(screen, GOLD, (star_x, star_y), 10)
            elif current_action == "orbs": 
                ox = witch_fight_x - 50 - ((40 - action_timer) * 10)
                if ox > angel_fight_x:
                    pygame.draw.circle(screen, RED, (ox, witch_fight_y + 20), 14)
                    pygame.draw.circle(screen, PURPLE, (ox + 15, witch_fight_y + 35), 8)

        pygame.draw.rect(screen, (20, 20, 30), (230, 15, 540, 55), border_radius=10)
        if game_over:
            winner_text = "DARKLING WITCH WINS! ANGEL DIED!" if angel_hp <= 0 else "DIVINE ANGEL WINS! WITCH DIED!"
            lbl_fight = font_md.render(winner_text, True, RED)
        else:
            lbl_fight = font_md.render("BACKSTAGE BRAWL: TO THE DEATH!", True, WHITE)
        screen.blit(lbl_fight, lbl_fight.get_rect(center=(WIDTH//2, 42)))

        if not game_over:
            if player_role == "angel":
                btn_a_beam.draw(screen)
                btn_a_stars.draw(screen)
            else:
                btn_w_curse.draw(screen)
                btn_w_orbs.draw(screen)
        btn_reset.draw(screen)

    pygame.display.flip()
    clock.tick(60)
