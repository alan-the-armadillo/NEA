import pygame
from typing import overload

from hitbox import *
from entity import Entity

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos)
        self.interactor = PlayerInteractor(pos, [200,200])

        self.HP = 100
        self.ATK = 5
        self.SPD = 5

        self.inventory = { ###########WORK ON INVENTORY AND ITEMS NEXT (stats will also be worked on in the process)
            "head" : None,
            "torso" : None,
            "lhand" : None,
            "rhand" : None,
            "lfoot" : None,
            "rfoot" : None
        }
    
    def update_position(self, new_pos):
        super().update_position(new_pos)
        self.interactor.rect.center = new_pos
        self.interactor.get_closest_interactor()

    def move(self):
        """Moves player collider"""
        new_pos = super().move(self.SPD)
        self.interactor.rect.center = new_pos
        self.interactor.get_closest_interactor()