"""WILL NEED AT SOME POINT, JUST NOT RIGHT NOW


INSTEAD OF SAVING TO AN INTERNAL FOLDER, SAVE FILES SHOULD BE SAVED TO LOCAL APPDATA USING THE LINE 'os.getenv("LOCALAPPDATA")'.
"""



import pygame
import json
from UI import Button
from map import Map

class SaveParser:
    def __init__(self, game):
        self.game = game

    def new_file(self):
        #Solve player
        self.game.player.HP = 100
        self.game.player.ATK = 0
        self.game.player.SPD = 5
        self.game.player.inventory = { ###########WORK ON INVENTORY AND ITEMS NEXT (stats will also be worked on in the process)
            "head" : None,
            "torso" : None,
            "lhand" : None,
            "rhand" : None,
            "lfoot" : None,
            "rfoot" : None
        }
        #Solve map
        self.game.map = Map(5)
        self.game.current_pos = self.map.center.copy()

    def file_selection_start(self, screen_size):
        w,h = screen_size
        new_file_button = Button("NEW GAME", [0,0], [w/2, h])
        continue_button = Button("CONTINUE", [w/2, 0], [w,h])
        Button.all = [new_file_button, continue_button]
    
    def file_select_click(self, mouse_pos):
        for button in Button.all:
            if button.mouse_check(mouse_pos):
                button_name = button.text
                break
        if button_name == "NEW GAME":
            self.new_file()
        else:
            self.load_save()