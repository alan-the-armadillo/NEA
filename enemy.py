from time import time
from random import uniform
import json
from entity import Entity
from behaviour_tree import BehaviourTree

class Enemy(Entity):
    all:list["Enemy"] = []
    update_time_min = 0.01
    update_time_max = 0.2
    with open("enemies.json", "r") as file:
        data = json.load(file)
    
    def parse_data(self):
        self.name = self.data["name"]
        self.AI = BehaviourTree(self, self.data["ai id"])
        self.HP = self.data["HP"]
        self.ATK = self.data["ATK"]
        self.SPD = self.data["SPD"]

    def generate_update_time(self):
        self.next_update_time = time() + uniform(Enemy.update_time_min, Enemy.update_time_max)

    def __init__(self, ID, pos):
        Enemy.all.append(self)
        super().__init__(pos)
        self.ID = ID
        self.data = Enemy.data[ID]
        self.parse_data()
        self.behaviour = None
        self.generate_update_time()
    
    @staticmethod
    def update_all():
        """Updates all enemies' behaviour trees.
        """
        for enemy in Enemy.all:
            current_time = time()
            if time() >= enemy.next_update_time:
                enemy.AI.update()
                enemy.generate_update_time()
    
    @staticmethod
    def behave_all():
        """Has each enemy perform some behaviour if required.
        """
        for enemy in Enemy.all:
            if enemy.behaviour != None:
                enemy.behaviour()