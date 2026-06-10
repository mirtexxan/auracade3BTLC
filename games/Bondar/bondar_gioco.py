import pygame  # importiamo pygame per creare il gioco
import sys  # importiamo sys per uscire dal programma

pygame.init()  # inizializziamo tutti i moduli di pygame

# ---------------- SCHERMO ----------------
W, H = 800, 600  # dimensioni della finestra
screen = pygame.display.set_mode((W, H))  # creiamo la finestra di gioco
pygame.display.set_caption("Grazie Gattino")  # titolo della finestra

clock = pygame.time.Clock()  # controlliamo il tempo del gioco (FPS)

# ---------------- FONT ----------------
title_font = pygame.font.SysFont("arial", 70, bold=True)  # font grande per titolo
font = pygame.font.SysFont("arial", 28)  # font normale
big = pygame.font.SysFont("arial", 50, bold=True)  # font medio-grande

# ---------------- COLORI ----------------
BG = (205, 235, 220)  # colore di sfondo
BTN = (170, 210, 240)  # colore normale dei pulsanti
BTN_HOVER = (150, 190, 220)  # colore quando il mouse è sopra il bottone
TEXT = (30, 50, 50)  # colore del testo

# ---------------- IMMAGINI ----------------
ragazzo_img = pygame.image.load("ragazzo.png")  # carichiamo immagine ragazzo
ragazza_img = pygame.image.load("ragazza.png")  # carichiamo immagine ragazza
zombie_img = pygame.image.load("zombie.png")  # carichiamo immagine zombie

win_img = pygame.image.load("win.png")  # immagine vittoria
lose_img = pygame.image.load("lose.png")  # immagine sconfitta

ragazzo_img = pygame.transform.scale(ragazzo_img, (55, 55))  # ridimensioniamo ragazzo
ragazza_img = pygame.transform.scale(ragazza_img, (55, 55))  # ridimensioniamo ragazza
zombie_img = pygame.transform.scale(zombie_img, (60, 60))  # ridimensioniamo zombie

win_img = pygame.transform.scale(win_img, (300, 300))  # ridimensioniamo win
lose_img = pygame.transform.scale(lose_img, (300, 300))  # ridimensioniamo lose

# ---------------- STATO GIOCO ----------------
state = "menu"  # stato iniziale del gioco (menu)
character = "ragazzo"  # personaggio scelto
difficulty = "easy"  # difficoltà iniziale

player = pygame.Rect(400, 300, 55, 55)  # rettangolo del giocatore
zombie = pygame.Rect(100, 100, 60, 60)  # rettangolo dello zombie

timer = 0  # timer del gioco

# ---------------- VELOCITÀ ----------------
def zspeed():  # funzione per la velocità dello zombie
    return {"easy": 1.5, "medium": 2.5, "hard": 3.5}[difficulty]  # ritorna velocità

# ---------------- FUNZIONI UTILI ----------------
def draw_text(text, y, font, color=TEXT):  # funzione per scrivere testo
    t = font.render(text, True, color)  # creiamo superficie testo
    rect = t.get_rect(center=(W // 2, y))  # centriamo testo
    screen.blit(t, rect)  # disegniamo testo

def button(text, y):  # funzione per creare bottone
    rect = pygame.Rect(W // 2 - 150, y, 300, 60)  # rettangolo bottone
    mouse = pygame.mouse.get_pos()  # posizione mouse

    color = BTN_HOVER if rect.collidepoint(mouse) else BTN  # cambio colore hover

    pygame.draw.rect(screen, color, rect, border_radius=15)  # disegno bottone

    t = font.render(text, True, TEXT)  # testo bottone
    t_rect = t.get_rect(center=rect.center)  # centriamo testo
    screen.blit(t, t_rect)  # disegniamo testo

    return rect  # ritorniamo area cliccabile

# ---------------- LOOP PRINCIPALE ----------------
running = True  # gioco attivo

while running:  # ciclo principale
    clock.tick(60)  # 60 FPS
    screen.fill(BG)  # puliamo schermo

    for e in pygame.event.get():  # eventi
        if e.type == pygame.QUIT:  # chiusura finestra
            running = False  # fermiamo gioco

        if e.type == pygame.MOUSEBUTTONDOWN:  # click mouse
            mx, my = e.pos  # posizione click

            # MENU
            if state == "menu":  # se siamo nel menu
                if play_btn.collidepoint(mx, my):  # clic su play
                    state = "rules"  # passiamo a regole

            # RULES → CHAR
            elif state == "rules":  # schermata regole
                if next_btn.collidepoint(mx, my):  # click next
                    state = "char"  # scelta personaggio

            # CHAR → DIFF
            elif state == "char":  # scelta personaggio
                if boy_btn.collidepoint(mx, my):  # ragazzo
                    character = "ragazzo"  # set personaggio
                    state = "diff"  # vai difficoltà
                if girl_btn.collidepoint(mx, my):  # ragazza
                    character = "ragazza"  # set personaggio
                    state = "diff"  # vai difficoltà

            # DIFF → GAME
            elif state == "diff":  # scelta difficoltà
                if easy_btn.collidepoint(mx, my):  # facile
                    difficulty = "easy"  # set facile
                    state = "game"  # start gioco
                if med_btn.collidepoint(mx, my):  # medio
                    difficulty = "medium"  # set medio
                    state = "game"  # start gioco
                if hard_btn.collidepoint(mx, my):  # difficile
                    difficulty = "hard"  # set difficile
                    state = "game"  # start gioco

            # END
            elif state in ["win", "lose"]:  # fine partita
                if menu_btn.collidepoint(mx, my):  # menu
                    state = "menu"  # ritorno menu

                if restart_btn.collidepoint(mx, my):  # restart
                    player.x, player.y = 400, 300  # reset player
                    zombie.x, zombie.y = 100, 100  # reset zombie
                    timer = 0  # reset timer
                    state = "rules"  # restart gioco

    keys = pygame.key.get_pressed()  # input tastiera

    # ---------------- MENU ----------------
    if state == "menu":  # menu principale
        draw_text("GRAZIE GATTINO", 120, title_font)  # titolo

        play_btn = button("PLAY", 300)  # bottone play

    # ---------------- RULES ----------------
    elif state == "rules":  # regole gioco
        draw_text("Scappa con il gattino usando le frecce", 180, font)
        draw_text("Sopravvivi 60 secondi per salvarlo", 220, font)
        draw_text("Non farti prendere dallo zombie", 260, font)

        next_btn = button("NEXT", 380)  # bottone next

    # ---------------- CHARACTER ----------------
    elif state == "char":  # scelta personaggio
        draw_text("Scegli personaggio", 140, big)

        boy_btn = button("Ragazzo", 260)  # bottone ragazzo
        girl_btn = button("Ragazza", 340)  # bottone ragazza

    # ---------------- DIFFICULTY ----------------
    elif state == "diff":  # scelta difficoltà
        draw_text("Difficoltà", 140, big)

        easy_btn = button("Easy", 240)  # facile
        med_btn = button("Medium", 320)  # medio
        hard_btn = button("Hard", 400)  # difficile

    # ---------------- GAME ----------------
    elif state == "game":  # gioco attivo

        if keys[pygame.K_LEFT]: player.x -= 4  # movimento sinistra
        if keys[pygame.K_RIGHT]: player.x += 4  # movimento destra
        if keys[pygame.K_UP]: player.y -= 4  # movimento su
        if keys[pygame.K_DOWN]: player.y += 4  # movimento giù

        if zombie.x < player.x: zombie.x += zspeed()  # zombie va a destra
        if zombie.x > player.x: zombie.x -= zspeed()  # zombie va a sinistra
        if zombie.y < player.y: zombie.y += zspeed()  # zombie va giù
        if zombie.y > player.y: zombie.y -= zspeed()  # zombie va su

        timer += 1  # aumenta timer
        sec = timer // 60  # convertiamo in secondi

        if sec >= 60:  # vittoria
            state = "win"

        if zombie.colliderect(player):  # collisione
            state = "lose"

        if character == "ragazzo":  # disegno personaggio
            screen.blit(ragazzo_img, (player.x, player.y))
        else:
            screen.blit(ragazza_img, (player.x, player.y))

        screen.blit(zombie_img, (zombie.x, zombie.y))  # disegno zombie

        draw_text(f"Time: {sec}", 20, font)  # timer

    # ---------------- WIN ----------------
    elif state == "win":  # schermata vittoria
        screen.blit(win_img, (250, 120))  # immagine win
        draw_text("Hai salvato il gattino!", 100, big)

        restart_btn = button("PLAY AGAIN", 360)  # restart
        menu_btn = button("MENU", 440)  # menu

    # ---------------- LOSE ----------------
    elif state == "lose":  # schermata sconfitta
        screen.blit(lose_img, (250, 120))  # immagine lose
        draw_text("Oh no! Lo zombie ha preso il gatto", 100, font)

        restart_btn = button("RETRY", 360)  # retry
        menu_btn = button("MENU", 440)  # menu

    pygame.display.update()  # aggiorniamo schermo

pygame.quit()  # chiudiamo pygame
sys.exit()  # chiudiamo programma

