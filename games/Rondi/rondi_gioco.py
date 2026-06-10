import pygame
import sys
import random
import math

# Inizializzazione Pygame
pygame.init()
pygame.font.init()

# Costanti di Gioco
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
CLAY_RED = (180, 70, 50)     
COURT_GREEN = (40, 120, 70)  
YELLOW = (255, 255, 0)
RED = (220, 20, 60)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tennis Career Simulator")
clock = pygame.time.Clock()

font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 32)
font_large = pygame.font.Font(None, 50)
font_titolo = pygame.font.Font(None, 80) 

NOMI_STRANIERI = ["Roger", "Rafa", "Novak", "Carlos", "Jannik", "Daniil", "Stefanos", "Alexander", "Taylor", "Casper"]
COGNOMI_STRANIERI = ["Smith", "Federer", "Nadal", "Djokovic", "Alcaraz", "Sinner", "Medvedev", "Tsitsipas", "Zverev", "Ruud"]

def genera_avversario(livello_torneo):
    nome = f"{random.choice(NOMI_STRANIERI)} {random.choice(COGNOMI_STRANIERI)}"
    
    if livello_torneo >= 5:
        moltiplicatore_livello = 4 + (livello_torneo - 4) * 0.25
    else:
        moltiplicatore_livello = livello_torneo
        
    velocita = 1.6 + (moltiplicatore_livello * 0.6)
    potenza = 2.5 + (moltiplicatore_livello * 0.7)
    battuta = 2.5 + (moltiplicatore_livello * 0.6)
    
    return {"nome": nome, "velocita": min(velocita, 6.8), "potenza": min(potenza, 11.0), "battuta": min(battuta, 10.0)}

class Giocatore:
    def __init__(self, nome):
        self.nome = nome
        self.livello_torneo = 1
        self.soldi = 0
        self.velocita = 4.5
        self.potenza = 4.5
        self.battuta = 4.5  
        self.partite_vinte = 0

    def potenzia_velocita(self):
        costo = int(self.velocita * 50)
        if self.soldi >= costo and self.velocita < 10:
            self.soldi -= costo
            self.velocita += 0.5
            return True
        return False

    def potenzia_potenza(self):
        costo = int(self.potenza * 50)
        if self.soldi >= costo and self.potenza < 10:
            self.soldi -= costo
            self.potenza += 0.5
            return True
        return False

    def potenzia_battuta(self):  
        costo = int(self.battuta * 50)
        if self.soldi >= costo and self.battuta < 10:
            self.soldi -= costo
            self.battuta += 0.5
            return True
        return False

# Stati del Gioco
STATO_INTRO_TITOLO = 0
STATO_MENU_INIZIALE = 1
STATO_HUB_CARRIERA = 2
STATO_MATCH = 3
STATO_GAME_OVER = 4

stato_attuale = STATO_INTRO_TITOLO 
giocatore_principale = None
avversario_attuale = None

# Dimensioni e Coordinate Campo da Gioco (Verde)
COURT_X = 80
COURT_Y = 110 
COURT_W = WIDTH - 160
COURT_H = HEIGHT - 180

# Limiti del campo di singolare
CORRIDOIO_H = 40
SINGLES_Y_TOP = COURT_Y + CORRIDOIO_H
SINGLES_Y_BOTTOM = COURT_Y + COURT_H - CORRIDOIO_H

# Variabili del Match
player_x = COURT_X + 10
player_y = HEIGHT // 2 - 45
opp_x = COURT_X + COURT_W - 25
opp_y = HEIGHT // 2 - 45
paddle_width = 15
paddle_height = 70

ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = 0
ball_speed_y = 0
ball_radius = 8

player_score = 0
opp_score = 0

messaggio_match = ""
timer_messaggio_match = 0
scia_pallina = [] 

timer_applausi = 0
tifosi_applaudono = False
posizioni_tifosi_sopra = [(x, random.randint(15, 30)) for x in range(40, WIDTH - 40, 25)]
posizioni_tifosi_sotto = [(x, random.randint(HEIGHT - 30, HEIGHT - 15)) for x in range(40, WIDTH - 40, 25)]

falli_battuta = 0
battitore_attuale = 1 
in_battuta = True 
palla_controllata_per_fallo = False
timer_battuta_cpu = 0
ultimo_tocco = 0  

def prepara_battuta(reset_falli=True):
    global ball_x, ball_y, ball_speed_x, ball_speed_y, in_battuta, timer_battuta_cpu, player_x, player_y, opp_x, opp_y, falli_battuta, palla_controllata_per_fallo, scia_pallina, ultimo_tocco
    in_battuta = True
    palla_controllata_per_fallo = False
    ball_speed_x = 0
    ball_speed_y = 0
    timer_battuta_cpu = pygame.time.get_ticks()
    scia_pallina.clear() 
    
    if reset_falli:
        falli_battuta = 0

    quadrante_sopra = ((player_score + opp_score) % 2 == 1)

    player_x = COURT_X + 5
    opp_x = COURT_X + COURT_W - paddle_width - 5

    if battitore_attuale == 1:
        ultimo_tocco = 1
        player_y = (SINGLES_Y_TOP + 20) if quadrante_sopra else (SINGLES_Y_BOTTOM - paddle_height - 20)
        opp_y = (SINGLES_Y_BOTTOM - paddle_height - 20) if quadrante_sopra else (SINGLES_Y_TOP + 20)
    else:
        ultimo_tocco = 2
        opp_y = (SINGLES_Y_TOP + 20) if quadrante_sopra else (SINGLES_Y_BOTTOM - paddle_height - 20)
        player_y = (SINGLES_Y_BOTTOM - paddle_height - 20) if quadrante_sopra else (SINGLES_Y_TOP + 20)

def attiva_applausi():
    global timer_applausi, tifosi_applaudono
    tifosi_applaudono = True
    timer_applausi = pygame.time.get_ticks()

def disegna_testo(testo, font, colore, x, y, centro=False):
    superficie = font.render(testo, True, colore)
    rettangolo = superficie.get_rect()
    if centro:
        rettangolo.center = (x, y)
    else:
        rettangolo.topleft = (x, y)
    screen.blit(superficie, rettangolo)

def disegna_bottone(testo, x, y, w, h, colore_base, colore_hover):
    mouse = pygame.mouse.get_pos()
    cliccato = pygame.mouse.get_pressed()[0]
    
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, colore_hover, (x, y, w, h), border_radius=8)
        if cliccato:
            pygame.time.delay(180)  
            return True
    else:
        pygame.draw.rect(screen, colore_base, (x, y, w, h), border_radius=8)
        
    disegna_testo(testo, font_small, WHITE, x + w//2, y + h//2, centro=True)
    return False

# --- LOOP PRINCIPALE ---
running = True
input_nome = ""

while running:
    screen.fill(BLACK)
    mouse_click = False
    tempo_corrente = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_click = True
            
        if stato_attuale == STATO_MENU_INIZIALE and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                input_nome = input_nome[:-1]
            elif event.key == pygame.K_RETURN:
                giocatore_principale = Giocatore(input_nome.strip() if input_nome.strip() != "" else "Giocatore 1")
                stato_attuale = STATO_HUB_CARRIERA
            else:
                if len(input_nome) < 16 and (event.unicode.isalnum() or event.unicode in [" ", "-", "'"]):
                    input_nome += event.unicode

    if not running:
        break

    # 0. SCHERMATA INTRO TITOLO
    if stato_attuale == STATO_INTRO_TITOLO:
        disegna_testo("PONG TENNIS", font_titolo, YELLOW, WIDTH//2, HEIGHT//2 - 80, centro=True)
        disegna_testo("Career Simulator Edition", font_small, GRAY, WIDTH//2, HEIGHT//2 - 20, centro=True)
        
        if disegna_bottone("START", WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50, COURT_GREEN, CLAY_RED):
            stato_attuale = STATO_MENU_INIZIALE

    # 1. MENU INIZIALE (NOME GIOCATORE)
    elif stato_attuale == STATO_MENU_INIZIALE:
        disegna_testo("CREAZIONE GIOCATORE", font_large, YELLOW, WIDTH//2, 100, centro=True)
        disegna_testo("Scrivi il nome del tuo giocatore:", font_medium, WHITE, WIDTH//2, 220, centro=True)
        
        box_color = RED if input_nome.strip() == "" else CLAY_RED
        pygame.draw.rect(screen, box_color, (WIDTH//2 - 175, 270, 350, 50), border_radius=6)
        
        testo_da_mostrare = input_nome if input_nome != "" else "Digita qui..."
        colore_testo = GRAY if input_nome == "" else WHITE
        disegna_testo(testo_da_mostrare, font_medium, colore_testo, WIDTH//2, 295, centro=True)
        
        disegna_testo("Premi INVIO o clicca sotto per confermare", font_small, GRAY, WIDTH//2, 340, centro=True)
        
        if disegna_bottone("CONFERMA", WIDTH//2 - 110, 400, 220, 50, COURT_GREEN, CLAY_RED):
            giocatore_principale = Giocatore(input_nome.strip() if input_nome.strip() != "" else "Giocatore 1")
            stato_attuale = STATO_HUB_CARRIERA

    # 2. HUB CARRIERA
    elif stato_attuale == STATO_HUB_CARRIERA:
        disegna_testo(f"Carriera di: {giocatore_principale.nome}", font_large, CLAY_RED, WIDTH//2, 40, centro=True)
        
        pygame.draw.rect(screen, GRAY, (50, 120, 320, 380), border_radius=10)
        disegna_testo("SCHEDA ATLETA", font_medium, YELLOW, 70, 140)
        disegna_testo(f"Velocita: {giocatore_principale.velocita:.1f} / 10", font_small, WHITE, 70, 190)
        disegna_testo(f"Potenza: {giocatore_principale.potenza:.1f} / 10", font_small, WHITE, 70, 230)
        disegna_testo(f"Battuta: {giocatore_principale.battuta:.1f} / 10", font_small, WHITE, 70, 270) 
        disegna_testo(f"Fondi Disponibili: {giocatore_principale.soldi} EUR", font_medium, COURT_GREEN, 70, 330)
        disegna_testo(f"Tornei Vinti: {giocatore_principale.partite_vinte}", font_small, WHITE, 70, 400)

        costo_vel = int(giocatore_principale.velocita * 50)
        costo_pot = int(giocatore_principale.potenza * 50)
        costo_bat = int(giocatore_principale.battuta * 50)
        
        if giocatore_principale.velocita < 10:
            if disegna_bottone(f"Allena Velocita ({costo_vel} EUR)", 420, 130, 320, 40, CLAY_RED, COURT_GREEN):
                giocatore_principale.potenzia_velocita()
        else:
            disegna_testo("Velocita Livello Massimo", font_small, YELLOW, 420, 140)
            
        if giocatore_principale.potenza < 10:
            if disegna_bottone(f"Allena Potenza ({costo_pot} EUR)", 420, 185, 320, 40, CLAY_RED, COURT_GREEN):
                giocatore_principale.potenzia_potenza()
        else:
            disegna_testo("Potenza Livello Massimo", font_small, YELLOW, 420, 195)

        if giocatore_principale.battuta < 10:
            if disegna_bottone(f"Allena Battuta ({costo_bat} EUR)", 420, 240, 320, 40, CLAY_RED, COURT_GREEN):
                giocatore_principale.potenzia_battuta()
        else:
            disegna_testo("Battuta Livello Massimo", font_small, YELLOW, 420, 250)

        pygame.draw.rect(screen, RED, (420, 310, 320, 130), border_radius=10)
        if avversario_attuale is None:
            avversario_attuale = genera_avversario(giocatore_principale.livello_torneo)
            
        disegna_testo(f"PROSSIMO TORNEO: LIVELLO {giocatore_principale.livello_torneo}", font_small, YELLOW, 440, 325)
        disegna_testo(f"Avversario: {avversario_attuale['nome']}", font_small, WHITE, 440, 355)
        disegna_testo(f"Difficolta IA: {giocatore_principale.livello_torneo}", font_small, WHITE, 440, 385)

        if disegna_bottone("GIOCA MATCH", 420, 460, 320, 50, COURT_GREEN, YELLOW):
            player_score = 0
            opp_score = 0
            battitore_attuale = 1 
            prepara_battuta(reset_falli=True)
            stato_attuale = STATO_MATCH

    # 3. IL MATCH
    elif stato_attuale == STATO_MATCH:
        screen.fill(CLAY_RED)
        
        if tifosi_applaudono and tempo_corrente - timer_applausi > 1500:
            tifosi_applaudono = False

        # DISEGNO TIFOSI
        colore_tifosi = YELLOW if tifosi_applaudono else DARK_GRAY
        for pos in posizioni_tifosi_sopra:
            pygame.draw.circle(screen, colore_tifosi, pos, 6)
            if tifosi_applaudono and random.random() > 0.7:
                disegna_testo("Clap!", font_small, WHITE, pos[0]-10, pos[1]+8)
                
        for pos in posizioni_tifosi_sotto:
            pygame.draw.circle(screen, colore_tifosi, pos, 6)
            if tifosi_applaudono and random.random() > 0.7:
                disegna_testo("Clap!", font_small, WHITE, pos[0]-10, pos[1]-18)

        # TRACCIAMENTO DEL CAMPO DI TENNIS
        pygame.draw.rect(screen, COURT_GREEN, (COURT_X, COURT_Y, COURT_W, COURT_H))
        pygame.draw.rect(screen, WHITE, (COURT_X, COURT_Y, COURT_W, COURT_H), 3) 
        
        pygame.draw.line(screen, WHITE, (COURT_X, SINGLES_Y_TOP), (COURT_X + COURT_W, SINGLES_Y_TOP), 3)
        pygame.draw.line(screen, WHITE, (COURT_X, SINGLES_Y_BOTTOM), (COURT_X + COURT_W, SINGLES_Y_BOTTOM), 3)
        
        pygame.draw.line(screen, WHITE, (WIDTH // 2, COURT_Y), (WIDTH // 2, COURT_Y + COURT_H), 4) 
        
        DISTR_BATTUTA_X = 140
        pygame.draw.line(screen, WHITE, (WIDTH // 2 - DISTR_BATTUTA_X, SINGLES_Y_TOP), (WIDTH // 2 - DISTR_BATTUTA_X, SINGLES_Y_BOTTOM), 3)
        pygame.draw.line(screen, WHITE, (WIDTH // 2 + DISTR_BATTUTA_X, SINGLES_Y_TOP), (WIDTH // 2 + DISTR_BATTUTA_X, SINGLES_Y_BOTTOM), 3)
        pygame.draw.line(screen, WHITE, (WIDTH // 2 - DISTR_BATTUTA_X, HEIGHT // 2), (WIDTH // 2 + DISTR_BATTUTA_X, HEIGHT // 2), 3)
        
        pygame.draw.line(screen, WHITE, (COURT_X, HEIGHT // 2), (COURT_X + 15, HEIGHT // 2), 3)
        pygame.draw.line(screen, WHITE, (COURT_X + COURT_W - 15, HEIGHT // 2), (COURT_X + COURT_W, HEIGHT // 2), 3)

        # MOVIMENTO GIOCATORE
        if not in_battuta:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and player_y > COURT_Y:
                player_y -= giocatore_principale.velocita
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player_y < COURT_Y + COURT_H - paddle_height:
                player_y += giocatore_principale.velocita
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_x > COURT_X:
                player_x -= giocatore_principale.velocita
            if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_x < (WIDTH // 2) - paddle_width - 5:
                player_x += giocatore_principale.velocita

        # IA AVVERSARIO (AGGIORNATA: NON GIOCA PIÙ SOTTO RETE)
        if not in_battuta:
            centro_ia_y = opp_y + paddle_height // 2
            centro_ia_x = opp_x + paddle_width // 2
            
            if giocatore_principale.livello_torneo >= 5:
                ritardo_ia = 15 
            else:
                ritardo_ia = max(0, 35 - (giocatore_principale.livello_torneo * 8))
            
            if random.randint(0, 100) > ritardo_ia:
                # Movimento Verticale (Inseguimento asse Y)
                if ball_y < centro_ia_y and opp_y > COURT_Y:
                    opp_y -= avversario_attuale["velocita"]
                if ball_y > centro_ia_y and opp_y < COURT_Y + COURT_H - paddle_height:
                    opp_y += avversario_attuale["velocita"]
                
                # Movimento Orizzontale (Asse X)
                if ball_speed_x > 0:  
                    # La pallina arriva verso l'IA: avanza per colpire ma con un LIMITE (non va sotto rete)
                    limite_avanzamento_rete = (WIDTH // 2) + (COURT_W // 4) # Blocca l'IA nella sua metà campo difensiva
                    
                    if ball_x < centro_ia_x and opp_x > limite_avanzamento_rete:
                        opp_x -= avversario_attuale["velocita"] * 0.8
                    elif ball_x > centro_ia_x and opp_x < COURT_X + COURT_W - paddle_width:
                        opp_x += avversario_attuale["velocita"] * 0.8
                else: 
                    # La pallina si allontana (va verso il giocatore): l'IA TORNA A FONDO CAMPO (Baseline)
                    posizione_attesa_x = COURT_X + COURT_W - paddle_width - 25 # Molto arretrata vicino la linea di fondo
                    if opp_x < posizione_attesa_x:
                        opp_x += avversario_attuale["velocita"] * 0.7 # Torna indietro rapidamente
                    elif opp_x > posizione_attesa_x:
                        opp_x -= avversario_attuale["velocita"] * 0.5

        quadrante_sopra = ((player_score + opp_score) % 2 == 1)

        # GESTIONE DELLA BATTUTA E DEL MIRINO
        if in_battuta:
            if battitore_attuale == 1:
                ball_x = player_x + paddle_width + ball_radius + 2
                ball_y = player_y + paddle_height // 2
                
                mx, my = pygame.mouse.get_pos()
                target_x = max(WIDTH // 2 + 10, min(mx, COURT_X + COURT_W - 20))
                target_y = max(SINGLES_Y_TOP + 10, min(my, SINGLES_Y_BOTTOM - 10))
                
                pygame.draw.circle(screen, YELLOW, (target_x, target_y), 12, 2)
                pygame.draw.circle(screen, RED, (target_x, target_y), 2)
                pygame.draw.line(screen, GRAY, (ball_x, ball_y), (target_x, target_y), 1)
                
                disegna_testo("SPOSTA IL MIRINO CON IL MOUSE E CLICCA PER BATTERE", font_small, YELLOW, WIDTH//2, HEIGHT - 30, centro=True)
                
                if mouse_click:
                    in_battuta = False
                    dx = target_x - ball_x
                    dy = target_y - ball_y
                    dist = math.hypot(dx, dy)
                    
                    sp_totale = (6.5 + giocatore_principale.battuta * 0.4)
                    ball_speed_x = (dx / dist) * sp_totale
                    ball_speed_y = (dy / dist) * sp_totale
            else:
                ball_x = opp_x - ball_radius - 2
                ball_y = opp_y + paddle_height // 2
                
                if tempo_corrente - timer_battuta_cpu > 1500:
                    in_battuta = False
                    sp_totale = (6.0 + avversario_attuale["battuta"] * 0.5)
                    
                    bersaglio_x = WIDTH // 2 - 60 
                    if quadrante_sopra:
                        bersaglio_y = random.randint(int(HEIGHT // 2) + 15, int(SINGLES_Y_BOTTOM) - 15)
                    else:
                        bersaglio_y = random.randint(int(SINGLES_Y_TOP) + 15, int(HEIGHT // 2) - 15)
                    
                    dx = bersaglio_x - ball_x
                    dy = bersaglio_y - ball_y
                    dist = math.hypot(dx, dy)
                    
                    ball_speed_x = (dx / dist) * sp_totale
                    ball_speed_y = (dy / dist) * sp_totale
        else:
            ball_x += ball_speed_x
            ball_y += ball_speed_y
            scia_pallina.append({"x": ball_x, "y": ball_y, "tempo": tempo_corrente})

        # LOGICA DEI FALLI DI BATTUTA
        if not in_battuta and not palla_controllata_per_fallo:
            if ball_speed_x > 0 and ball_x >= WIDTH // 2:
                palla_controllata_per_fallo = True
                quadrante_ball_sopra = ball_y < HEIGHT // 2
                quadrante_opp_sopra = (opp_y + paddle_height // 2) < HEIGHT // 2
                
                if quadrante_ball_sopra != quadrante_opp_sopra:
                    falli_battuta += 1
                    if falli_battuta >= 2:
                        opp_score += 1
                        attiva_applausi()
                        messaggio_match = "DOPPIO FALLO! PUNTO ALL'AVVERSARIO"
                        battitore_attuale = -1  
                        prepara_battuta(reset_falli=True)
                    else:
                        messaggio_match = "FALLO DI BATTUTA! (2° SERVIZIO)"
                        prepara_battuta(reset_falli=False)
                    timer_messaggio_match = tempo_corrente

            elif ball_speed_x < 0 and ball_x <= WIDTH // 2:
                palla_controllata_per_fallo = True
                quadrante_ball_sopra = ball_y < HEIGHT // 2
                quadrante_player_sopra = (player_y + paddle_height // 2) < HEIGHT // 2
                
                if quadrante_ball_sopra != quadrante_player_sopra:
                    falli_battuta += 1
                    if falli_battuta >= 2:
                        player_score += 1
                        attiva_applausi()
                        messaggio_match = "DOPPIO FALLO CPU! PUNTO A TE"
                        battitore_attuale = 1  
                        prepara_battuta(reset_falli=True)
                    else:
                        messaggio_match = "FALLO BATTUTA CPU! (2° SERVIZIO)"
                        prepara_battuta(reset_falli=False)
                    timer_messaggio_match = tempo_corrente

        # LOGICA DI RIMBALZO E PUNTEGGIO
        if not in_battuta:
            if ball_y - ball_radius <= COURT_Y:
                ball_speed_y *= -1
                ball_y = COURT_Y + ball_radius
            elif ball_y + ball_radius >= COURT_Y + COURT_H:
                ball_speed_y *= -1
                ball_y = COURT_Y + COURT_H - ball_radius

            if ball_x - ball_radius <= COURT_X:
                opp_score += 1
                attiva_applausi()
                battitore_attuale = -1 if battitore_attuale == 1 else 1 
                prepara_battuta(reset_falli=True)
            elif ball_x + ball_radius >= COURT_X + COURT_W:
                player_score += 1
                attiva_applausi()
                battitore_attuale = -1 if battitore_attuale == 1 else 1 
                prepara_battuta(reset_falli=True)

        # COLLISIONI RACCHETTE DINAMICHE IN 2D
        if not in_battuta:
            if player_x <= ball_x - ball_radius <= player_x + paddle_width and ball_speed_x < 0:
                if player_y <= ball_y <= player_y + paddle_height:
                    punto_impatto = (ball_y - (player_y + paddle_height / 2)) / (paddle_height / 2)
                    ball_speed_x = (5.5 + giocatore_principale.potenza * 0.4)
                    ball_speed_y = punto_impatto * 5.5
                    ball_x = player_x + paddle_width + ball_radius + 1
                    ultimo_tocco = 1

            if opp_x <= ball_x + ball_radius <= opp_x + paddle_width and ball_speed_x > 0:
                if opp_y <= ball_y <= opp_y + paddle_height:
                    punto_impatto = (ball_y - (opp_y + paddle_height / 2)) / (paddle_height / 2)
                    ball_speed_x = -(5.5 + avversario_attuale["potenza"] * 0.4)
                    ball_speed_y = punto_impatto * 5.5
                    ball_x = opp_x - ball_radius - 1
                    ultimo_tocco = 2

        # DISEGNO DELLE OMBRE
        scia_pallina = [ombra for ombra in scia_pallina if tempo_corrente - ombra["tempo"] < 2000]
        for ombra in scia_pallina:
            tempo_vissuto = tempo_corrente - ombra["tempo"]
            fattore_dissolvenza = 1.0 - (tempo_vissuto / 2000.0)
            r_ombra = max(1, int(ball_radius * fattore_dissolvenza))
            colore_ombra = (25, 75, 45) 
            pygame.draw.circle(screen, colore_ombra, (int(ombra["x"]), int(ombra["y"]) + 6), r_ombra)

        # Grafica elementi attivi
        pygame.draw.rect(screen, WHITE, (player_x, player_y, paddle_width, paddle_height), border_radius=4)
        pygame.draw.rect(screen, WHITE, (opp_x, opp_y, paddle_width, paddle_height), border_radius=4)
        pygame.draw.circle(screen, YELLOW, (int(ball_x), int(ball_y)), ball_radius) 

        if tempo_corrente - timer_messaggio_match < 2000 and messaggio_match != "":
            disegna_testo(messaggio_match, font_medium, WHITE, WIDTH // 2, 95, centro=True)

        # TABELLONE SEGNAPUNTI AD ALTA VISIBILITÀ
        # Box Player 1 (Sinistra)
        pygame.draw.rect(screen, BLACK, (40, 45, 260, 45), border_radius=6)
        pygame.draw.rect(screen, WHITE, (40, 45, 260, 45), 2, border_radius=6)
        disegna_testo(f"{giocatore_principale.nome.upper()}", font_small, WHITE, 55, 58)
        disegna_testo(f"{player_score}", font_large, YELLOW, 265, 53)

        # Box CPU (Destra)
        pygame.draw.rect(screen, BLACK, (WIDTH - 300, 45, 260, 45), border_radius=6)
        pygame.draw.rect(screen, WHITE, (WIDTH - 300, 45, 260, 45), 2, border_radius=6)
        disegna_testo(f"{avversario_attuale['nome'].upper()}", font_small, WHITE, WIDTH - 285, 58)
        disegna_testo(f"{opp_score}", font_large, YELLOW, WIDTH - 75, 53)

        if player_score >= 5 or opp_score >= 5:
            stato_attuale = STATO_GAME_OVER

    # 4. SCHERMATA DI FINE MATCH
    elif stato_attuale == STATO_GAME_OVER:
        if player_score >= 5:
            disegna_testo("GAME, SET, MATCH!", font_large, YELLOW, WIDTH//2, 100, centro=True)
            disegna_testo("VITTORIA NEL TORNEO!", font_large, COURT_GREEN, WIDTH//2, 170, centro=True)
            
            soldi_vinti = giocatore_principale.livello_torneo * 150
            disegna_testo(f"Hai sconfitto {avversario_attuale['nome']}!", font_small, WHITE, WIDTH//2, 240, centro=True)
            disegna_testo(f"Premio in denaro: +{soldi_vinti} EUR", font_medium, YELLOW, WIDTH//2, 290, centro=True)
            
            if disegna_bottone("AVANZA AL PROSSIMO TORNEO", WIDTH//2 - 160, 410, 320, 50, COURT_GREEN, CLAY_RED):
                giocatore_principale.soldi += soldi_vinti
                giocatore_principale.partite_vinte += 1
                giocatore_principale.livello_torneo += 1  
                avversario_attuale = None  
                stato_attuale = STATO_HUB_CARRIERA
        else:
            disegna_testo("SCONFITTA!", font_large, RED, WIDTH//2, 160, centro=True)
            disegna_testo(f"Sei stato eliminato da {avversario_attuale['nome']}.", font_small, WHITE, WIDTH//2, 230, centro=True)
            
            if disegna_bottone("TORNA ALL'HUB", WIDTH//2 - 110, 400, 220, 50, RED, CLAY_RED):
                avversario_attuale = None  
                stato_attuale = STATO_HUB_CARRIERA

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
