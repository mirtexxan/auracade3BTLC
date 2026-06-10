import pygame
import sys
import random
import math

# 1. INIZIALIZZAZIONE DI PYGAME
pygame.init()

TILE_SIZE = 40
MAP_WIDTH = 15
MAP_HEIGHT = 15

SCREEN_WIDTH = MAP_WIDTH * TILE_SIZE
SCREEN_HEIGHT = (MAP_HEIGHT * TILE_SIZE) + 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Final Fantasy I - Goblin RPG Edition")
clock = pygame.time.Clock()

COLOR_BOX = (10, 10, 25)
COLOR_TEXT = (240, 240, 255)

# --- SISTEMA DI LOCALIZZAZIONE (ITALIANO / INGLESE) ---
lang = "it"

TEXT = {
    "it": {
        "title": "Final Fantasy : goblin hero",
        "press_start": "Premi INVIO per iniziare il gioco",
        "press_lang": "Premi X per cambiare lingua / Change language",
        "press_keys": "Premi K per i comandi / Press K for controls",
        "lang_title": "SELEZIONE LINGUA / LANGUAGE SELECT",
        "controls_title": "COMANDI DI COMBATTIMENTO E CHEAT",
        "ctrl_a": "[A] Attacca",
        "ctrl_r": "[R] Fuggi",
        "ctrl_h": "[H] Herotoktonos (Sbloccato dopo il boss)",
        "ctrl_v": "[V] Attiva/Disattiva Cheat EXP x8",
        "ctrl_m": "[M] Evoca Console Cheat Musci",
        "back": "Premi Z per tornare indietro",
        "world_init": "Devi fermare gli eroi dall'andare verso il tempio del chaos",
        "cheat_exp": "Cheat EXP x8",
        "cheat_musci": "Cheat Spawn Musci",
        "activated": "ATTIVATO",
        "deactivated": "DISATTIVATO",
        "hero_lock": "Herotoktonos [H] sbloccato solo dopo aver ucciso gli Eroi!",
        "use_hero": "Usi HEROTOKTONOS! Squarci {name} per {dmg} danni! ",
        "hit": "Colpisci {name} per {dmg} danni! ",
        "useless": "(Inutile...) ",
        "ko": "KO! ",
        "garland_win": "VITTORIA ASSOLUTA!",
        "heroes_win": "VITTORIA FINALE! Hai sterminato gli Eroi! (+{exp} EXP)",
        "normal_win": "Vittoria! Guadagni {exp} EXP.",
        "lvl_up": " LIV. {lvl} (+{hp} HP, +{atk} ATK)!",
        "musci_annihilate": "ti annienta dall'esistenza!",
        "fireball": "lancia PALLA DI FUOCO!",
        "attack": "ti attacca!",
        "musci_appear": "MUSCI È APPARSO DAL NULLA! IL TUO DESTINO È SEGNATO.",
        "soldier_block": "Dei mostri sbarrano il cammino!",
        "heroes_assault": "I 4 EROI TI ASSALTANO!",
        "musci_appear_city": "MUSCI È QUI ANCHE IN CITTÀ! SCAPPA!",
        "guard_block": "Una Guardia ti blocca!",
        "enter_cornelia": "Sei dentro Cornelia.",
        "exit_cornelia": "Sei uscito nel Mondo Esterno.",
        "player_chaos": "Tu (Signore del Chaos)",
        "player_goblin": "Tu (Goblin)",
        "liv": "LIV",
        "hp": "HP",
        "atk": "ATK",
        "exp": "EXP",
        "vite": "VITE",
        "run_text": "RUN: {count}",
        "comb_options": "OPZIONI DI COMBATTIMENTO:",
        "opt_attack": "[A] Attacca",
        "opt_escape": "[R] Fuggi",
        "opt_hero": "[H] Herotoktonos",
        "others_queue": "+ {count} altri avversari in coda...",
        "combat_title": "COMBATTIMENTO",
        "garland_speech": "GARLAND: 'Vi abbatterò tutti quanti!'",
        "soldier_name": "Soldato",
        "guard_name": "Guardia di Cornelia",
        "guerriero": "Guerriero",
        "ninja": "Ninja",
        "stregone_b": "Stregone B.",
        "stregone_n": "Stregone N.",
        "world_safe": "Mondo in salvo. Tu sei l'unico, potente, Signore del Chaos!",
        "heroes_defeated_go_temp": "Eroi sconfitti! Torna al Tempio del Chaos, Garland ti aspetta!",
        "city_msg": "Città. Tuo Liv: {lvl}. ",
        "reach_lvl8": "Raggiungi il Liv.8 per sfidare gli Eroi.",
        "heroes_warning": "ATTENZIONE: Gli Eroi Liv.{lvl} hanno l'80% chance di assaltarti qui fuori!",
        "boss_no_escape": "Non puoi fuggire dai boss della storia! Combatti!",
        "escaped": "Sei fuggito!",
        "escape_failed_musci": "Fuga fallita! Musci ti disintegra all'istante (∞ HP!).",
        "escape_failed": "Fuga fallita! {name} ti colpisce per {dmg} danni.",
        "reset_heroes": "Sconfitto dagli Eroi! Gioco riavviato. Gli Eroi tornano al Liv.8!",
        "reset_garland": "Hai fallito contro Garland! Gioco riavviato. Gli Eroi tornano al Liv.8!",
        "reset_lives": "Hai perso tutte le vite. Gioco riavviato! Gli Eroi tornano al Liv.8!",
        "dead_respawn": "Sconfitto... Ti risvegli davanti al Tempio. Vite rimaste: {lives}.",
        "escape_dead": "Sconfitto in fuga... Vite rimaste: {lives}.",
        "infinite_text": "Infinito",
        "choice_title": "Vuoi affrontare il boss secondario?",
        "choice_keys": "Premere [Y] per SI  oppure  [N] per NO",
        "end_rh_title": "FINALE: Braccio destro del signore del chaos",
        "end_rh_msg": "Hai eliminato gli eroi e assicurato il dominio assieme al tuo signore.",
        "any_key_title": "Premi un tasto per tornare al titolo",
        "comp_all_title": "Hai completato tutto!",
        "comp_all_msg": "Premere [Y] per continuare...",
        "end_cl_title": "FINALE: Signore del Chaos",
        "end_cl_msg": "Hai eliminato il tuo signore e ora domini su tutto."
    },
    "en": {
        "title": "Final Fantasy : goblin hero",
        "press_start": "Press ENTER to start the game",
        "press_lang": "Press X to change language / Cambiare lingua",
        "press_keys": "Press K for controls / Premi K for i comandi",
        "lang_title": "SELEZIONE LINGUA / LANGUAGE SELECT",
        "controls_title": "COMBAT CONTROLS & CHEATS",
        "ctrl_a": "[A] Attack",
        "ctrl_r": "[R] Run",
        "ctrl_h": "[H] Herotoktonos (Unlocked after boss)",
        "ctrl_v": "[V] Toggle Cheat EXP x8",
        "ctrl_m": "[M] Summon Musci Cheat Console",
        "back": "Press Z to go back",
        "world_init": "You must stop the heroes from going to the Chaos Temple",
        "cheat_exp": "Cheat EXP x8",
        "cheat_musci": "Cheat Spawn Musci",
        "activated": "ACTIVATED",
        "deactivated": "DEACTIVATED",
        "hero_lock": "Herotoktonos [H] unlocked only after killing the Heroes!",
        "use_hero": "You use HEROTOKTONOS! You slash {name} for {dmg} damage! ",
        "hit": "You hit {name} for {dmg} damage! ",
        "useless": "(Useless...) ",
        "ko": "KO! ",
        "garland_win": "ABSOLUTE VICTORY!",
        "heroes_win": "FINAL VICTORY! You exterminated the Heroes! (+{exp} EXP)",
        "normal_win": "Victory! You gain {exp} EXP.",
        "lvl_up": " LVL. {lvl} (+{hp} HP, +{atk} ATK)!",
        "musci_annihilate": "annihilates you from existence!",
        "fireball": "casts FIREBALL!",
        "attack": "attacks you!",
        "musci_appear": "MUSCI HAS APPEARED OUT OF NOWHERE! YOUR DOOM IS SEALED.",
        "soldier_block": "Monsters block your path!",
        "heroes_assault": "THE 4 HEROES AMBUSH YOU!",
        "musci_appear_city": "MUSCI IS HERE IN THE CITY TOO! RUN!",
        "guard_block": "A Guard blocks your way!",
        "enter_cornelia": "You are inside Cornelia.",
        "exit_cornelia": "You exited to the Overworld.",
        "player_chaos": "You (Chaos Lord)",
        "player_goblin": "You (Goblin)",
        "liv": "LVL",
        "hp": "HP",
        "atk": "ATK",
        "exp": "EXP",
        "vite": "LIVES",
        "run_text": "RUN: {count}",
        "comb_options": "COMBAT OPTIONS:",
        "opt_attack": "[A] Attack",
        "opt_escape": "[R] Run",
        "opt_hero": "[H] Herotoktonos",
        "others_queue": "+ {count} other opponents in queue...",
        "combat_title": "COMBAT",
        "garland_speech": "GARLAND: 'I will strike you all down!'",
        "soldier_name": "Soldier",
        "guard_name": "Cornelia Guard",
        "guerriero": "Warrior",
        "ninja": "Ninja",
        "stregone_b": "White Mage",
        "stregone_n": "Black Mage",
        "world_safe": "World saved. You are the one, powerful, Chaos Lord!",
        "heroes_defeated_go_temp": "Heroes defeated! Return to the Chaos Temple, Garland awaits you!",
        "city_msg": "City. Your Lvl: {lvl}. ",
        "reach_lvl8": "Reach Lvl.8 to challenge the Heroes.",
        "heroes_warning": "WARNING: Lvl.{lvl} Heroes have an 80% chance to ambush you out here!",
        "boss_no_escape": "You cannot run from story bosses! Fight!",
        "escaped": "You escaped!",
        "escape_failed_musci": "Escape failed! Musci disintegrates you instantly (∞ HP!).",
        "escape_failed": "Escape failed! {name} hits you for {dmg} damage.",
        "reset_heroes": "Defeated by the Heroes! Game restarted. Heroes reset to Lvl.8!",
        "reset_garland": "Failed against Garland! Game restarted. Heroes reset to Lvl.8!",
        "reset_lives": "Lost all lives. Game restarted! Heroes reset to Lvl.8!",
        "dead_respawn": "Defeated... You wake up in front of the Temple. Lives left: {lives}.",
        "escape_dead": "Defeated while escaping... Lives left: {lives}.",
        "infinite_text": "Infinite",
        "choice_title": "Do you want to challenge the secondary boss?",
        "choice_keys": "Press [Y] for YES  or  [N] for NO",
        "end_rh_title": "ENDING: Right Hand of the Chaos Lord",
        "end_rh_msg": "You eliminated the heroes and secured dominance alongside your lord.",
        "any_key_title": "Press any key to return to the title screen",
        "comp_all_title": "You completed everything!",
        "comp_all_msg": "Press [Y] to continue...",
        "end_cl_title": "ENDING: Chaos Lord",
        "end_cl_msg": "You eliminated your lord and now rule over everything."
    }
}

# STATO DEL GIOCO E VARIABILI DI COMBATTIMENTO
game_state = "TITLE"       
previous_state = "WORLD"  
previous_state_for_input = "WORLD" 
user_typed = ""

enemy_turn_idx = 0  
cheat_exp_x8 = False  
cheat_musci = False       
musci_spawned = False     

# STATISTICHE GIOCATORE E NEMICI
run_count = 1  
player_level = 1
player_exp = 0
player_max_hp = 50
player_hp = 50
player_atk = 6  
player_lives = 3 

current_enemies = []  
boss_defeated = False 
garland_defeated = False
heroes_level = 8  
battle_msg = "" 
world_msg = ""

# --- CARICAMENTO IMMAGINI ---
boss_images = {}
boss_filenames = {
    "Guerriero": "guerriero.png",
    "Ninja": "ninja.png",
    "Stregone B.": "stregonbianco.png",
    "Stregone N.": "stregonero.png"
}
for b_name, b_file in boss_filenames.items():
    try:
        img = pygame.image.load(b_file).convert_alpha()
        boss_images[b_name] = pygame.transform.scale(img, (45, 45))
    except Exception as e:
        boss_images[b_name] = None 

garland_image = None
try:
    img_garl = pygame.image.load("garland.png").convert_alpha()
    garland_image = pygame.transform.scale(img_garl, (45, 45))
except Exception as e:
    pass

musci_image = None
try:
    img_musci = pygame.image.load("Musci.png").convert_alpha()
    musci_image = pygame.transform.scale(img_musci, (45, 45))
except Exception as e:
    pass

try:
    img_p = pygame.image.load("player.png").convert_alpha()
    player_image = pygame.transform.scale(img_p, (36, 36))
except Exception as e:
    player_image = None

soldato_image = None
try:
    img_s = pygame.image.load("soldato.png").convert_alpha()
    soldato_image = pygame.transform.scale(img_s, (45, 45))
except Exception as e:
    pass

guardia_image = None
try:
    img_g = pygame.image.load("guardia.png").convert_alpha()
    guardia_image = pygame.transform.scale(img_g, (45, 45))
except Exception as e:
    pass

# 2. FUNZIONI DI SUPPORTO E RESET
def get_enemy_display_name(enemy):
    t = enemy.get("type")
    lvl = enemy.get("level")
    is_boss = enemy.get("is_boss", False)
    is_garland = enemy.get("is_garland", False)
    is_musci = enemy.get("is_musci", False)
    if is_musci: return "Musci"
    if is_garland: return "Garland"
    if t == "soldier":
        return f"{TEXT[lang]['soldier_name']} {TEXT[lang]['liv']}.{lvl}"
    elif t == "guard":
        return f"{TEXT[lang]['guard_name']} {TEXT[lang]['liv']}.{lvl}"
    else:
        name_key = enemy.get("name_key", enemy["name"])
        base = TEXT[lang].get(name_key, enemy["name"])
        if is_boss and not is_garland:
            return f"{base} {TEXT[lang]['liv']}.{lvl}"
        return base

def get_enemy_level(p_level, min_cap, max_cap):
    diffs = [-2, -1, 0, 1, 2]
    weights = [1, 4, 45, 35, 15]
    lvl = p_level + random.choices(diffs, weights=weights, k=1)[0]
    lvl = max(min_cap, lvl)
    return min(lvl, max_cap) 

def get_enemy_exp(level):
    exp = 3
    for _ in range(1, level):
        exp = math.ceil(exp * 1.5)
    return exp

def get_required_exp(level):
    if level <= 8:
        return 2 ** level
    else:
        base_exp = 2 ** 8  
        for _ in range(8, level):
            base_exp = math.ceil(base_exp * 1.25)
        return base_exp

def reset_game(reason=""):
    global player_level, player_exp, player_max_hp, player_hp, player_atk, player_lives
    global game_state, previous_state, player_x, player_y, boss_defeated, garland_defeated, world_msg, heroes_level
    global musci_spawned, cheat_musci, run_count
    
    player_level = 1
    player_exp = 0
    player_max_hp = 50
    player_hp = 50
    player_atk = 6
    player_lives = 3
    boss_defeated = False
    garland_defeated = False
    musci_spawned = False
    cheat_musci = False
    
    heroes_level = 8 
    run_count += 1
    
    game_state = "WORLD"
    previous_state = "WORLD"
    player_x, player_y = 7, 2
    
    if reason == "heroes":
        world_msg = TEXT[lang]["reset_heroes"]
    elif reason == "garland":
        world_msg = TEXT[lang]["reset_garland"]
    elif reason == "lives":
        world_msg = TEXT[lang]["reset_lives"]

# 3. FUNZIONI DI DISEGNO GRAFICO
def draw_grass(surf, x, y):
    pygame.draw.rect(surf, (34, 139, 34), (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.line(surf, (25, 110, 25), (x + 10, y + 15), (x + 12, y + 8), 2)
    pygame.draw.line(surf, (25, 110, 25), (x + 12, y + 8), (x + 15, y + 15), 2)

def draw_water(surf, x, y):
    pygame.draw.rect(surf, (28, 107, 160), (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.line(surf, (70, 160, 220), (x + 8, y + 15), (x + 18, y + 15), 2)

def draw_mountain(surf, x, y):
    pygame.draw.rect(surf, (34, 139, 34), (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.polygon(surf, (130, 130, 135), [(x + 20, y + 5), (x + 5, y + 35), (x + 20, y + 35)])
    pygame.draw.polygon(surf, (90, 90, 95), [(x + 20, y + 5), (x + 35, y + 35), (x + 20, y + 35)])

def draw_cornelia_world(surf, x, y):
    pygame.draw.rect(surf, (34, 139, 34), (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surf, (218, 165, 32), (x + 4, y - 10, 32, 40))
    pygame.draw.rect(surf, (184, 134, 11), (x, y - 30, 10, 60))
    pygame.draw.rect(surf, (184, 134, 11), (x + 30, y - 30, 10, 60))
    pygame.draw.polygon(surf, (190, 30, 30), [(x + 5, y - 50), (x - 2, y - 30), (x + 12, y - 30)])

def draw_chaos_shrine(surf, x, y):
    pygame.draw.rect(surf, (70, 50, 50), (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surf, (45, 35, 60), (x + 2, y - 10, 36, 40))
    pygame.draw.polygon(surf, (25, 15, 35), [(x + 20, y - 40), (x - 6, y - 10), (x + 46, y - 10)])

def draw_city_grass(surf, x, y):
    pygame.draw.rect(surf, (40, 155, 40), (x, y, TILE_SIZE, TILE_SIZE))

def draw_city_wall(surf, x, y):
    pygame.draw.rect(surf, (110, 110, 115), (x, y, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surf, (140, 140, 145), (x, y, TILE_SIZE, 10))
    pygame.draw.line(surf, (75, 75, 80), (x, y + 22), (x + TILE_SIZE, y + 22), 2)
    pygame.draw.line(surf, (75, 75, 80), (x + 15, y + 10), (x + 15, y + 22), 2)
    pygame.draw.line(surf, (75, 75, 80), (x + 30, y + 22), (x + 30, y + 40), 2)

def draw_tall_tree(surf, x, y):
    pygame.draw.rect(surf, (100, 65, 30), (x + 16, y + 18, 8, 22))
    pygame.draw.circle(surf, (20, 115, 20), (x + 20, y + 6), 16)

def draw_tall_house(surf, x, y):
    pygame.draw.rect(surf, (175, 145, 105), (x, y + 12, TILE_SIZE, 28))
    pygame.draw.rect(surf, (80, 45, 15), (x + 14, y + 24, 12, 16))
    pygame.draw.polygon(surf, (190, 50, 40), [(x - 3, y + 12), (x + TILE_SIZE + 3, y + 12), (x + 20, y - 12)])

def draw_player(surf, x, y):
    if player_image is not None:
        surf.blit(player_image, (x + 2, y + 2))
    else:
        cx, cy = x + 20, y + 20
        pygame.draw.rect(surf, (70, 75, 85), (cx - 10, cy, 20, 14))
        pygame.draw.rect(surf, (140, 20, 20), (cx - 7, cy - 6, 14, 13))
        pygame.draw.circle(surf, (45, 140, 70), (cx, cy - 10), 7)
        pygame.draw.circle(surf, (255, 0, 0), (cx - 3, cy - 10), 1)
        pygame.draw.circle(surf, (255, 0, 0), (cx + 3, cy - 10), 1)

# 4. MATRICI DELLE MAPPE
WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 4, 4, 4, 4, 4, 4, 3, 4, 4, 4, 4, 4, 4, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 1],
    [1, 4, 0, 4, 4, 4, 0, 0, 0, 4, 4, 4, 0, 4, 1],
    [1, 4, 0, 4, 1, 1, 0, 0, 0, 1, 1, 4, 0, 4, 1],
    [1, 0, 0, 4, 1, 1, 0, 0, 0, 1, 1, 4, 0, 0, 1],
    [1, 0, 0, 4, 4, 4, 0, 0, 0, 4, 4, 4, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 4, 4, 4, 4, 4, 0, 0, 0, 4, 4, 4, 4, 4, 1],
    [1, 4, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0, 0, 4, 1],
    [1, 4, 0, 0, 0, 4, 0, 2, 0, 4, 0, 0, 0, 4, 1],
    [1, 4, 0, 0, 0, 4, 0, 0, 0, 4, 0, 0, 0, 4, 1],
    [1, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

CITY_MAP = [
    [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 9, 9, 9, 0, 0, 0, 0, 0, 9, 9, 9, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 8, 8, 0, 0, 0, 0, 0, 8, 8, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 9, 9, 0, 0, 0, 0, 0, 0, 0, 9, 9, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 8, 8, 8, 0, 0, 0, 0, 0, 8, 8, 8, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7],
    [7, 7, 7, 7, 7, 7, 7, 0, 7, 7, 7, 7, 7, 7, 7],
    [7, 7, 7, 7, 7, 7, 7, 0, 7, 7, 7, 7, 7, 7, 7],
    [7, 7, 7, 7, 7, 7, 7, 0, 7, 7, 7, 7, 7, 7, 7]
]

player_x, player_y = 7, 2

try:
    font = pygame.font.SysFont("Consolas", 18, bold=True)
    big_font = pygame.font.SysFont("Consolas", 26, bold=True)
except:
    font = pygame.font.Font(None, 22)
    big_font = pygame.font.Font(None, 32)

# 5. LOOP DI GIOCO PRINCIPALE
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
            
            # --- CONSOLE INPUT MUSCI ---
            if game_state == "MUSCI_INPUT":
                if event.key == pygame.K_RETURN:
                    if user_typed.strip().lower() == "ciao mirto":
                        cheat_musci = not cheat_musci
                        status = f"{TEXT[lang]['activated']} (80%)" if cheat_musci else f"{TEXT[lang]['deactivated']} (1e-12)"
                        msg_txt = f"{TEXT[lang]['cheat_musci']} {status}!"
                        if previous_state_for_input == "BATTLE": battle_msg = msg_txt
                        else: world_msg = msg_txt
                    game_state = previous_state_for_input
                elif event.key == pygame.K_ESCAPE:
                    game_state = previous_state_for_input
                elif event.key == pygame.K_BACKSPACE:
                    user_typed = user_typed[:-1]
                else:
                    if len(user_typed) < 25: 
                        user_typed += event.unicode
                continue 

            # --- SCHERMATA TITOLO ---
            if game_state == "TITLE":
                if event.key == pygame.K_RETURN:  
                    game_state = "WORLD"
                    world_msg = TEXT[lang]["world_init"]
                elif event.key == pygame.K_x:     
                    game_state = "LANG_SELECT"
                elif event.key == pygame.K_k:     
                    game_state = "CONTROLS_SCREEN"
            
            # --- SCHERMATA CAMBIO LINGUA ---
            elif game_state == "LANG_SELECT":
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    lang = "it"
                    game_state = "TITLE"
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    lang = "en"
                    game_state = "TITLE"
                elif event.key == pygame.K_z:     
                    game_state = "TITLE"

            # --- SCHERMATA COMANDI E CHEAT ---
            elif game_state == "CONTROLS_SCREEN":
                if event.key == pygame.K_z:     
                    game_state = "TITLE"

            # --- GESTIONE DEI BIVI / SCHERMATE FINALI ---
            elif game_state == "POST_HEROES_CHOICE":
                if event.key == pygame.K_y:
                    game_state = "WORLD"
                    player_x, player_y = 7, 9  
                    world_msg = TEXT[lang]["heroes_defeated_go_temp"]
                elif event.key == pygame.K_n:
                    game_state = "ENDING_RIGHT_HAND"
                    
            elif game_state == "ENDING_RIGHT_HAND":
                reset_game()
                game_state = "TITLE"
                
            elif game_state == "GARLAND_DEFEATED_WAIT":
                if event.key == pygame.K_y:
                    game_state = "ENDING_CHAOS_LORD"
                    
            elif game_state == "ENDING_CHAOS_LORD":
                reset_game()
                game_state = "TITLE"

            elif game_state in ["WORLD", "CITY", "BATTLE"]:
                if event.key == pygame.K_v:
                    cheat_exp_x8 = not cheat_exp_x8
                    status = TEXT[lang]["activated"] if cheat_exp_x8 else TEXT[lang]["deactivated"]
                    msg_txt = f"{TEXT[lang]['cheat_exp']} {status}!"
                    if game_state == "BATTLE": battle_msg = msg_txt
                    else: world_msg = msg_txt
                
                elif event.key == pygame.K_m:
                    previous_state_for_input = game_state
                    game_state = "MUSCI_INPUT"
                    user_typed = ""
            
            # --- LOGICA DEL COMBATTIMENTO ---
            if game_state == "BATTLE":
                if event.key in [pygame.K_a, pygame.K_h]:
                    is_boss_fight = any(e.get("is_boss", False) for e in current_enemies)
                    is_garland_fight = any(e.get("is_garland", False) for e in current_enemies)
                    
                    target = current_enemies[enemy_turn_idx]
                    target_name = get_enemy_display_name(target)
                    
                    if event.key == pygame.K_h:
                        if not boss_defeated:
                            battle_msg = TEXT[lang]["hero_lock"]
                            continue
                        dmg_inflicted = player_atk * 2
                        msg_player = TEXT[lang]["use_hero"].format(name=target_name, dmg=dmg_inflicted)
                    else:
                        dmg_inflicted = player_atk
                        msg_player = TEXT[lang]["hit"].format(name=target_name, dmg=dmg_inflicted)
                    
                    target["hp"] -= dmg_inflicted
                    
                    if target.get("is_musci"):
                        msg_player += TEXT[lang]["useless"]
                    elif target["hp"] <= 0:
                        target["hp"] = 0
                        msg_player += TEXT[lang]["ko"]

                    all_dead = all(e["hp"] <= 0 for e in current_enemies if not e.get("is_musci")) and not any(e.get("is_musci") for e in current_enemies)
                    
                    if all_dead:
                        gained_exp = sum(get_enemy_exp(e["level"]) for e in current_enemies)
                        if cheat_exp_x8: gained_exp *= 8
                        player_exp += gained_exp
                        
                        while True:
                            req_exp = get_required_exp(player_level)
                            if player_exp >= req_exp:
                                player_exp -= req_exp
                                player_level += 1
                                hp_gain = random.randint(1, 10)
                                atk_gain = random.randint(1, 5)  
                                player_max_hp += hp_gain
                                player_atk += atk_gain
                                player_hp = player_max_hp
                            else:
                                break
                        
                        if is_garland_fight:
                            garland_defeated = True
                            game_state = "GARLAND_DEFEATED_WAIT"
                        elif is_boss_fight:
                            boss_defeated = True
                            game_state = "POST_HEROES_CHOICE"
                        else:
                            world_msg = TEXT[lang]["normal_win"].format(exp=gained_exp)
                            game_state = previous_state

                    else:
                        while current_enemies[enemy_turn_idx]["hp"] <= 0 and not current_enemies[enemy_turn_idx].get("is_musci"):
                            enemy_turn_idx = (enemy_turn_idx + 1) % len(current_enemies)
                            
                        attacker = current_enemies[enemy_turn_idx]
                        attacker_name = get_enemy_display_name(attacker)
                        
                        if attacker.get("is_musci"):
                            player_hp = 0
                            enemy_dmg_text = "∞"
                            atk_text = TEXT[lang]["musci_annihilate"]
                        elif attacker.get("is_mage", False) and random.randint(1, 100) <= 50:
                            enemy_dmg = random.randint(15, 22) 
                            player_hp -= enemy_dmg
                            enemy_dmg_text = str(enemy_dmg)
                            atk_text = TEXT[lang]["fireball"]
                        else:
                            enemy_dmg = attacker["atk"] 
                            player_hp -= enemy_dmg
                            enemy_dmg_text = str(enemy_dmg)
                            atk_text = TEXT[lang]["attack"]
                            
                        battle_msg = msg_player + f"{attacker_name} {atk_text} ({enemy_dmg_text} HP!)"
                        
                        enemy_turn_idx = (enemy_turn_idx + 1) % len(current_enemies)
                        while current_enemies[enemy_turn_idx]["hp"] <= 0 and not current_enemies[enemy_turn_idx].get("is_musci") and not all_dead:
                            enemy_turn_idx = (enemy_turn_idx + 1) % len(current_enemies)
                        
                        if player_hp <= 0:
                            if is_garland_fight:
                                reset_game("garland")
                            elif is_boss_fight:
                                reset_game("heroes")
                            else:
                                player_lives -= 1
                                if player_lives <= 0:
                                    reset_game("lives")
                                else:
                                    heroes_level += 1  
                                    world_msg = TEXT[lang]["dead_respawn"].format(lives=player_lives) + f" Gli Eroi salgono al Liv.{heroes_level}!"
                                    player_hp = int(player_max_hp * 0.5)
                                    game_state, player_x, player_y = "WORLD", 7, 2  

                elif event.key == pygame.K_r:  
                    is_boss_fight = any(e.get("is_boss", False) for e in current_enemies)
                    if is_boss_fight:
                        battle_msg = TEXT[lang]["boss_no_escape"]
                    else:
                        if random.randint(1, 100) <= 50:
                            world_msg = TEXT[lang]["escaped"]
                            game_state = previous_state  
                        else:
                            attacker = current_enemies[enemy_turn_idx]
                            attacker_name = get_enemy_display_name(attacker)
                            if attacker.get("is_musci"):
                                player_hp = 0
                                battle_msg = TEXT[lang]["escape_failed_musci"]
                            else:
                                enemy_dmg = attacker["atk"]
                                player_hp -= enemy_dmg
                                battle_msg = TEXT[lang]["escape_failed"].format(name=attacker_name, dmg=enemy_dmg)
                            
                            enemy_turn_idx = (enemy_turn_idx + 1) % len(current_enemies)
                            while current_enemies[enemy_turn_idx]["hp"] <= 0 and not current_enemies[enemy_turn_idx].get("is_musci"):
                                enemy_turn_idx = (enemy_turn_idx + 1) % len(current_enemies)
                            
                            if player_hp <= 0:
                                player_lives -= 1
                                if player_lives <= 0:
                                    reset_game("lives")
                                else:
                                    heroes_level += 1  
                                    world_msg = TEXT[lang]["escape_dead"].format(lives=player_lives) + f" Gli Eroi salgono al Liv.{heroes_level}!"
                                    player_hp = int(player_max_hp * 0.5)
                                    game_state, player_x, player_y = "WORLD", 7, 2

            # --- LOGICA DI MOVIMENTO E INCONTRI ---
            elif game_state in ["WORLD", "CITY"]:
                nx, ny = player_x, player_y
                moved = False
                if event.key == pygame.K_UP: ny -= 1; moved = True
                elif event.key == pygame.K_DOWN: ny += 1; moved = True
                elif event.key == pygame.K_LEFT: nx -= 1; moved = True
                elif event.key == pygame.K_RIGHT: nx += 1; moved = True
                    
                if moved and 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    can_move = False
                    
                    if game_state == "WORLD" and WORLD_MAP[ny][nx] not in [1, 3, 4]:
                        can_move = True
                    elif game_state == "CITY" and CITY_MAP[ny][nx] == 0:
                        can_move = True
                        
                    if can_move:
                        player_x, player_y = nx, ny
                        triggered_musci = False
                        
                        if not musci_spawned:
                            spawn_chance = 0.80 if cheat_musci else 1e-12
                            if random.random() < spawn_chance:
                                musci_spawned = True
                                triggered_musci = True
                                previous_state = game_state
                                game_state = "BATTLE"
                                enemy_turn_idx = 0
                                battle_msg = TEXT[lang]["musci_appear"]
                                current_enemies = [{"name": "Musci", "hp": float('inf'), "max_hp": float('inf'), "level": 99, "atk": float('inf'), "color": (50, 0, 50), "is_mage": False, "is_musci": True}]
                        
                        if not triggered_musci:
                            if game_state == "WORLD":
                                if boss_defeated and not garland_defeated and player_x == 7 and player_y == 2:
                                    previous_state = "WORLD"
                                    game_state = "BATTLE"
                                    enemy_turn_idx = 0
                                    battle_msg = TEXT[lang]["garland_speech"]
                                    current_enemies = [{"name": "Garland", "hp": 120, "max_hp": 120, "color": (110, 0, 110), "is_boss": True, "is_garland": True, "level": 10, "atk": 30, "is_mage": False}]
                                
                                elif WORLD_MAP[player_y][player_x] == 0: 
                                    if random.randint(1, 100) <= 25:
                                        previous_state = "WORLD"  
                                        game_state = "BATTLE"
                                        enemy_turn_idx = 0 
                                        battle_msg = TEXT[lang]["soldier_block"]
                                        enemy_lvl = get_enemy_level(player_level, 1, 4)
                                        hp_growth = sum(random.randint(1, 5) for _ in range(enemy_lvl - 1)) if enemy_lvl > 1 else 0
                                        en_max_hp = 35 + hp_growth
                                        atk_growth = sum(random.randint(1, 5) for _ in range(enemy_lvl - 1)) if enemy_lvl > 1 else 0
                                        en_atk = random.randint(1, 5) + atk_growth
                                        current_enemies = [{"name": "Soldato", "type": "soldier", "hp": en_max_hp, "max_hp": en_max_hp, "level": enemy_lvl, "atk": en_atk, "color": (160, 160, 170), "is_mage": False}]
                            
                            elif game_state == "CITY":
                                if random.randint(1, 100) <= 15:
                                    previous_state = "CITY"  
                                    game_state = "BATTLE"
                                    enemy_turn_idx = 0 
                                    
                                    # CHANCE DI SPAWN DEI BOSS MODIFICATA ALL'80%
                                    if player_level >= 8 and not boss_defeated and random.randint(1, 100) <= 80:
                                        battle_msg = TEXT[lang]["heroes_assault"]
                                        hp_bonus = (heroes_level - 8) * 10
                                        atk_bonus = (heroes_level - 8) * 2
                                        current_enemies = [
                                            {"name": "Guerriero", "name_key": "guerriero", "hp": 60+hp_bonus, "max_hp": 60+hp_bonus, "color": (190, 50, 50), "is_boss": True, "level": heroes_level, "atk": 16+atk_bonus, "is_mage": False},
                                            {"name": "Ninja", "name_key": "ninja", "hp": 60+hp_bonus, "max_hp": 60+hp_bonus, "color": (40, 40, 50), "is_boss": True, "level": heroes_level, "atk": 15+atk_bonus, "is_mage": False},
                                            {"name": "Stregone B.", "name_key": "stregone_b", "hp": 60+hp_bonus, "max_hp": 60+hp_bonus, "color": (230, 230, 240), "is_boss": True, "level": heroes_level, "atk": 12+atk_bonus, "is_mage": True},
                                            {"name": "Stregone N.", "name_key": "stregone_n", "hp": 60+hp_bonus, "max_hp": 60+hp_bonus, "color": (50, 50, 180), "is_boss": True, "level": heroes_level, "atk": 13+atk_bonus, "is_mage": True}
                                        ]
                                    else:
                                        enemy_lvl = get_enemy_level(player_level, 4, 8)
                                        hp_growth = sum(random.randint(1, 5) for _ in range(enemy_lvl - 1)) if enemy_lvl > 1 else 0
                                        en_max_hp = 35 + hp_growth
                                        atk_growth = sum(random.randint(1, 5) for _ in range(enemy_lvl - 1)) if enemy_lvl > 1 else 0
                                        en_atk = random.randint(1, 5) + atk_growth
                                        battle_msg = TEXT[lang]["guard_block"]
                                        current_enemies = [{"name": "Guardia", "type": "guard", "hp": en_max_hp, "max_hp": en_max_hp, "level": enemy_lvl, "atk": en_atk, "color": (200, 140, 40), "is_mage": False}]

    # TELETRASPORTI
    if game_state == "WORLD" and player_x == 7 and player_y == 10:
        game_state, player_x, player_y = "CITY", 7, 11
        world_msg = TEXT[lang]["enter_cornelia"]
    elif game_state == "CITY" and player_x == 7 and player_y == 14:
        game_state, player_x, player_y = "WORLD", 7, 11
        world_msg = TEXT[lang]["exit_cornelia"]

    screen.fill((0, 0, 0))

    draw_state = game_state
    if game_state == "MUSCI_INPUT":
        draw_state = previous_state_for_input

    # --- SCHERMATA DEL TITOLO ---
    if draw_state == "TITLE":
        screen.fill((10, 10, 25))
        title_surf = big_font.render(TEXT[lang]["title"], True, (255, 215, 0))
        start_surf = font.render(TEXT[lang]["press_start"], True, (255, 255, 255))
        lang_surf = font.render(TEXT[lang]["press_lang"], True, (140, 160, 230))
        keys_surf = font.render(TEXT[lang]["press_keys"], True, (140, 230, 160)) 
        
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 140))
        screen.blit(start_surf, (SCREEN_WIDTH // 2 - start_surf.get_width() // 2, 260))
        screen.blit(lang_surf, (SCREEN_WIDTH // 2 - lang_surf.get_width() // 2, 320))
        screen.blit(keys_surf, (SCREEN_WIDTH // 2 - keys_surf.get_width() // 2, 360))

    # --- SCHERMATA CAMBIO LINGUA ---
    elif draw_state == "LANG_SELECT":
        screen.fill((10, 10, 25))
        title_surf = big_font.render(TEXT[lang]["lang_title"], True, (240, 240, 240))
        it_surf = font.render("[1] Italiano", True, (100, 255, 100) if lang == "it" else (180, 180, 180))
        en_surf = font.render("[2] English", True, (100, 255, 100) if lang == "en" else (180, 180, 180))
        back_surf = font.render(TEXT[lang]["back"], True, (255, 100, 100))
        
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 120))
        screen.blit(it_surf, (SCREEN_WIDTH // 2 - it_surf.get_width() // 2, 220))
        screen.blit(en_surf, (SCREEN_WIDTH // 2 - en_surf.get_width() // 2, 260))
        screen.blit(back_surf, (SCREEN_WIDTH // 2 - back_surf.get_width() // 2, 350))

    # --- SCHERMATA COMANDI E CHEAT ---
    elif draw_state == "CONTROLS_SCREEN":
        screen.fill((10, 10, 25))
        title_surf = big_font.render(TEXT[lang]["controls_title"], True, (240, 240, 240))
        a_surf = font.render(TEXT[lang]["ctrl_a"], True, (255, 255, 255))
        r_surf = font.render(TEXT[lang]["ctrl_r"], True, (255, 255, 255))
        h_surf = font.render(TEXT[lang]["ctrl_h"], True, (255, 255, 255))
        v_surf = font.render(TEXT[lang]["ctrl_v"], True, (255, 215, 0))
        m_surf = font.render(TEXT[lang]["ctrl_m"], True, (255, 215, 0))
        back_surf = font.render(TEXT[lang]["back"], True, (255, 100, 100))
        
        screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 80))
        screen.blit(a_surf, (100, 160))
        screen.blit(r_surf, (100, 200))
        screen.blit(h_surf, (100, 240))
        v_text_w = v_surf.get_width()
        screen.blit(v_surf, (100, 290))
        screen.blit(m_surf, (100, 330))
        back_text_w = back_surf.get_width()
        screen.blit(back_surf, (SCREEN_WIDTH // 2 - back_text_w // 2, 420))

    # --- SCHERMATA SCELTA POST-BOSS E FINALI ---
    elif draw_state == "POST_HEROES_CHOICE":
        screen.fill((15, 15, 35))
        title_s = big_font.render(TEXT[lang]["choice_title"], True, (255, 215, 0))
        keys_s = font.render(TEXT[lang]["choice_keys"], True, (240, 240, 240))
        screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, 180))
        screen.blit(keys_s, (SCREEN_WIDTH // 2 - keys_s.get_width() // 2, 260))

    elif draw_state == "ENDING_RIGHT_HAND":
        screen.fill((10, 35, 15))
        title_s = big_font.render(TEXT[lang]["end_rh_title"], True, (100, 255, 100))
        msg_s = font.render(TEXT[lang]["end_rh_msg"], True, (240, 240, 240))
        anyk_s = font.render(TEXT[lang]["any_key_title"], True, (150, 150, 150))
        screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, 150))
        screen.blit(msg_s, (SCREEN_WIDTH // 2 - msg_s.get_width() // 2, 230))
        screen.blit(anyk_s, (SCREEN_WIDTH // 2 - anyk_s.get_width() // 2, 340))

    elif draw_state == "GARLAND_DEFEATED_WAIT":
        screen.fill((35, 15, 15))
        title_s = big_font.render(TEXT[lang]["comp_all_title"], True, (255, 100, 100))
        msg_s = font.render(TEXT[lang]["comp_all_msg"], True, (240, 240, 240))
        screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, 180))
        screen.blit(msg_s, (SCREEN_WIDTH // 2 - msg_s.get_width() // 2, 260))

    elif draw_state == "ENDING_CHAOS_LORD":
        screen.fill((45, 10, 10))
        title_s = big_font.render(TEXT[lang]["end_cl_title"], True, (255, 50, 50))
        msg_s = font.render(TEXT[lang]["end_cl_msg"], True, (240, 240, 240))
        anyk_s = font.render(TEXT[lang]["any_key_title"], True, (150, 150, 150))
        screen.blit(title_s, (SCREEN_WIDTH // 2 - title_s.get_width() // 2, 150))
        screen.blit(msg_s, (SCREEN_WIDTH // 2 - msg_s.get_width() // 2, 230))
        screen.blit(anyk_s, (SCREEN_WIDTH // 2 - anyk_s.get_width() // 2, 340))

    # --- RENDERING BATTAGLIA ---
    elif draw_state == "BATTLE":
        pygame.draw.rect(screen, (15, 20, 30), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT - 60))
        pygame.draw.rect(screen, (40, 45, 60), (20, 100, 220, 260))
        
        draw_player(screen, 112, 300) 
        
        current_req = get_required_exp(player_level)
        cheat_indicator = " [x8]" if cheat_exp_x8 else ""
        player_title = TEXT[lang]["player_chaos"] if garland_defeated else TEXT[lang]["player_goblin"]
        
        screen.blit(font.render(player_title, True, (255, 255, 255)), (30, 110))
        screen.blit(font.render(f"{TEXT[lang]['liv']}: {player_level}", True, (240, 200, 50)), (30, 140))
        
        hp_disp = 0 if player_hp < 0 else player_hp
        screen.blit(font.render(f"{TEXT[lang]['hp']}: {hp_disp}/{player_max_hp}", True, (100, 255, 100)), (30, 160))
        screen.blit(font.render(f"{TEXT[lang]['atk']}: {player_atk}", True, (255, 150, 150)), (30, 180))
        screen.blit(font.render(f"{TEXT[lang]['exp']}: {player_exp}/{current_req}{cheat_indicator}", True, (200, 200, 200)), (30, 200))
        screen.blit(font.render(f"{TEXT[lang]['vite']}: {player_lives}/3", True, (255, 80, 80)), (30, 220))

        pygame.draw.rect(screen, (30, 30, 45), (20, 380, 560, 60), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 150), (20, 380, 560, 60), 2, border_radius=8)
        
        commands_text = f"{TEXT[lang]['opt_attack']}      {TEXT[lang]['opt_escape']}"
        if boss_defeated:
            commands_text += f"      {TEXT[lang]['opt_hero']}"
            
        screen.blit(font.render(TEXT[lang]["comb_options"], True, (150, 200, 255)), (35, 390))
        screen.blit(font.render(commands_text, True, (255, 255, 255)), (35, 415))

        if len(current_enemies) > 0:
            active_enemy = current_enemies[enemy_turn_idx]
            offset_y = 140  
            
            pygame.draw.rect(screen, (200, 180, 40), (336, offset_y - 4, 248, 83), 2)
            pygame.draw.rect(screen, (60, 30, 30), (340, offset_y, 240, 75))
            
            is_boss = active_enemy.get("is_boss", False)
            is_garland = active_enemy.get("is_garland", False)
            is_musci = active_enemy.get("is_musci", False)
            
            enemy_img = None
            if is_garland: enemy_img = garland_image
            elif is_musci: enemy_img = musci_image
            elif is_boss: enemy_img = boss_images.get(active_enemy["name"])
            else:
                e_name = active_enemy["name"]
                if "Soldato" in e_name or active_enemy.get("type") == "soldier": enemy_img = soldato_image
                elif "Guardia" in e_name or active_enemy.get("type") == "guard": enemy_img = guardia_image

            if enemy_img is not None:
                screen.blit(enemy_img, (350, offset_y + 15))
            else:
                pygame.draw.rect(screen, active_enemy["color"], (350, offset_y + 15, 45, 45))
            
            e_display_name = get_enemy_display_name(active_enemy)
            screen.blit(font.render(e_display_name, True, (255, 255, 255)), (405, offset_y + 8))
            
            if is_musci:
                screen.blit(font.render("HP: N/A", True, (255, 100, 100)), (405, offset_y + 32))
                screen.blit(font.render(f"{TEXT[lang]['atk']}: {TEXT[lang]['infinite_text']}", True, (170, 170, 170)), (405, offset_y + 52))
            else:
                screen.blit(font.render(f"HP: {active_enemy['hp']}/{active_enemy['max_hp']}", True, (255, 100, 100)), (405, offset_y + 32))
                screen.blit(font.render(f"{TEXT[lang]['atk']}: {active_enemy['atk']}", True, (170, 170, 170)), (405, offset_y + 52))

            alive_count = sum(1 for e in current_enemies if e["hp"] > 0 or e.get("is_musci"))
            if alive_count > 1:
                 screen.blit(font.render(TEXT[lang]["others_queue"].format(count=alive_count - 1), True, (150, 150, 150)), (340, offset_y + 85))

        screen.blit(big_font.render(TEXT[lang]["combat_title"], True, (255, 60, 60)), (20, 20))
        msg = battle_msg

    # --- RENDERING MONDO E CITTÀ ---
    elif draw_state in ["WORLD", "CITY"]:
        if draw_state == "WORLD":
            for r in range(MAP_HEIGHT):
                for c in range(MAP_WIDTH):
                    tile = WORLD_MAP[r][c]
                    px, py = c * TILE_SIZE, r * TILE_SIZE
                    if tile in [0, 2, 3]: draw_grass(screen, px, py)
                    elif tile == 1: draw_water(screen, px, py)
                    elif tile == 4: draw_mountain(screen, px, py)
                    if tile == 2: draw_cornelia_world(screen, px, py)
                    elif tile == 3: draw_chaos_shrine(screen, px, py)
            
            if boss_defeated and not garland_defeated:
                if garland_image is not None:
                    screen.blit(garland_image, (7 * TILE_SIZE, 2 * TILE_SIZE))
                else:
                    pygame.draw.rect(screen, (110, 0, 110), (7 * TILE_SIZE + 4, 2 * TILE_SIZE + 4, TILE_SIZE - 8, TILE_SIZE - 8))
                    
            draw_player(screen, player_x * TILE_SIZE, player_y * TILE_SIZE)
            msg = world_msg

        elif draw_state == "CITY":
            for r in range(MAP_HEIGHT):
                for c in range(MAP_WIDTH):
                    draw_city_grass(screen, c * TILE_SIZE, r * TILE_SIZE)
            
            for r in range(MAP_HEIGHT):
                if r == player_y: draw_player(screen, player_x * TILE_SIZE, player_y * TILE_SIZE)
                for c in range(MAP_WIDTH):
                    tile = CITY_MAP[r][c]
                    px, py = c * TILE_SIZE, r * TILE_SIZE
                    if tile == 7: draw_city_wall(screen, px, py)
                    elif tile == 8: draw_tall_tree(screen, px, py)
                    elif tile == 9: draw_tall_house(screen, px, py)
            
            if garland_defeated:
                msg = TEXT[lang]["world_safe"]
            elif boss_defeated:
                msg = TEXT[lang]["heroes_defeated_go_temp"]
            else:
                msg = TEXT[lang]["city_msg"].format(lvl=player_level)
                if player_level < 8: 
                    msg += TEXT[lang]["reach_lvl8"]
                else: 
                    msg += TEXT[lang]["heroes_warning"].format(lvl=heroes_level)

        # DISEGNO DEL CONTATORE DELLE RUN
        run_txt = TEXT[lang]["run_text"].format(count=run_count)
        run_surf = font.render(run_txt, True, (255, 255, 255))
        rx = SCREEN_WIDTH - run_surf.get_width() - 15
        ry = 15
        pygame.draw.rect(screen, (20, 20, 30), (rx - 8, ry - 5, run_surf.get_width() + 16, run_surf.get_height() + 10), border_radius=4)
        pygame.draw.rect(screen, (255, 215, 0), (rx - 8, ry - 5, run_surf.get_width() + 16, run_surf.get_height() + 10), 2, border_radius=4)
        screen.blit(run_surf, (rx, ry))

    # BOX DI TESTO IN BASSO
    if draw_state in ["WORLD", "CITY", "BATTLE"]:
        pygame.draw.rect(screen, COLOR_BOX, (0, MAP_HEIGHT * TILE_SIZE, SCREEN_WIDTH, 60))
        pygame.draw.rect(screen, COLOR_TEXT, (4, MAP_HEIGHT * TILE_SIZE + 4, SCREEN_WIDTH - 8, 52), 2)
        screen.blit(font.render(msg, True, COLOR_TEXT), (15, MAP_HEIGHT * TILE_SIZE + 20))

    # --- RENDERING CONSOLE MUSCI ---
    if game_state == "MUSCI_INPUT":
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        screen.blit(s, (0,0))
        
        pygame.draw.rect(screen, (20, 20, 30), (50, 200, 500, 100), border_radius=5)
        pygame.draw.rect(screen, (100, 200, 100), (50, 200, 500, 100), 2, border_radius=5)
        
        prompt_surf = font.render("Console (ESC per uscire, INVIO conferma):", True, (200, 200, 200))
        screen.blit(prompt_surf, (70, 215))
        
        input_text = f'print("{user_typed}")'
        input_surf = big_font.render(input_text, True, (100, 255, 100))
        screen.blit(input_surf, (70, 250))
        
        if pygame.time.get_ticks() % 1000 < 500:
            cursor_x = 70 + input_surf.get_width() - 20
            pygame.draw.rect(screen, (100, 255, 100), (cursor_x, 252, 12, 22))

    pygame.display.flip()
    clock.tick(30)
