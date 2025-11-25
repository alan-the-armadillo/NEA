from typing import overload

from hitbox import *
from entity import Entity
from item import Limb, Weapon

class Player(Entity):
    def __init__(self, pos):
        super().__init__(pos, [100,50])
        self.interactor = PlayerInteractor(pos, [200,200])
        self.renderer = None

        self.max_HP = 100
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
    
    def update_motion_vector(self, new_vector):
        initial_motion = self.get_sub_motion_vector()
        super().update_motion_vector(new_vector)
        final_motion = self.get_sub_motion_vector()
        self.check_anim_updates(initial_motion, final_motion)
    
    def add_to_motion_vector(self, adding_vector):
        initial_motion = self.get_sub_motion_vector()
        super().add_to_motion_vector(adding_vector)
        final_motion = self.get_sub_motion_vector()
        self.check_anim_updates(initial_motion, final_motion)
    
    def check_anim_updates(self, initial_motion, final_motion):
        #If stopped moving:
        if (initial_motion[0] != 0 or initial_motion[1] != 0) and final_motion == [0,0]:
            self.renderer.unload_anim("walk")
        #If started moving:
        elif initial_motion == [0,0] and (final_motion[0] != 0 or final_motion[1] != 0):
            self.renderer.load_anim("walk", False, insert_index=-1)

    def move(self):
        """Moves player collider"""
        new_pos = super().move(self.SPD)
        self.interactor.rect.center = new_pos
        self.interactor.get_closest_interactor()