import json
import pygame

class Item:
    with open("item_data.json", "r") as file:
        all_data = json.load(file)
    def __init__(self, ID):
        self.data = Item.all_data[ID]
        self.name = self.data["name"]
        self.stat_boosts = self.data["stat boosts"]
        self.img = pygame.image.load("sprites/"+self.data["img"])

class Limb(Item):
    def __init__(self, ID):
        super().__init__(ID)
        self.slot = self.data["slot"]
        if "denies" in list(self.data.keys()):
            self.deny = True

class Weapon(Item):
    def __init__(self, ID):
        super().__init__(ID)
        self.slot_size = self.data["slot size"]
        self.base_damage = self.data["base damage"]
        self.weapon_type = self.data["weapon type"]
        self.equiv_anim = self.data["equiv_anims"]
        self.hitboxes = self.data["hitboxes"]