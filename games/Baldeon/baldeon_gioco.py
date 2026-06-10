import pygame
import random

pygame.init()

LARGHEZZA, ALTEZZA = 450, 650
schermo = pygame.display.set_mode((LARGHEZZA, ALTEZZA))
pygame.display.set_caption("Alien Attack")

clock = pygame.time.Clock()

nero = (0, 0, 0)
verde = (50, 255, 50)
rosso = (255, 50, 50)
bianco = (255, 255, 255)
giallo = (255, 255, 0)

player = pygame.Rect(225 - 25, ALTEZZA - 60, 50, 30)
vel_player = 6

proiettili = []
vel_proiettile = -8

nemici = []
vel_nemici_y = 2

SPAWN_NEMICO = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_NEMICO, 800)

score = 0
font_punteggio = pygame.font.Font(None, 36)
font_titoli = pygame.font.Font(None, 50)
game_state = "play"


in_esecuzione = True
while in_esecuzione:
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            in_esecuzione = False
            
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and game_state == "play":
                proiettile = pygame.Rect(player.centerx - 2, player.top - 10, 4, 10)
                proiettili.append(proiettile)
                
        if evento.type == SPAWN_NEMICO and game_state == "play":
            x_casuale = random.randint(0, LARGHEZZA - 40)
            nuovo_nemico = pygame.Rect(x_casuale, -40, 40, 30)
            nemici.append(nuovo_nemico)

    if game_state == "play":
        
        tasti = pygame.key.get_pressed()
        if tasti[pygame.K_LEFT]:
            player.x -= vel_player
        if tasti[pygame.K_RIGHT]:
            player.x += vel_player
            
        if player.left < 0:
            player.left = 0
        if player.right > LARGHEZZA:
            player.right = LARGHEZZA

        for p in proiettili[:]:
            p.y += vel_proiettile
            if p.bottom < 0:
                proiettili.remove(p)

        for n in nemici[:]:
            n.y += vel_nemici_y
            if n.colliderect(player) or n.bottom >= ALTEZZA:
                game_state = "game_over"

        for p in proiettili[:]:
            for n in nemici[:]:
                if p.colliderect(n):
                    if p in proiettili:
                        proiettili.remove(p)
                    if n in nemici:
                        nemici.remove(n)
                    score += 10
                    break
                    
        if score >= 150:
            game_state = "win"


    schermo.fill(nero)
    
    if game_state == "play":
        pygame.draw.rect(schermo, verde, player)
        for p in proiettili:
            pygame.draw.rect(schermo, bianco, p)
        for n in nemici:
            pygame.draw.rect(schermo, rosso, n)
            
        testo_score = font_punteggio.render(f"Punti: {score}", True, bianco)
        schermo.blit(testo_score, (10, 10))
        
    elif game_state == "game_over":
        testo_over = font_titoli.render("GAME OVER", True, rosso)
        rect_over = testo_over.get_rect(center=(LARGHEZZA//2, ALTEZZA//2))
        schermo.blit(testo_over, rect_over)
        
    elif game_state == "win":
        testo_win = font_titoli.render("VITTORIA!", True, giallo)
        rect_win = testo_win.get_rect(center=(LARGHEZZA//2, ALTEZZA//2))
        schermo.blit(testo_win, rect_win)
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
