from typing import Tuple
import os
from datetime import datetime

import json

import pygame
import pygame.font
pygame.font.init()
font = pygame.font.SysFont("consolas", 50)

from hitbox import *
from enemy import Enemy
from player import Player
from map import Map

class Renderer:
    def __init__(self, window_size:Tuple[int, int]|str, player:Player):
        if window_size == "fullscreen":
            pygame.display.init()
            size = pygame.display.get_desktop_sizes()[0]
            self.display = pygame.display.set_mode(size, pygame.NOFRAME)
        elif type(window_size) == str:
            raise ValueError (f"Display size command '{window_size}' not recognised.")
        else:
            self.display = pygame.display.set_mode(window_size)
        size = [1600,900]#self.display.get_size()
        self.world = pygame.Surface(size)
        self.world_fg = pygame.Surface(size)
        #Transparent layer to make it an overlay
        #The final version of the HUD will use images, so transparent layers should not be an issue
        self.map = pygame.Surface([self.display.get_height()/3, self.display.get_height()/3])
        self.overlay = pygame.Surface(self.display.get_size(), pygame.SRCALPHA)
        self.center = pygame.Vector2(self.display.get_rect().center)

        self.player = player
        PlayerRenderer(player, "idle")

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
        mini_room_rect = pygame.Rect(0, 0, room_size, room_size)
        adjacencies = [[1,0], [0,-1], [-1,0], [0,1]]
        dotted_drawn = []
        dotted_color = [150, 150, 150]
        #Loop through rooms and draw those that have been visited
        for i in range(map.size):
            for j in range(map.size):
                if map.rooms[i][j]:
                    if [i,j] == current_pos:
                        color = [255, 255, 255]
                    else:
                        color = [150, 150, 150]

                    #Draw room
                    mini_room_rect.topleft= [(i+(1-room_size_mult)/2)*cell_size, (j+(1-room_size_mult)/2)*cell_size]
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
                            neighbor_index = [i+adjacencies[n][0],j+adjacencies[n][1]]
                            if not map.rooms[neighbor_index[0]][neighbor_index[1]] and neighbor_index not in dotted_drawn:
                                dotted_drawn.append(neighbor_index)
                                mini_room_rect.topleft= [(neighbor_index[0]+(1-room_size_mult)/2)*cell_size, (neighbor_index[1]+(1-room_size_mult)/2)*cell_size]
                                line_length = mini_room_rect.width/12
                                for d in range(0, 12, 4):
                                    start_x = mini_room_rect.left+d*line_length
                                    pygame.draw.line(self.map, dotted_color, [start_x, mini_room_rect.top], [start_x+line_length, mini_room_rect.top], 2)
                                    start_x = mini_room_rect.right-d*line_length
                                    pygame.draw.line(self.map, dotted_color, [start_x, mini_room_rect.bottom], [start_x-line_length, mini_room_rect.bottom], 2)
                                    start_y = mini_room_rect.top+d*line_length
                                    pygame.draw.line(self.map, dotted_color, [mini_room_rect.right, start_y], [mini_room_rect.right, start_y+line_length], 2)
                                    start_y = mini_room_rect.bottom-d*line_length
                                    pygame.draw.line(self.map, dotted_color, [mini_room_rect.left, start_y], [mini_room_rect.left, start_y-line_length], 2)
                                

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


    def debug_render_frame(self, fps:float):
        #Reset the frame
        self.display.fill(0)
        #Draw the background
        self.world_fg.blit(self.world, [0,0])
        #Draw the enemies
        for enemy in Enemy.all:
            pygame.draw.rect(self.world_fg, [255,20,50], enemy.collider.rect)
        #Highlight closest interactor
        player_interactor = self.player.interactor
        player_collider = self.player.collider
        if player_interactor.closest_interactor:
            rect = player_interactor.closest_interactor.rect
            pygame.draw.rect(self.world_fg, [255,255,255], pygame.Rect([rect.left-5, rect.top-5], [rect.width+10, rect.height+10]), 5)
        self.display.blit(self.world_fg, self.center - player_collider.rect.center)
        #Draw player interactor
        #pygame.draw.rect(self.display, [50,50,50], pygame.Rect(self.center - player_interactor.hdim, player_interactor.rect.size), 5)
        #Draw player collider
        #pygame.draw.rect(self.display, [180,130,200], pygame.Rect(self.center - player_collider.hdim, player_collider.rect.size))
        
        self.player.renderer.next_frame()
        self.player.renderer.render_frame(self.display, self.center)
        
        #Draw the map, fps and screenshot acknowledgement
        self.debug_render_overlay(fps)
        self.display.blit(self.overlay, [0,0])
        #Update the frame
        pygame.display.update()

""" ## In order of urgency ##

Need to create a method in PlayerRenderer that loads in an animation by name.
It should load it in for the corresponding limbs with the corresponding data (single run is provided as parameter on top of anim name).
Another function should be implemented to unload an animation, taking it off corresponding limbs.
Also need to check the current code handles single runs.
Loading and unloading means that, in the changing movement vector section of the player class (need to make one and then __super()__),
the checks need to be made to add or remove animations from the list (done by comparing last motion vector to current motion vector).

There seems to be an issue with creating frames, such that, during testing, frames were being created (significantly less than those being loaded in)
when really no frames should have been created since it was loading a repeated animation.

Also need to fix the issue with the screen, where wall colliders at the edge of the map are not rendered correctly due to the surface
size being too small. It works on a larger monitor because the surface fits the monitor. You need to ensure the surface will be able
to fit any map area, regardless of screen size.

AND may want to implement functionality to allow limbs to not be rendered if there is no limb in the relevant player inventory slot.

Need to update player hitbox. Either use per-sprite hitboxes (may be a very bad idea) or just make a larger player hitbox.
OR! put the collision hitbox at the player's feet/blit the player such that the feet are at the bottom. This will either require a total
system change to better the efficiency so it saves limbs in relation to the base feet position, or ignore efficiency and go for current model
(would prefer efficiency due to how much this system is going to work during gameplay).
"""

class PlayerRenderer():
    SCALE = 5
    FPS = 12
    MSPF = 1000/FPS
    with open("anim_data_refined.json", "r") as file:
        animation_data = json.load(file)
    with open("sprite_offsets.json", "r") as file:
        offset_data = json.load(file)
    def __init__(self, player:Player, anim):
        self.player = player
        self.player.renderer = self
        # [anim_name, frame_number, single_run]
        self.anims = {
            "head" : [[anim,0,False]],
            "torso" : [[anim,0,False]],
            "left foot" : [[anim,0,False]],
            "right foot" : [[anim,0,False]],
            "left hand" : [[anim,0,False]],
            "right hand" : [[anim,0,False]],
            "left melee" : [[anim,0,False]],
            "right melee" : [[anim,0,False]]
        }
        # [frame data]
        self.cache = {
            "head" : {},
            "torso" : {},
            "left foot" : {},
            "right foot" : {},
            "left hand" : {},
            "right hand" : {},
            "left melee" : {},
            "right melee" : {}
        }
        # [clock, time since last frame]
        self.timing = {
            "head" : [pygame.time.Clock(), 0],
            "torso" : [pygame.time.Clock(), 0],
            "left foot" : [pygame.time.Clock(), 0],
            "right foot" : [pygame.time.Clock(), 0],
            "left hand" : [pygame.time.Clock(), 0],
            "right hand" : [pygame.time.Clock(), 0],
            "left melee" : [pygame.time.Clock(), 0],
            "right melee" : [pygame.time.Clock(), 0],
        }

    def load_anim(self, anim:str, single_run:bool):
        anim_data = PlayerRenderer.animation_data[anim]
        for limb_name in anim_data:
            if limb_name in self.player.inventory and self.player.inventory[limb_name]:
                self.anims[limb_name] = [[anim, 0, single_run]] + self.anims[limb_name]
                self.timing[limb_name][1] = 0

    def unload_anim(self, anim:str):
        anim_data = PlayerRenderer.animation_data[anim]
        for limb_name in anim_data:
            self.anims[limb_name] = list(filter(lambda l: l[0] != anim, self.anims[limb_name]))
            self.timing[limb_name][1] = 0

    def load_frame(self, limb_name, anim):
        """Loads in object for a frame.
        Returns [relative position (to pos), rotation, sequence, img]."""
        #Get frame data
        frame_data = PlayerRenderer.animation_data[anim[0]][limb_name][anim[1]]
        #Retrieve data
        relative_pos, rot, seq, vec_rot = frame_data["pos"], frame_data["rot"], frame_data["seq"], frame_data["offset vector rot"]
        #Format and calculate useful data
        real_pos = relative_pos[0]*self.SCALE, relative_pos[1]*self.SCALE
        #Img
        img = pygame.transform.scale_by(self.player.inventory[limb_name].img, PlayerRenderer.SCALE)
        img_name = self.player.inventory[limb_name].data["img"]
        if img_name in PlayerRenderer.offset_data:
            relative_center = (pygame.Vector2(PlayerRenderer.offset_data[img_name])*self.SCALE).rotate(vec_rot)
        else:
            relative_center = pygame.Vector2(img.get_rect().center).rotate(vec_rot)
        #Relative positino
        true_pos = -relative_center + real_pos
        return [true_pos, rot, seq, img]
    
    def next_frame(self):
        """DOES NOT YET ALLOW FOR SPRITES WITH THEIR OWN SPRITE SHEETS.
        Checks to see if limb animations should be progressed and, if so, progresses them.
        """
        #Loop through limbs
        for limb_name in self.anims:
            #Tick clock
            self.timing[limb_name][1] += self.timing[limb_name][0].tick()
            #If at next FPS time (ergo next frame should be shown)
            if self.timing[limb_name][1] >= PlayerRenderer.MSPF:
                self.timing[limb_name][1] = 0
                #Increment frame number
                self.anims[limb_name][0][1] += 1
                #If the animation has now ended
                if len(PlayerRenderer.animation_data[self.anims[limb_name][0][0]][limb_name]) == self.anims[limb_name][0][1]:
                    if self.anims[limb_name][0][2]: #Not looping
                        self.anims[limb_name] = self.anims[limb_name][1:]
                    else: #Looping
                        self.anims[limb_name][0][1] = 0

    def render_frame(self, surface, player_pos):
        offset = [0,-30*PlayerRenderer.SCALE+self.player.collider.rect.height]
        render_data = []
        for limb_name, limb_data in list(self.anims.items()):
            #Loads cached sprite frame if existing
            if limb_data[0][0] + f"FRAME{limb_data[0][1]}" in self.cache[limb_name]:
                rel_pos, rotated_img, seq = self.cache[limb_name][limb_data[0][0] + f"FRAME{limb_data[0][1]}"]
            #Otherwise, creates the sprite frame, then caches it
            else:
                frame_data = self.load_frame(limb_name, limb_data[0])
                ############# ISSUE MAY ARISE IF PLAYER POS IS CENTRE OF TORSO RATHER THAN TOPLEFT
                #Rotated image
                rotated_img = pygame.transform.rotate(frame_data[3], frame_data[1])
                seq = frame_data[2]
                #Cache [pos, img] for the specific frame
                rect = frame_data[3].get_rect(topleft = frame_data[0])
                #Use this pos to keep rotation central
                rel_pos = rotated_img.get_rect(center=rect.center).topleft
                self.cache[limb_name].update({limb_data[0][0]+f"FRAME{limb_data[0][1]}":[rel_pos, rotated_img, seq]})

            if self.player.direction:
                true_pos = [rel_pos[0]+player_pos[0], rel_pos[1]+player_pos[1]]
            else:
                true_pos = [-rel_pos[0]+player_pos[0]-rotated_img.get_width(), rel_pos[1]+player_pos[1]]
                rotated_img = pygame.transform.flip(rotated_img, flip_x=True, flip_y=False)
            render_data.append([rotated_img, true_pos, seq])
        render_data = sorted(render_data, key=lambda o:o[2])
        for limb in render_data:
            surface.blit(limb[0], [limb[1][0]+offset[0], limb[1][1]+offset[1]])