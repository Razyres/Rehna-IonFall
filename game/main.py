import pygame

pygame.init()

screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
running = True
x = 0
y = 0

image = pygame.image.load("ball.png").convert_alpha()
image = pygame.transform.scale(image, (200, 200))

while running :
    for event in pygame.event.get():
        if event.type == pygame.QUIT :
            running = False
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]:
        y -= 1
    if pressed[pygame.K_a]:
        x -= 1
    if pressed[pygame.K_s]:
        y += 1
    if pressed[pygame.K_d]:
        x += 1
    screen.fill((0, 0, 0))
    screen.blit(image, (x, y))
    pygame.display.flip()
    clock.tick(60)
pygame.quit()