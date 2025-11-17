import pygame
from typing import overload

from hitbox import *
from entity import Entity
from item import Limb, Weapon

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos)
        self.interactor = PlayerInteractor(pos, [200,200])

        self.HP = 100
        self.ATK = 5
        self.SPD = 5

        self.inventory = { ###########WORK ON INVENTORY AND ITEMS NEXT (stats will also be worked on in the process)
            "torso" : Limb("l0"),
            "head" : Limb("l1"),
            "left hand" : Limb("l2"),
            "right hand" : Limb("l2"),
            "left foot" : Limb("l3"),
            "right foot" : Limb("l3"),
            "left melee" : Weapon("w0"),
            "right melee" : Weapon("w0")
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