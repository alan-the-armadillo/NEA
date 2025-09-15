from typing import Tuple
import os
from datetime import datetime

import pygame
import pygame.font
pygame.font.init()
font = pygame.font.SysFont("consolas", 50)

from hitbox import *
from enemy import Enemy
from map import Map

class Renderer:
    def __init__(self, window_size:Tuple[int, int]|str):
        if window_size == "fullscreen":
            pygame.display.init()
            size = pygame.display.get_desktop_sizes()[0]
            self.display = pygame.display.set_mode(size, pygame.NOFRAME)
        elif type(window_size) == str:
            raise ValueError (f"Display size command '{window_size}' not recognised.")
        else:
            self.display = pygame.display.set_mode(window_size)
        size = self.display.get_size()
        self.world = pygame.Surface(size)
        self.world_fg = pygame.Surface(size)
        #Transparent layer to make it an overlay
        #The final version of the HUD will use images, so transparent layers should not be an issue
        self.map = pygame.Surface([size[1]/3, size[1]/3])
        self.overlay = pygame.Surface(size, pygame.SRCALPHA)
        self.center = pygame.Vector2(size[0]/2, size[1]/2)

        self.screenshot_life = 0
        self.screenshot_clock = pygame.time.Clock()
    
    def screenshot(self):
        if not os.path.isdir("screenshots"):
            os.mkdir("screenshots")
        now = datetime.now()
        screenshot_name = "screenshots/"+str(datetime.date(now))+"_"+str(now.hour)+"."+str(now.minute)+"."+str(now.second)+".png"
        pygame.image.save(self.display, screenshot_name)
        self.screenshot_life = 3
        self.screenshot_clock.tick() 
        
    
    def debug_render_map(self, map:Map, current_pos:list):
        """Draws the map, including doors and highlighting the room the player is currently in."""
        self.map.fill(0)
        cell_size = (self.map.get_width()/map.size)
        room_size_mult = 0.75
        door_width = 0.2
        room_size = cell_size*room_size_mult
        #Loop through rooms and draw those that have been visited
        for i in range(map.size):
            for j in range(map.size):
                if map.rooms[i][j]:
                    if [i,j] == current_pos:
                        color = [255, 255, 255]
                    else:
                        color = [150, 150, 150]

                    #Draw room
                    mini_room_rect = pygame.Rect((i+(1-room_size_mult)/2)*cell_size, (j+(1-room_size_mult)/2)*cell_size, room_size, room_size)
                    pygame.draw.rect(self.map, color, mini_room_rect)
                    #Make door dimensions and locations on the minimap
                    door_dimensions = [
                        [cell_size*(1-room_size_mult)//2 +2, cell_size*door_width],
                        [cell_size*door_width, cell_size*(1-room_size_mult)//2 +2],
                        [cell_size*(1-room_size_mult)//2 +2, cell_size*door_width],
                        [cell_size*door_width, cell_size*(1-room_size_mult)//2 +2]
                    ]
                    door_locations = [
                        [mini_room_rect.right, mini_room_rect.top+(room_size-door_dimensions[0][1])/2],
                        [mini_room_rect.left+(room_size-door_dimensions[1][0])/2, mini_room_rect.top-door_dimensions[1][1]],
                        [mini_room_rect.left-door_dimensions[2][0], mini_room_rect.top+(room_size-door_dimensions[2][1])/2],
                        [mini_room_rect.left+(room_size-door_dimensions[3][0])/2, mini_room_rect.bottom]
                    ]
                    #Draw doors as required
                    for n, door in enumerate(map.rooms[i][j].doors):
                        if door:
                            pygame.draw.rect(self.map, color, pygame.Rect(door_locations[n], door_dimensions[n]))

    def debug_render_room(self, colliders, interactors, map, current_pos):
        self.world.fill(0)
        [pygame.draw.rect(self.world, [200,200,200], c.rect) for c in colliders]
        for n,i in enumerate(interactors):
            if i != None:
                color = ["red", "yellow", "green", "blue"][n]
                pygame.draw.rect(self.world, color, i.rect, 5)
        self.debug_render_map(map, current_pos)

    
    def debug_render_overlay(self, fps:float):
        self.overlay.fill(0)
        self.overlay.blit(font.render(str(round(fps)), True, "white"), [100,100])
        w = self.overlay.get_width()
        self.overlay.blit(self.map, [w-self.map.get_width(),0])

        if self.screenshot_life > 0:
            self.overlay.blit(font.render("Screenshot taken", True, [255,255,255]), [0 , self.overlay.get_height()-font.get_height()])
            self.screenshot_life -= self.screenshot_clock.get_time()/1000
            self.screenshot_clock.tick()


    def debug_render_frame(self, player_collider:EntityCollider, player_interactor:PlayerInteractor, fps:float):
        #Reset the frame
        self.display.fill(0)
        #Draw the background
        self.world_fg.blit(self.world, [0,0])
        #Draw the enemies
        for enemy in Enemy.all:
            pygame.draw.rect(self.world_fg, [255,20,50], enemy.collider.rect)
        #Highlight closest interactor
        if player_interactor.closest_interactor:
            rect = player_interactor.closest_interactor.rect
            pygame.draw.rect(self.world_fg, [255,255,255], pygame.Rect([rect.left-5, rect.top-5], [rect.width+10, rect.height+10]), 5)
        self.display.blit(self.world_fg, self.center - player_collider.rect.center)
        #Draw player interactor
        pygame.draw.rect(self.display, [50,50,50], pygame.Rect(self.center - player_interactor.hdim, player_interactor.rect.size), 5)
        #Draw player collider
        pygame.draw.rect(self.display, [180,130,200], pygame.Rect(self.center - player_collider.hdim, player_collider.rect.size))
        #Draw the map, fps and screenshot acknowledgement
        self.debug_render_overlay(fps)
        self.display.blit(self.overlay, [0,0])
        #Update the frame
        pygame.display.update()

