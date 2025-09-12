import pygame

class Button:
    all:list["Button"] = []
    def __init__(self, text, pos, dim):
        self.text = text
        self.rect = pygame.Rect(pos, dim)
    
    def mouse_check(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)