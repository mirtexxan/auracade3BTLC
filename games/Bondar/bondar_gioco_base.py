import pygame
import random

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Zombie Game")

clock = pygame.time.Clock()

player = pygame.Rect(400, 300, 30, 30)
zombies = []
speed = 6

running = True

while running:

    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.x -= speed
    if keys[pygame.K_RIGHT]:
        player.x += speed
    if keys[pygame.K_UP]:
        player.y -= speed
    if keys[pygame.K_DOWN]:
        player.y += speed

    if random.randint(1, 30) == 1:
        zombie = pygame.Rect(
            random.randint(0, 770),
            random.randint(0, 570),
            30, 30
        )
        zombies.append(zombie)

    for z in zombies:
        if z.x < player.x:
            z.x += 2
        if z.x > player.x:
            z.x -= 2
        if z.y < player.y:
            z.y += 2
        if z.y > player.y:
            z.y -= 2

        if z.colliderect(player):
            running = False

    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, (0, 255, 0), player)

    for z in zombies:
        pygame.draw.rect(screen, (255, 0, 0), z)

    pygame.display.update()

pygame.quit()
