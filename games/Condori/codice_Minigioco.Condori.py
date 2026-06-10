import pygame
import random
import sys
from pathlib import Path


ASSET_DIR = Path(__file__).resolve().parent

# --- CONFIGURAZIONE INIZIALE ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orbital Cleanup: La Sfida di MATATO")
clock = pygame.time.Clock()
font_piccolo = pygame.font.SysFont("Arial", 22)
font_medio = pygame.font.SysFont("Arial", 26, bold=True)
font_grande = pygame.font.SysFont("Arial", 40, bold=True)

# Colori (RGB)
NERO = (10, 10, 20)
BIANCO = (255, 255, 255)
ROSSO = (255, 50, 50)
VERDE = (50, 255, 50)
ORO = (255, 215, 0)
BLU = (50, 150, 255)
VIOLA = (160, 32, 240)

# --- GENERAZIONE PARTICELLE DELLA NEVE ---
NUMERO_FIOCCHI = 100
lista_neve = []
for i in range(NUMERO_FIOCCHI):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    velocita_caduta = random.randint(1, 3)
    lista_neve.append([x, y, velocita_caduta])

# --- FUNZIONE AGGIORNAMENTO NEVE ---
def aggiorna_e_disegna_neve():
    for fiocco in lista_neve:
        fiocco[1] += fiocco[2]
        if fiocco[1] > HEIGHT:
            fiocco[1] = random.randint(-20, -1)
            fiocco[0] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, BIANCO, (fiocco[0], fiocco[1]), 2)


def carica_immagine(nome_file, dimensione, colore_fallback):
    try:
        percorso = ASSET_DIR / nome_file
        immagine = pygame.image.load(percorso).convert_alpha()
        return pygame.transform.scale(immagine, dimensione)
    except Exception:
        superficie = pygame.Surface(dimensione, pygame.SRCALPHA)
        superficie.fill(colore_fallback)
        return superficie

# --- GESTIONE AUDIO SICURA ---
audio_funzionante = False
suono_sparo = None

try:
    pygame.mixer.init()
    pygame.mixer.music.load(str(ASSET_DIR / "musica_sottofondo.mp3"))
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)
    
    suono_sparo = pygame.mixer.Sound(str(ASSET_DIR / "suono_sparo.wav"))
    suono_sparo.set_volume(0.4)
    audio_funzionante = True
except Exception:
    print("Avviso: Dispositivo audio non trovato o file audio mancanti. Modalità silenziosa attiva.")

# --- CLASSI (Programmazione a Oggetti) ---

class Giocatore(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = carica_immagine("navicella.png", (50, 40), VERDE)
            
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))
        self.velocita = 8
        self.monete = 0

    def update(self):
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_LEFT] and self.rect.left > 0: 
            self.rect.x -= self.velocita
        if tasti[pygame.K_RIGHT] and self.rect.right < WIDTH: 
            self.rect.x += self.velocita

    def spara(self):
        if self.monete >= 10:
            return [
                Proiettile(self.rect.centerx, self.rect.top, -3),
                Proiettile(self.rect.centerx, self.rect.top, 0),
                Proiettile(self.rect.centerx, self.rect.top, 3)
            ]
        else:
            return [Proiettile(self.rect.centerx, self.rect.top, 0)]

class Proiettile(pygame.sprite.Sprite):
    def __init__(self, x, y, vel_x):
        super().__init__()
        self.image = carica_immagine("proiettile.png", (12, 24), BLU)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.vel_y = -10
        self.vel_x = vel_x

    def update(self):
        self.rect.y += self.vel_y
        self.rect.x += self.vel_x
        if self.rect.bottom < 0 or self.rect.left < 0 or self.rect.right > WIDTH: 
            self.kill()

class Ostacolo(pygame.sprite.Sprite):
    def __init__(self, liv):
        super().__init__()
        self.image = carica_immagine("asteroide.png", (35, 35), ROSSO)
            
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-35), y=-50)
        self.vel = random.randint(6, 10) + liv 

    def update(self):
        self.rect.y += self.vel
        if self.rect.top > HEIGHT: 
            self.kill()

class MeteoriteBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = carica_immagine("meteorite_boss.png", (25, 25), VIOLA)
            
        self.rect = self.image.get_rect(center=(x, y))
        # MODIFICA: Velocità ulteriormente aumentata a 14 per rendere i colpi micidiali
        self.vel_y = 14 

    def update(self):
        self.rect.y += self.vel_y
        if self.rect.top > HEIGHT:
            self.kill()

class Moneta(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = carica_immagine("moneta.png", (25, 25), ORO)
            
        self.rect = self.image.get_rect(x=random.randint(0, WIDTH-25), y=-50)
        self.vel = 4

    def update(self):
        self.rect.y += self.vel
        if self.rect.top > HEIGHT: 
            self.kill()

class BossMatato(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = carica_immagine("boss_matato.png", (150, 100), VIOLA)
            
        self.rect = self.image.get_rect(center=(WIDTH//2, 100))
        self.vita = 50
        self.vel = 5
        self.direzione = 1
        
        # --- VARIABILI PER LA RAFFICA (BURST) ---
        self.timer_attacco = 0       # Tempo tra una raffica e l'altra
        self.colpi_rimanenti = 0     # Quanti colpi deve ancora sparare nella raffica attuale
        self.timer_singolo_colpo = 0 # Tempo millimetrico tra i colpi consecutivi della stessa raffica

    def update(self):
        self.rect.x += self.vel * self.direzione
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direzione *= -1

    def controlla_sparo(self):
        # Avanza il contatore principale per decidere quando avviare una nuova raffica
        self.timer_attacco += 1
        
        # Ogni 80 frame (circa 1.3 secondi), il boss pianifica una nuova raffica da 3 colpi consecutivi
        if self.timer_attacco >= 80 and self.colpi_rimanenti == 0:
            self.timer_attacco = 0
            self.colpi_rimanenti = 3  # Carica la raffica con 3 colpi
            self.timer_singolo_colpo = 0

        # Se ci sono colpi programmati nella raffica attuale
        if self.colpi_rimanenti > 0:
            self.timer_singolo_colpo += 1
            # Spara un colpo ogni 10 frame (frazione di secondo minima per l'effetto consecutività)
            if self.timer_singolo_colpo >= 10:
                self.timer_singolo_colpo = 0
                self.colpi_rimanenti -= 1 # Decrementa i colpi rimasti nella raffica
                return MeteoriteBoss(self.rect.centerx, self.rect.bottom)
                
        return None

# --- SCHERMATA DI INIZIO (MENU PRINCIPALE) ---
def mostra_menu():
    mostra = True
    while mostra:
        screen.fill(NERO)
        aggiorna_e_disegna_neve() 
        
        titolo = font_grande.render("Orbital Cleanup: La Sfida di MATATO", True, ORO)
        screen.blit(titolo, (WIDTH // 2 - titolo.get_width() // 2, 80))
        
        txt_comando1 = font_medio.render("COMANDI DI GIOCO:", True, BLU)
        txt_comando2 = font_piccolo.render("- FRECCIA SINISTRA / DESTRA : Muovi la navicella", True, BIANCO)
        txt_comando3 = font_piccolo.render("- BARRA SPAZIATRICE : Spara ai meteoriti", True, BIANCO)
        
        txt_regola1 = font_medio.render("REGOLE DELL'AVVENTURA:", True, ROSSO)
        txt_regola2 = font_piccolo.render("- Distruggi i meteoriti per fare punti e salire di livello", True, BIANCO)
        txt_regola3 = font_piccolo.render("- Raccogli 10 Monete d'Oro per sbloccare il TRIPLO SPARO", True, VERDE)
        txt_regola4 = font_piccolo.render("- Al Livello 3 affronterai le RAFFICHE del BOSS MATATO!", True, VIOLA)
        
        screen.blit(txt_comando1, (100, 180))
        screen.blit(txt_comando2, (120, 220))
        screen.blit(txt_comando3, (120, 250))
        screen.blit(txt_regola1, (100, 310))
        screen.blit(txt_regola2, (120, 350))
        screen.blit(txt_regola3, (120, 380))
        screen.blit(txt_regola4, (120, 410))
        
        istruzione_avvio = font_grande.render("Clicca X per iniziare l'avventura!", True, VERDE)
        screen.blit(istruzione_avvio, (WIDTH // 2 - istruzione_avvio.get_width() // 2, 490))
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_x:
                    mostra = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                else:
                    pass
                    
        pygame.display.flip()
        clock.tick(60)

# --- FUNZIONE PRINCIPALE (GAME LOOP) ---
def gioco():
    mostra_menu()
    
    nave = Giocatore()
    gruppo_tutti = pygame.sprite.Group(nave)
    gruppo_nemici = pygame.sprite.Group()
    gruppo_monete = pygame.sprite.Group()
    gruppo_proiettili = pygame.sprite.Group()
    gruppo_boss = pygame.sprite.Group()
    gruppo_colpi_boss = pygame.sprite.Group() 

    punteggio = 0
    livello = 1
    boss_attivo = False
    vittoria = False
    game_over = False

    while not game_over and not vittoria:
        screen.fill(NERO)
        aggiorna_e_disegna_neve() 
        
        # --- 1. GESTIONE INPUT ---
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT: 
                pygame.quit()
                sys.exit()
                
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if evento.key == pygame.K_SPACE:
                    if audio_funzionante:
                        try:
                            suono_sparo.play()
                        except Exception:
                            pass
                    
                    nuovi_colpi = nave.spara()
                    for c in nuovi_colpi:
                        gruppo_tutti.add(c)
                        gruppo_proiettili.add(c)

        # --- 2. LOGICA DEI LIVELLI E ATTACCO BOSS ---
        if punteggio > livello * 100 and livello < 3:
            livello += 1
        
        if livello == 3 and punteggio > 350 and not boss_attivo:
            boss_attivo = True
            matato = BossMatato()
            gruppo_boss.add(matato)
            gruppo_tutti.add(matato)

        if not boss_attivo:
            if random.random() < 0.03:
                n = Ostacolo(livello)
                gruppo_nemici.add(n)
                gruppo_tutti.add(n)
            if random.random() < 0.01:
                m = Moneta()
                gruppo_monete.add(m)
                gruppo_tutti.add(m)
        else:
            # Controllo continuo dei colpi a raffica generati dal Boss
            nuovi_colpi_boss = matato.controlla_sparo()
            if nuovi_colpi_boss:
                gruppo_colpi_boss.add(nuovi_colpi_boss)
                gruppo_tutti.add(nuovi_colpi_boss)

        # --- 3. AGGIORNAMENTO POSIZIONI SPRITE ---
        gruppo_tutti.update()

        # --- 4. GESTIONE COLLISIONI ---
        monete_prese = pygame.sprite.spritecollide(nave, gruppo_monete, True)
        for m in monete_prese: 
            nave.monete += 1
            punteggio += 10

        for p in gruppo_proiettili:
            colpiti = pygame.sprite.spritecollide(p, gruppo_nemici, True)
            if colpiti:
                p.kill()
                punteggio += 15
            
            if boss_attivo and pygame.sprite.spritecollide(p, gruppo_boss, False):
                p.kill()
                matato.vita -= 1
                if matato.vita <= 0: 
                    punteggio += 1000
                    vittoria = True

        if pygame.sprite.spritecollide(nave, gruppo_nemici, False) or \
           pygame.sprite.spritecollide(nave, gruppo_boss, False) or \
           pygame.sprite.spritecollide(nave, gruppo_colpi_boss, False):
            game_over = True

        # --- 5. AGGIORNAMENTO GRAFICO SPRITE E INTERFACCIA (UI) ---
        gruppo_tutti.draw(screen)
        
        txt_score = font_piccolo.render(f"Punti: {punteggio} | Monete: {nave.monete}/10 | Livello: {livello if not boss_attivo else 'BOSS'}", True, BIANCO)
        screen.blit(txt_score, (10, 10))
        
        if nave.monete >= 10:
            txt_bonus = font_piccolo.render("TRIPLO SPARO ATTIVO!", True, VERDE)
            screen.blit(txt_bonus, (10, 40))

        if boss_attivo:
            pygame.draw.rect(screen, NERO, (WIDTH//2 - 77, 18, 154, 19))
            pygame.draw.rect(screen, ROSSO, (WIDTH//2 - 75, 20, matato.vita * 3, 15))
            txt_boss = font_piccolo.render("MATATO", True, BIANCO)
            screen.blit(txt_boss, (WIDTH//2 - 40, 40))

        pygame.display.flip()
        clock.tick(60)

    # --- 6. SCHERMATA FINALE ---
    screen.fill(NERO)
    if vittoria:
        testo = "HAI VINTO! MATATO SCONFITTO"
        colore = VERDE
    else:
        testo = "GAME OVER"
        colore = ROSSO
        
    msg = font_grande.render(testo, True, colore)
    msg_punti = font_piccolo.render(f"Punteggio Finale: {punteggio}", True, BIANCO)
    
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 50))
    screen.blit(msg_punti, (WIDTH//2 - msg_punti.get_width()//2, HEIGHT//2 + 20))
    
    pygame.display.flip()
    pygame.time.delay(4000)

gioco()
pygame.quit()
