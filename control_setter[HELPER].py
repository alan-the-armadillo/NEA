import pygame
import pygame.font

pygame.font.init()

size = 100

font = pygame.font.SysFont("consolas", size)

display = pygame.display.set_mode([1000,size])

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            display.fill(0)
            key = str(event.key)
            display.blit(font.render(key, True, "white"),[display.get_width()/2 - len(key)*size/4, display.get_height()/2 - size/2])
            if event.type == pygame.KEYUP:
                print(key)
            pygame.display.update()
        elif event.type == pygame.QUIT:
            running = False