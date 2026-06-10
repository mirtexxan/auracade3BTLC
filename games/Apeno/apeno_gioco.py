import pygame, random, sys, os, math

pygame.init()
WIDTH, HEIGHT = 1024, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Luna Park Shooting Gallery: Prof. Revenge")
clock = pygame.time.Clock()   

STATO_GIOCO, nome_giocatore, punteggio, prof_eliminati, total_prof = "MENU_INIZIALE", "", 0, 0, 4
camera_x, velocita_camera, LARGHEZZA_PALCO = -200, 8, 1800
vita_giocatore, ultimo_danno_tempo, palline_mostri = 100, pygame.time.get_ticks(), []
frase_sconfitta_scelta = "Niente vacanze estive per te, ci vediamo direttamente al corso di recupero!"

# --- VARIABILI POWER-UP ---
lista_powerup = []           
moltiplicatore_punti = 1      
tempo_fine_moltiplicatore = 0 

# --- VARIABILI MUNIZIONI E RICARICA ---
MUNIZIONI_MAX = 6
munizioni_attuali = 6
sta_ricaricando = False
inizio_ricarica_tempo = 0
tempo_ricarica_totale = 1000  

# --- VARIABILI SISTEMA COMBO ---
combo_attuale = 1
lista_testi_fluttuanti = []  

# --- VARIABILI EFFETTI VISIVI ---
tempo_colpo_mostro = 0  # Gestisce il lampeggio di danno del prof

# --- VARIABILI SCHERMATE DI TRANSIZIONE (4 SECONDI) ---
inizio_transizione_tempo = 0
durata_transizione = 4000  
testo_transizione_titolo = ""
testo_transizione_sub = ""
colore_transizione = (255, 255, 255)

# Rettangolo del pulsante Info nel Menu
rect_pulsante_info = pygame.Rect(WIDTH // 2 - 100, 500, 200, 50)

# --- GENERATORE DI GRAFICA PROCEDURALE (FALLBACK SE MANCANO I FILE) ---
def genera_superficie_prof(tipo, colore_tema, dimensioni):
    """Crea una grafica in stile pixel/cartoon se non ci sono immagini nella cartella"""
    surf = pygame.Surface(dimensioni, pygame.SRCALPHA)
    w, h = dimensioni
    
    # Abito / Corpo
    pygame.draw.ellipse(surf, colore_tema, (10, h - 110, w - 20, 120))
    pygame.draw.ellipse(surf, (30, 30, 30), (w//2 - 25, h - 110, 50, 40)) # Colletto
    
    # Testa (Faccia verde per il boss, pelle normale per i prof)
    colore_pelle = (255, 219, 172) if tipo != "boss" else (150, 220, 150)
    pygame.draw.ellipse(surf, colore_pelle, (20, 40, w - 40, 110))
    
    # Personalizzazione dettagli facciali
    if tipo == "mostro1":  # Trioschi (Italiano - Barba e capelli da saggio)
        pygame.draw.arc(surf, (110, 110, 110), (15, 30, w - 30, 70), 0, math.pi, 12)
        pygame.draw.ellipse(surf, (110, 110, 110), (w//2 - 30, 125, 60, 25)) # Barba
        pygame.draw.circle(surf, (0, 0, 0), (w//2 - 25, 85), 5)
        pygame.draw.circle(surf, (0, 0, 0), (w//2 + 25, 85), 5)
    elif tipo == "mostro2":  # Cascone (Matematica - Occhiali quadrati da nerd)
        pygame.draw.rect(surf, (0, 0, 0), (w//2 - 40, 75, 30, 22), 3)
        pygame.draw.rect(surf, (0, 0, 0), (w//2 + 10, 75, 30, 22), 3)
        pygame.draw.line(surf, (0, 0, 0), (w//2 - 10, 85), (w//2 + 10, 85), 3)
        pygame.draw.circle(surf, (0, 0, 0), (w//2 - 25, 86), 3)
        pygame.draw.circle(surf, (0, 0, 0), (w//2 + 25, 86), 3)
    elif tipo == "mostro3":  # Fabretto (Sistemi - Visore Cyber-Punk)
        pygame.draw.rect(surf, (40, 40, 40), (22, 70, w - 44, 28), 0, 4)
        pygame.draw.rect(surf, (0, 255, 0), (28, 74, w - 56, 20), 0, 2) # Schermo visore
    elif tipo == "mostro4":  # Cavallo (Telecomunicazioni - Capelli elettrici viola)
        for _ in range(12):
            pygame.draw.circle(surf, (180, 60, 240), (random.randint(25, w-25), random.randint(20, 45)), 10)
        pygame.draw.circle(surf, (255, 0, 0), (w//2 - 25, 85), 8)
        pygame.draw.circle(surf, (255, 0, 0), (w//2 + 25, 85), 8)
    elif tipo == "boss":  # Mirto Musci (Informatica - Il Re dei Bug)
        punti_corona = [(20, 40), (45, 15), (w//2, 35), (w - 45, 15), (w - 20, 40)]
        pygame.draw.polygon(surf, (255, 215, 0), punti_corona) # Corona d'oro
        pygame.draw.ellipse(surf, (15, 15, 15), (w//2 - 50, 85, 40, 20)) # Occhiali Matrix
        pygame.draw.ellipse(surf, (15, 15, 15), (w//2 + 10, 85, 40, 20))
        pygame.draw.arc(surf, (180, 20, 20), (w//2 - 35, 125, 70, 30), math.pi, 2*math.pi, 3) # Sorrisetto

    if tipo != "boss": # Bocca standard imbronciata
        pygame.draw.line(surf, (0, 0, 0), (w//2 - 15, 130), (w//2 + 15, 130), 3)
    return surf

def genera_superficie_arma():
    surf = pygame.Surface((250, 250), pygame.SRCALPHA)
    pygame.draw.rect(surf, (70, 80, 95), (90, 70, 45, 130), 0, 6) # Impugnatura
    pygame.draw.rect(surf, (130, 140, 155), (50, 50, 120, 45), 0, 4) # Canna
    pygame.draw.circle(surf, (0, 255, 255), (50, 72), 6) # Laser frontale
    return surf

def genera_superficie_bonus(tipo):
    surf = pygame.Surface((50, 50), pygame.SRCALPHA)
    if tipo == "libro":
        pygame.draw.rect(surf, (200, 40, 40), (10, 5, 30, 40), 0, 4)
        pygame.draw.rect(surf, (245, 245, 245), (14, 8, 22, 34))
    elif tipo == "gemini":
        punti = [(25, 5), (32, 18), (45, 25), (32, 32), (25, 45), (18, 32), (5, 25), (18, 18)]
        pygame.draw.polygon(surf, (0, 255, 255), punti)
    return surf

# Elenco dei professori con le materie e le battute specifiche richieste!
dati_professori = [
    {
        "file": "mostro1", "nome": "TRIOSCHI", "materia": "ITALIANO", 
        "sub": '"Lasciate ogne speranza, voi ch\'intrate... Ti interrogo sui canti della Divina Commedia!"', 
        "colore": (230, 90, 90), "vita": 5, "max_vita": 5
    },
    {
        "file": "mostro2", "nome": "CASCONE", "materia": "MATEMATICA", 
        "sub": '"I tuoi voti tendono a zero! Risolvi questa equazione prima che io azzeri la tua salute!"', 
        "colore": (0, 200, 255), "vita": 5, "max_vita": 5
    },
    {
        "file": "mostro3", "nome": "FABRETTO", "materia": "SISTEMI E RETI", 
        "sub": '"Rete instabile! Hai sbagliato a configurare i router su Cisco Packet Tracer. Anno resettato!"', 
        "colore": (50, 220, 50), "vita": 5, "max_vita": 5
    },
    {
        "file": "mostro4", "nome": "CAVALLO", "materia": "TELECOMUNICAZIONI", 
        "sub": '"La mia tensione è altissima. Vediamo se ti ricordi le leggi di Ohm prima che ti fulmini!"', 
        "colore": (190, 60, 255), "vita": 5, "max_vita": 5
    }
]

dati_boss = {
    "file": "boss", "nome": "MIRTO MUSCI", "materia": "INFORMATICA", 
    "sub": '"SyntaxError: Invalid Student. Il tuo codice Python ha troppi bug e non compila. BOCCIATO!"', 
    "colore": (255, 30, 30), "vita": 10, "max_vita": 10
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def carica_immagine(nome_base, nome_alternativo, dimensioni, tipo_disegno=None, colore_fallback=(200,200,200)):
    nome_pulito = nome_base.replace(".png", "").replace(".jpg", "").replace(".jpeg", "").replace(",png", "").strip()
    nome_alt_pulito = nome_alternativo.replace(".png", "").replace(".jpg", "").strip()
    basi_da_tentare = [nome_pulito.lower(), nome_pulito.upper(), nome_pulito.capitalize(), nome_alt_pulito.lower(), nome_alt_pulito.upper(), nome_alt_pulito.capitalize()]
    num = "".join(filter(str.isdigit, nome_pulito))
    if num: basi_da_tentare.extend([f"mostro {num}", f"Mostro {num}", f"MOSTRO {num}", f"mostro_{num}", f"Mostro_{num}", f"MOSTRO_{num}"])
    basi_da_tentare = list(dict.fromkeys(basi_da_tentare))
    estensioni = [".png", ".PNG", ".png.png", ".PNG.PNG", " .png", " .PNG", ".jpg", ".JPG", ".jpeg", ".JPEG", ",png", ",PNG"]
    
    for b in basi_da_tentare:
        for est in estensioni:
            percorso_completo = os.path.join(BASE_DIR, b + est)
            if os.path.exists(percorso_completo):
                try: return pygame.transform.scale(pygame.image.load(percorso_completo).convert_alpha(), dimensioni)
                except: pass
    try:
        if os.path.exists(BASE_DIR):
            for file_presente in os.listdir(BASE_DIR):
                fp_lower = file_presente.lower()
                target_mostro = f"mostro{num}" if num else "---"
                if (nome_alt_pulito.lower() in fp_lower) or (target_mostro in fp_lower.replace("_", "").replace(" ", "")):
                    if any(fp_lower.endswith(e) for e in [".png", ".jpg", ".jpeg", ".bmp", ".webp"]):
                        percorso_completo = os.path.join(BASE_DIR, file_presente)
                        try: return pygame.transform.scale(pygame.image.load(percorso_completo).convert_alpha(), dimensioni)
                        except: pass
    except: pass
    
    # Se l'immagine non esiste, usiamo il generatore procedurale per non lasciare lo schermo vuoto
    if tipo_disegno:
        return genera_superficie_prof(tipo_disegno, colore_fallback, dimensioni)
    elif nome_base == "pistola":
        return genera_superficie_arma()
    elif nome_base in ["libro", "gemini"]:
        return genera_superficie_bonus(nome_base)
    return None

# Caricamento asset (Con disegno procedurale incorporato come piano B se mancano i file)
for p in dati_professori: p["immagine"] = carica_immagine(p["file"], p["nome"], (160, 240), p["file"], p["colore"])
img_boss = carica_immagine(dati_boss["file"], dati_boss["nome"], (240, 310), "boss", dati_boss["colore"])
img_pistola = carica_immagine("pistola", "pistola", (250, 250))
img_bonus_libro = carica_immagine("libro", "libro", (40, 45))
img_bonus_gemini = carica_immagine("gemini", "gemini", (40, 40))
img_guida_libro = carica_immagine("libro", "libro", (60, 65))
img_guida_gemini = carica_immagine("gemini", "gemini", (60, 60))

passo_pos = LARGHEZZA_PALCO // (total_prof + 1)
for i, prof in enumerate(dati_professori):
    prof.update({"x": passo_pos * (i + 1) + random.randint(-50, 50), "y": 190, "direzione": random.choice([-1, 1]), "velocita_base": random.uniform(2.2, 3.5)})

boss_x, boss_y, velocita_boss_base, direzione_boss, indice_corrente = LARGHEZZA_PALCO // 2 - 120, 120, 4.5, 1, 0

font_titolo, font_big_gameover = pygame.font.SysFont("Impact", 42), pygame.font.SysFont("Impact", 95)
font_sub, font_testo, font_hud = pygame.font.SysFont("Impact", 26), pygame.font.SysFont("Impact", 24), pygame.font.SysFont("Courier New", 20, bold=True)
font_punti_fluttuanti = pygame.font.SysFont("Impact", 28)
font_transizione_titolo = pygame.font.SysFont("Impact", 44) 

luci_luna_park = [{"x": x, "colore_idx": random.randint(0, 3)} for x in range(0, LARGHEZZA_PALCO, 40)]
stelle_sfondo = [{"x": random.randint(0, LARGHEZZA_PALCO), "y": random.randint(10, 150)} for _ in range(70)]
particelle_sfondo = [{"x": random.randint(0, LARGHEZZA_PALCO), "y": random.randint(60, 390), "colore": (random.randint(100, 255), random.randint(100, 255), random.randint(0, 255)), "raggio": random.randint(2, 5), "velocita_y": random.uniform(0.4, 1.3)} for _ in range(60)]

def attiva_transizione(prof_dict, numero_livello, e_boss=False):
    global STATO_GIOCO, inizio_transizione_tempo, testo_transizione_titolo, testo_transizione_sub, colore_transizione, palline_mostri
    STATO_GIOCO = "TRANSIZIONE"
    inizio_transizione_tempo = pygame.time.get_ticks()
    palline_mostri.clear() 
    colore_transizione = prof_dict["colore"]
    testo_transizione_sub = prof_dict["sub"]
    if e_boss:
        testo_transizione_titolo = f"⚠️ SCONTRO FINALE: {prof_dict['nome']} ({prof_dict['materia']}) ⚠️"
    else:
        testo_transizione_titolo = f"--- LIVELLO {numero_livello}: {prof_dict['nome']} ({prof_dict['materia']}) ---"

running = True
while running:
    tempo_attuale = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        elif STATO_GIOCO == "MENU_INIZIALE":
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    nome_giocatore = "CARLEZT" if not nome_giocatore.strip() else nome_giocatore
                    pygame.mouse.set_visible(False)
                    combo_attuale = 1
                    attiva_transizione(dati_professori[0], 1)
                elif event.key == pygame.K_BACKSPACE: nome_giocatore = nome_giocatore[:-1]
                elif len(nome_giocatore) < 14 and (event.unicode.isalnum() or event.unicode == ' '): nome_giocatore += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if rect_pulsante_info.collidepoint(mx, my): STATO_GIOCO = "MENU_INFO" 
                    
        elif STATO_GIOCO == "MENU_INFO" and event.type == pygame.MOUSEBUTTONDOWN:
            STATO_GIOCO = "MENU_INIZIALE" 

        elif event.type == pygame.KEYDOWN and STATO_GIOCO in ["PROFESSORI", "BOSS"]:
            if event.key == pygame.K_r and not sta_ricaricando and munizioni_attuali < MUNIZIONI_MAX:
                sta_ricaricando = True
                inizio_ricarica_tempo = tempo_attuale

        elif event.type == pygame.MOUSEBUTTONDOWN and vita_giocatore > 0 and STATO_GIOCO in ["PROFESSORI", "BOSS"]:
            if sta_ricaricando or munizioni_attuali <= 0: continue
            mx, my = pygame.mouse.get_pos()
            rx = mx - camera_x
            munizioni_attuali -= 1
            
            ha_cliccato_powerup = False
            for pu in lista_powerup[:]:
                hitbox_pu = pygame.Rect(pu["x"] - 25, pu["y"] - 25, 50, 50)
                if hitbox_pu.collidepoint(rx, my):
                    if pu["tipo"] == "libro": vita_giocatore = min(100, vita_giocatore + 20)  
                    elif pu["tipo"] == "gemini": moltiplicatore_punti = 2; tempo_fine_moltiplicatore = tempo_attuale + 5000  
                    lista_powerup.remove(pu)
                    ha_cliccato_powerup = True
                    break 
            if ha_cliccato_powerup: continue

            ha_colpito_mostro = False

            if STATO_GIOCO == "PROFESSORI" and indice_corrente < len(dati_professori):
                if pygame.Rect(dati_professori[indice_corrente]["x"], dati_professori[indice_corrente]["y"], 160, 240).collidepoint(rx, my):
                    ha_colpito_mostro = True
                    tempo_colpo_mostro = tempo_attuale # Attiva lampeggio rosso danno
                    punti_guadagnati = 50 * combo_attuale * moltiplicatore_punti
                    punteggio += punti_guadagnati
                    lista_testi_fluttuanti.append({"testo": f"+{punti_guadagnati}!", "x": mx, "y": my, "alfa": 255, "colore": (255, 215, 0) if combo_attuale > 1 else (255, 255, 255)})
                    dati_professori[indice_corrente]["vita"] -= 1
                    
                    if random.random() < 0.35: 
                        lista_powerup.append({"x": dati_professori[indice_corrente]["x"] + 60, "x_originale": dati_professori[indice_corrente]["x"] + 60, "y": 20, "tipo": random.choice(["libro", "gemini"]), "velocita_y": random.uniform(1.2, 2.0)})

                    if dati_professori[indice_corrente]["vita"] <= 0:
                        punti_morte = 200 * combo_attuale * moltiplicatore_punti
                        punteggio += punti_morte
                        prof_eliminati += 1
                        
                        if prof_eliminati >= total_prof:
                            attiva_transizione(dati_boss, 5, e_boss=True)
                        else:
                            indice_corrente = prof_eliminati
                            attiva_transizione(dati_professori[indice_corrente], indice_corrente + 1)
            
            elif STATO_GIOCO == "BOSS" and pygame.Rect(boss_x, boss_y, 240, 310).collidepoint(rx, my):
                ha_colpito_mostro = True
                tempo_colpo_mostro = tempo_attuale # Attiva lampeggio rosso danno
                punti_guadagnati = 100 * combo_attuale * moltiplicatore_punti
                punteggio += punti_guadagnati
                lista_testi_fluttuanti.append({"testo": f"+{punti_guadagnati}!!", "x": mx, "y": my, "alfa": 255, "colore": (255, 69, 0)})
                dati_boss["vita"] -= 1
                
                if random.random() < 0.45:
                    lista_powerup.append({"x": boss_x + 100, "x_originale": boss_x + 100, "y": 20, "tipo": random.choice(["libro", "gemini"]), "velocita_y": random.uniform(1.4, 2.2)})

                if dati_boss["vita"] <= 0: 
                    STATO_GIOCO = "VITTORIA"
                    pygame.mouse.set_visible(True)

            if ha_colpito_mostro: combo_attuale += 1  
            else: combo_attuale = 1   

    # --- LOGICA DI TRANSIZIONE ---
    if STATO_GIOCO == "TRANSIZIONE":
        if tempo_attuale - inizio_transizione_tempo >= durata_transizione:
            if prof_eliminati >= total_prof: STATO_GIOCO = "BOSS"
            else: STATO_GIOCO = "PROFESSORI"
            ultimo_danno_tempo = tempo_attuale

    if vita_giocatore > 0 and STATO_GIOCO in ["PROFESSORI", "BOSS"]:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: camera_x = min(0, camera_x + velocita_camera)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: camera_x = max(-(LARGHEZZA_PALCO - WIDTH), camera_x - velocita_camera)

        if sta_ricaricando:
            if tempo_attuale - inizio_ricarica_tempo >= tempo_ricarica_totale:
                munizioni_attuali = MUNIZIONI_MAX
                sta_ricaricando = False

        if moltiplicatore_punti == 2 and tempo_attuale > tempo_fine_moltiplicatore: moltiplicatore_punti = 1

        for pu in lista_powerup[:]:
            pu["y"] += pu["velocita_y"]
            # Movimento oscillatorio a onda sinusoidale per i power-up
            pu["x"] = pu["x_originale"] + math.sin(tempo_attuale * 0.005) * 40
            if pu["y"] > 430: pu["y"] = 430
            if pu["y"] > HEIGHT: lista_powerup.remove(pu)

        for tf in lista_testi_fluttuanti[:]:
            tf["y"] -= 1.5; tf["alfa"] -= 5
            if tf["alfa"] <= 0: lista_testi_fluttuanti.remove(tf)

        if STATO_GIOCO == "PROFESSORI" and indice_corrente < len(dati_professori):
            p = dati_professori[indice_corrente]
            p["x"] += p["velocita_base"] * (1.0 + prof_eliminati * 0.35) * p["direzione"]
            if p["x"] < 100 or p["x"] > LARGHEZZA_PALCO - 250:
                p["direzione"] *= -1; p["x"] = max(100, min(p["x"], LARGHEZZA_PALCO - 250))
            if tempo_attuale - ultimo_danno_tempo > 2400:
                palline_mostri.append({"x": p["x"] + 80, "y": p["y"] + 100, "target_x": WIDTH // 2 - camera_x, "target_y": HEIGHT - 150, "progress": 0.0})
                ultimo_danno_tempo = tempo_attuale
        elif STATO_GIOCO == "BOSS":
            boss_x += velocita_boss_base * (1.0 + total_prof * 0.30) * direzione_boss
            if boss_x < 150 or boss_x > LARGHEZZA_PALCO - 350:
                direzione_boss *= -1; boss_x = max(150, min(boss_x, LARGHEZZA_PALCO - 350))
            if tempo_attuale - ultimo_danno_tempo > 2000:
                palline_mostri.append({"x": boss_x + 120, "y": boss_y + 150, "target_x": WIDTH // 2 - camera_x, "target_y": HEIGHT - 150, "progress": 0.0})
                ultimo_danno_tempo = tempo_attuale

        for pallina in palline_mostri[:]:
            pallina["progress"] += 0.04
            if pallina["progress"] >= 1.0:
                vita_giocatore = max(0, vita_giocatore - 15)
                combo_attuale = 1  
                if vita_giocatore <= 0: 
                    STATO_GIOCO = "GAMEOVER"
                    pygame.mouse.set_visible(True)
                palline_mostri.remove(pallina)

    for p in particelle_sfondo:
        p["y"] += p["velocita_y"]
        if p["y"] > 390: p["y"], p["x"] = 60, random.randint(0, LARGHEZZA_PALCO)

    # --- RENDERING ---
    screen.fill((15, 10, 25))
    
    if STATO_GIOCO == "MENU_INIZIALE":
        for i in range(0, WIDTH, 80): pygame.draw.polygon(screen, (160, 25, 25) if i % 160 == 0 else (230, 190, 50), [(i, 0), (i+40, 90), (i+80, 0)])
        for t, f, c, y in [
            ("TIRO AL BERSAGLIO: LUNA PARK SPECIALE!", font_titolo, (255, 240, 60), 200), 
            ("Sconfiggi i Prof-Mostri e abbatti il Boss Mirto Musci!", font_sub, (255, 255, 255), 270), 
            ("INSERISCI IL TUO NOME E PREMI INVIO PER GIOCARE:", font_testo, (220, 220, 220), 340), 
            (nome_giocatore if nome_giocatore else "Digita il tuo nome...", font_sub, (80, 255, 80) if nome_giocatore else (120, 120, 120), 392), 
            ("Usa i tasti A / D o FRECCE per muoverti - Click del mouse per sparare", font_testo, (160, 160, 180), 640)
        ]:
            img = f.render(t, True, c); screen.blit(img, (WIDTH//2 - img.get_width()//2, y))
        pygame.draw.rect(screen, (230, 190, 50), (WIDTH//2 - 250, 380, 500, 60), 3, 10)
        
        pygame.draw.rect(screen, (40, 140, 220), rect_pulsante_info, 0, 8)
        pygame.draw.rect(screen, (255, 255, 255), rect_pulsante_info, 2, 8)
        txt_info = font_testo.render("GUIDA BONUS", True, (255, 255, 255))
        screen.blit(txt_info, (rect_pulsante_info.centerx - txt_info.get_width()//2, rect_pulsante_info.centery - txt_info.get_height()//2))

    elif STATO_GIOCO == "MENU_INFO":
        for i in range(0, WIDTH, 80): pygame.draw.polygon(screen, (40, 60, 120) if i % 160 == 0 else (20, 30, 70), [(i, 0), (i+40, 60), (i+80, 0)])
        titolo_info = font_titolo.render("GUIDA AI BONUS DEL LUNA PARK", True, (0, 255, 255))
        screen.blit(titolo_info, (WIDTH//2 - titolo_info.get_width()//2, 100))
        
        if img_guida_libro: screen.blit(img_guida_libro, (WIDTH//2 - 200, 220))
        txt_lib_t = font_sub.render("IL LIBRO DI RECUPERO", True, (255, 255, 255))
        txt_lib_d = font_testo.render("Prendilo al volo per studiare e recuperare il 20% della VITA!", True, (200, 200, 200))
        screen.blit(txt_lib_t, (WIDTH//2 - 130, 225)); screen.blit(txt_lib_d, (WIDTH//2 - 130, 255))
        
        if img_guida_gemini: screen.blit(img_guida_gemini, (WIDTH//2 - 200, 370))
        txt_gem_t = font_sub.render("LOGO GEMINI", True, (255, 255, 255))
        txt_gem_d = font_testo.render("Attiva la FRENESIA AI! Raddoppia tutti i punti (2X) per 5 secondi!", True, (200, 200, 200))
        screen.blit(txt_gem_t, (WIDTH//2 - 130, 370)); screen.blit(txt_gem_d, (WIDTH//2 - 130, 400))
        
        txt_nota = font_testo.render("I bonus piovono dall'alto del cielo! Acchiappali prima che tocchino il tavolo.", True, (255, 240, 100))
        txt_back = font_sub.render("[ CLICCA IN QUALSIASI PUNTO PER TORNARE INDIETRO ]", True, (50, 255, 50))
        screen.blit(txt_nota, (WIDTH//2 - txt_nota.get_width()//2, 530))
        screen.blit(txt_back, (WIDTH//2 - txt_back.get_width()//2, 630))

    else:
        for s in stelle_sfondo: pygame.draw.circle(screen, (255, 255, 220), (s["x"] + camera_x, s["y"]), random.randint(1, 3))
        angolo_faro = math.sin(tempo_attuale * 0.0015) * 50
        for fx, col in [(100, (30, 40, 70)), (600, (50, 30, 60)), (1100, (30, 50, 60)), (1600, (60, 40, 40))]:
            pygame.draw.polygon(screen, col, [(fx+camera_x, 410), (int(fx+150+angolo_faro*2+camera_x), 0), (int(fx+250+angolo_faro*2+camera_x), 0)])
        for i in range(0, LARGHEZZA_PALCO, 160): pygame.draw.rect(screen, (140, 25, 35), (i + camera_x, 0, 80, HEIGHT - 320))
        for i in range(0, LARGHEZZA_PALCO, 40): pygame.draw.polygon(screen, (240, 180, 40) if i % 80 == 0 else (40, 180, 220) if i % 120 == 0 else (200, 50, 200), [(i + camera_x, 0), (i + 20 + camera_x, 35), (i + 40 + camera_x, 0)])
        for p in particelle_sfondo: pygame.draw.circle(screen, p["colore"], (int(p["x"] + camera_x), int(p["y"])), p["raggio"])
        pygame.draw.line(screen, (20, 20, 20), (camera_x, 50), (LARGHEZZA_PALCO + camera_x, 50), 3)
        for luce in luci_luna_park:
            if random.random() < 0.05: luce["colore_idx"] = (luce["colore_idx"] + 1) % 4
            pygame.draw.circle(screen, [(255, 50, 50), (50, 255, 50), (50, 150, 255), (255, 255, 50)][luce["colore_idx"]], (luce["x"] + camera_x, 53), 8)
        pygame.draw.rect(screen, (75, 35, 15), (0, 430, LARGHEZZA_PALCO, 240))
        pygame.draw.rect(screen, (100, 50, 20), (0, 410, LARGHEZZA_PALCO, 20))
        pygame.draw.rect(screen, (50, 20, 5), (0, 430, LARGHEZZA_PALCO, 10))

        if STATO_GIOCO in ["PROFESSORI", "BOSS"]:
            if STATO_GIOCO == "PROFESSORI" and indice_corrente < len(dati_professori):
                p = dati_professori[indice_corrente]; sx = p["x"] + camera_x
                if p["immagine"]: 
                    screen.blit(p["immagine"], (sx, p["y"]))
                    # Flash rosso se colpito di recente (entro 150ms)
                    if tempo_attuale - tempo_colpo_mostro < 150:
                        f_surf = pygame.Surface((160, 240), pygame.SRCALPHA)
                        f_surf.fill((255, 0, 0, 140))
                        screen.blit(f_surf, (sx, p["y"]), special_flags=pygame.BLEND_RGBA_MULT)
                txt = font_testo.render(p["nome"], True, (255, 255, 255)); tx = sx + 80 - txt.get_width()//2
                pygame.draw.rect(screen, (15, 15, 15), (tx - 10, p["y"] - 45, txt.get_width() + 20, 32), 0, 4)
                pygame.draw.rect(screen, (230, 190, 50), (tx - 10, p["y"] - 45, txt.get_width() + 20, 32), 2, 4)
                screen.blit(txt, (tx, p["y"] - 41))
                for v in range(p["max_vita"]): pygame.draw.circle(screen, (0, 255, 60) if v < p["vita"] else (50, 50, 50), (sx + 40 + (v * 20), p["y"] - 8), 6)
            elif STATO_GIOCO == "BOSS":
                sbx = boss_x + camera_x
                if img_boss: 
                    screen.blit(img_boss, (sbx, boss_y))
                    if tempo_attuale - tempo_colpo_mostro < 150:
                        f_surf = pygame.Surface((240, 310), pygame.SRCALPHA)
                        f_surf.fill((255, 0, 0, 140))
                        screen.blit(f_surf, (sbx, boss_y), special_flags=pygame.BLEND_RGBA_MULT)
                txt = font_testo.render(dati_boss["nome"], True, (255, 50, 50)); tbx = sbx + 120 - txt.get_width()//2
                pygame.draw.rect(screen, (15, 15, 15), (tbx - 10, boss_y - 45, txt.get_width() + 20, 32), 0, 4)
                pygame.draw.rect(screen, (255, 0, 0), (tbx - 10, boss_y - 45, txt.get_width() + 20, 32), 2, 4)
                screen.blit(txt, (tbx, boss_y - 41))
                for v in range(dati_boss["max_vita"]): pygame.draw.circle(screen, (255, 230, 0) if v < dati_boss["vita"] else (50, 50, 50), (sbx + 30 + (v * 20), boss_y - 8), 6)

        for pu in lista_powerup:
            pos_render_x = int(pu["x"] + camera_x); pos_render_y = int(pu["y"])
            if pu["tipo"] == "libro" and img_bonus_libro:
                screen.blit(img_bonus_libro, (pos_render_x - 20, pos_render_y - 22))
            elif pu["tipo"] == "gemini" and img_bonus_gemini:
                screen.blit(img_bonus_gemini, (pos_render_x - 20, pos_render_y - 20))

        for pallina in palline_mostri:
            cx = pallina["x"] + (pallina["target_x"] - pallina["x"]) * pallina["progress"] + camera_x
            cy = pallina["y"] + (pallina["target_y"] - pallina["y"]) * pallina["progress"]
            dr = int(6 + (24 * pallina["progress"]))
            pygame.draw.circle(screen, (255, 0, 0), (int(cx), int(cy)), dr)
            pygame.draw.circle(screen, (255, 150, 150), (int(cx - dr//3), int(cy - dr//3)), dr//3)

        if tempo_attuale - ultimo_danno_tempo < 120 and STATO_GIOCO not in ["GAMEOVER", "VITTORIA", "TRANSIZIONE"]:
            flash = pygame.Surface((WIDTH, HEIGHT)); flash.fill((240, 0, 0)); flash.set_alpha(100); screen.blit(flash, (0, 0))

        # Pulsazione di allerta schermo quando la vita è critica (< 30%)
        if vita_giocatore <= 30 and STATO_GIOCO in ["PROFESSORI", "BOSS"]:
            allerta_alfa = int(abs(math.sin(tempo_attuale * 0.005)) * 40) + 15
            flash_allerta = pygame.Surface((WIDTH, HEIGHT)); flash_allerta.fill((200, 0, 0))
            flash_allerta.set_alpha(allerta_alfa); screen.blit(flash_allerta, (0, 0))

        if STATO_GIOCO == "PROFESSORI" or STATO_GIOCO == "BOSS":
            if sta_ricaricando:
                txt_warn = font_sub.render("RICARICA IN CORSO...", True, (255, 140, 0))
                screen.blit(txt_warn, (WIDTH // 2 - txt_warn.get_width() // 2, HEIGHT - 270))
            elif munizioni_attuali == 0:
                txt_warn = font_sub.render("CARICATORE VUOTO! PREMI 'R' PER RICARICARE!", True, (255, 50, 50))
                screen.blit(txt_warn, (WIDTH // 2 - txt_warn.get_width() // 2, HEIGHT - 270))

        for tf in lista_testi_fluttuanti:
            img_testo_punti = font_punti_fluttuanti.render(tf["testo"], True, tf["colore"])
            img_testo_punti.set_alpha(tf["alfa"])
            screen.blit(img_testo_punti, (tf["x"] - img_testo_punti.get_width() // 2, tf["y"]))

        pos_m = pygame.mouse.get_pos()
        osc = math.sin(tempo_attuale * 0.003) * 4
        if STATO_GIOCO not in ["GAMEOVER", "VITTORIA", "TRANSIZIONE"]:
            offset_y = 180 if sta_ricaricando else 0
            if img_pistola: screen.blit(img_pistola, (pos_m[0] - 125, HEIGHT - 230 + int(osc) + offset_y))

        # --- INTERFACCIA UTENTE (HUD) ---
        for hx, txts in [(30, [f"GIOCATORE: {nome_giocatore.upper()}", f"PUNTI: {punteggio}", f"ELIMINATI: {prof_eliminati}/{total_prof}"]), (630, [f"VITA: {vita_giocatore}%", "VITA BOSS FINALE", "BARRA"])]:
            pygame.draw.rect(screen, (10, 15, 12), (hx, 650, 360, 95), 0, 6)
            pygame.draw.rect(screen, (100, 120, 105), (hx, 650, 360, 95), 3, 6)
            for idx, text in enumerate(txts):
                if text == "BARRA":
                    pygame.draw.rect(screen, (50, 20, 20), (hx + 20, 720, 320, 12))
                    if STATO_GIOCO == "BOSS" and dati_boss["vita"] > 0: pygame.draw.rect(screen, (255, 30, 30), (hx + 20, 720, int((320 * dati_boss["vita"]) / dati_boss["max_vita"]), 12))
                else: screen.blit(font_hud.render(text, True, (255, 40, 40) if "VITA:" in text and vita_giocatore <= 35 else (0, 255, 255) if "GIOCATORE" in text else (255, 255, 255) if "BOSS" in text else (255, 255, 0)), (hx + 20, 662 + idx * 25))

        if STATO_GIOCO in ["PROFESSORI", "BOSS"]:
            colore_munizioni = (255, 50, 50) if munizioni_attuali <= 1 else (255, 215, 0) if munizioni_attuali <= 3 else (255, 255, 255)
            testo_munizioni = font_sub.render(f"MUNIZIONI: {munizioni_attuali} / {MUNIZIONI_MAX}", True, colore_munizioni)
            screen.blit(testo_munizioni, (30, 612))
            if combo_attuale > 1:
                colore_combo = (50, 255, 50) if combo_attuale < 4 else (255, 255, 0) if combo_attuale < 7 else (255, 50, 50)
                testo_combo = font_sub.render(f"COMBO: x{combo_attuale - 1}", True, colore_combo)
                screen.blit(testo_combo, (250, 612))

        if moltiplicatore_punti == 2:
            txt_bonus = font_sub.render("FRENESIA DOPPI PUNTI (2X) ATTIVATA!", True, (255, 215, 0))
            screen.blit(txt_bonus, (WIDTH // 2 - txt_bonus.get_width() // 2, 612))

        # --- SCHERMATE DI TRANSIZIONE ---
        if STATO_GIOCO == "TRANSIZIONE":
            osc_transizione = pygame.Surface((WIDTH, HEIGHT))
            osc_transizione.fill((8, 8, 20))
            osc_transizione.set_alpha(225)
            screen.blit(osc_transizione, (0, 0))
            
            onda_pulsante = int(math.sin(tempo_attuale * 0.007) * 35) + 220
            colore_pulsante = (max(0, colore_transizione[0] - (255 - onda_pulsante)), max(0, colore_transizione[1] - (255 - onda_pulsante)), max(0, colore_transizione[2] - (255 - onda_pulsante)))

            img_titolo = font_transizione_titolo.render(testo_transizione_titolo, True, colore_pulsante)
            img_sub = font_sub.render(testo_transizione_sub, True, (255, 240, 90))
            tempo_rimasto = max(1, 4 - (tempo_attuale - inizio_transizione_tempo) // 1000)
            img_pronto = font_testo.render(f"PRONTI AL FUOCO IN {tempo_rimasto}...", True, (140, 140, 140))
            
            screen.blit(img_titolo, (WIDTH // 2 - img_titolo.get_width() // 2, HEIGHT // 2 - 80))
            screen.blit(img_sub, (WIDTH // 2 - img_sub.get_width() // 2, HEIGHT // 2 + 15))
            screen.blit(img_pronto, (WIDTH // 2 - img_pronto.get_width() // 2, HEIGHT // 2 + 110))

        if STATO_GIOCO in ["GAMEOVER", "VITTORIA"]:
            osc_s = pygame.Surface((WIDTH, HEIGHT)); osc_s.fill((15, 5, 5) if STATO_GIOCO == "GAMEOVER" else (5, 25, 5)); osc_s.set_alpha(225); screen.blit(osc_s, (0, 0))
            pygame.draw.rect(screen, (25, 15, 20) if STATO_GIOCO == "GAMEOVER" else (15, 25, 15), (60, 160, 904, 390), 0, 20)
            pygame.draw.rect(screen, ((255, 0, 0) if STATO_GIOCO == "GAMEOVER" else (0, 255, 0)) if (tempo_attuale // 250) % 2 == 0 else ((100, 0, 0) if STATO_GIOCO == "GAMEOVER" else (0, 100, 0)), (60, 160, 904, 390), 6, 20)
            
            if STATO_GIOCO == "GAMEOVER":
                for t, f, c, y in [("Game Over !!", font_big_gameover, (255, 0, 0), 210), (frase_sconfitta_scelta, font_sub, (255, 230, 50), 335), (f"Punteggio finale di {nome_giocatore}: {punteggio} Punti.", font_testo, (255, 255, 255), 425)]:
                    img = f.render(t, True, c); screen.blit(img, (WIDTH//2 - img.get_width()//2, y))
            else:
                for t, f, c, y in [("Hai vinto ! professori mandati in pensione .", font_sub, (0, 255, 0), 195), ("Hai distrutto il consiglio di classe,", font_titolo, (255, 255, 50), 260), ("goditi le vacanze estive !!", font_titolo, (255, 255, 50), 320), (f"Punteggio Record per {nome_giocatore}: {punteggio} Punti!", font_testo, (255, 255, 255), 430)]:
                    img = f.render(t, True, c); screen.blit(img, (WIDTH//2 - img.get_width()//2, y))

        if STATO_GIOCO not in ["GAMEOVER", "VITTORIA", "TRANSIZIONE"]:
            pygame.draw.circle(screen, (255, 40, 40), pos_m, 24, 3); pygame.draw.circle(screen, (255, 40, 40), pos_m, 3, 0)
            for l in [((pos_m[0] - 32, pos_m[1]), (pos_m[0] - 10, pos_m[1])), ((pos_m[0] + 10, pos_m[1]), (pos_m[0] + 32, pos_m[1])), ((pos_m[0], pos_m[1] - 32), (pos_m[0], pos_m[1] - 10)), ((pos_m[0], pos_m[1] + 10), (pos_m[0], pos_m[1] + 32))]: pygame.draw.line(screen, (255, 40, 40), l[0], l[1], 3)

    pygame.display.flip()
    clock.tick(60)

pygame.quit(); sys.exit()
