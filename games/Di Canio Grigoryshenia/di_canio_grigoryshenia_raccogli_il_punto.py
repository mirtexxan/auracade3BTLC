import pygame

import random

# Inizializza pygame
pygame.init()

# Dimensioni finestra
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Raccogli il Punto")

# Clock
clock = pygame.time.Clock()

# Colori
GREEN = (50, 180, 50)
BLUE = (50, 120, 255)
RED = (255, 50, 50)
BLACK = (0, 0, 0)

# Giocatore
player = pygame.Rect(400, 300, 40, 40)

# Oggetto da raccogliere
item = pygame.Rect(
    random.randint(0, WIDTH - 20),
    random.randint(0, HEIGHT - 20),
    20,
    20
)

# Font
font = pygame.font.Font(None, 36)

# Punteggio
score = 0

# Loop principale
running = True

while running:

    # Eventi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input tastiera
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.x -= 5

    if keys[pygame.K_RIGHT]:
        player.x += 5

    if keys[pygame.K_UP]:
        player.y -= 5

    if keys[pygame.K_DOWN]:
        player.y += 5

    # Blocca dentro lo schermo
    if player.x < 0:
        player.x = 0

    if player.x > WIDTH - player.width:
        player.x = WIDTH - player.width

    if player.y < 0:
        player.y = 0

    if player.y > HEIGHT - player.height:
        player.y = HEIGHT - player.height

    # Collisione
    if player.colliderect(item):

        score += 1

        item.x = random.randint(0, WIDTH - item.width)
        item.y = random.randint(0, HEIGHT - item.height)

    # Disegno
    screen.fill(GREEN)

    pygame.draw.rect(screen, BLUE, player)

    pygame.draw.ellipse(screen, RED, item)

    # Testo punteggio
    text = font.render(f"Punti: {score}", True, BLACK)
    screen.blit(text, (10, 10))

    # Aggiorna schermo
    pygame.display.flip()

    # FPS
    clock.tick(60)

# Chiusura
pygame.quit()
