from typing import Tuple

import pygame
import pygame.font
pygame.font.init()
font = pygame.font.SysFont("consolas", 20)

from hitbox import *
from enemy import Enemy

class Renderer:
    def __init__(self, window_size:Tuple[int, int]):
        self.display = pygame.display.set_mode(window_size)
        self.world = pygame.Surface(window_size)
        self.world_fg = pygame.Surface(window_size)  ###################################
        self.center = pygame.Vector2(window_size[0]/2, window_size[1]/2)
    
    def debug_render_room(self, colliders, interactors):
        self.world.fill(0)
        [pygame.draw.rect(self.world, [200,200,200], c.rect) for c in colliders]
        for n,i in enumerate(interactors):
            if i != None:
                color = ["red", "yellow", "green", "blue"][n]
                pygame.draw.rect(self.world, color, i.rect, 5)


    def debug_render_frame(self, player_collider:EntityCollider, player_interactor:PlayerInteractor):
        self.display.fill(0)
        self.world_fg.blit(self.world, [0,0])
        for enemy in Enemy.all:
            pygame.draw.rect(self.world_fg, [255,20,50], enemy.collider.rect)
        self.display.blit(self.world_fg, self.center - player_collider.rect.center)
        pygame.draw.rect(self.display, [50,50,50], pygame.Rect(self.center - player_interactor.hdim, player_interactor.rect.size))
        pygame.draw.rect(self.display, [180,130,200], pygame.Rect(self.center - player_collider.hdim, player_collider.rect.size))
        if player_interactor.closest_interactor:
            self.display.blit(font.render(player_interactor.closest_interactor.__class__.name, True, "yellow"), self.center - player_collider.rect.center + player_interactor.closest_interactor.rect.topleft)
        
        #self.display.blit(self.world, [0,0])
        #pygame.draw.rect(self.display, [200, 130, 220], player_collider.rect)
        pygame.display.update()