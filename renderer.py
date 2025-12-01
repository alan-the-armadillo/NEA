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
        size = [2400, 1350]#self.display.get_size()
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
                                line_length = mini_room_rect.width/8
                                for d in range(0, 8, 3):
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

        x_end = 300*round(self.player.HP/self.player.max_HP)
        pygame.draw.rect(self.overlay, [255,0,0], pygame.Rect([0,0], [x_end,50]))
        pygame.draw.rect(self.overlay, [255,255,255], pygame.Rect([0,0], [x_end,50]), 5)

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
Need to fix animation layer rendering. The problem seems to be that layers are in the wrong order if the limb has a different
anim to the rest of the body. This could be fixed by taking the median limb as the center and inserting the other limbs of the animation around it,
such that the median limb is at the same sequence as it was before the new animation was pushed to the stack, and the other limbs of the
new animation move to be the same offset from the median limb as in the new animation. e.g. new animation with sequencing of lhand, torso, rhand.
Torso is left at the sequence it is at, say 3, lhand moves to the layer below torso (2) and r hand moves to the layer above torso (4).

Need to implement variable usage into renderer size. At the moment, it is hard set to [2400,1350] due to the room dimensions and collider size.
If either was changed, the screen would render bits weird (either unnecessary space or drawn off screen).

Currently have implemented feet-level hitbox, but this note is worth keeping:
Need to update player hitbox. Either use per-sprite hitboxes (may be a very bad idea) or just make a larger player hitbox.
OR! put the collision hitbox at the player's feet/blit the player such that the feet are at the bottom. This will either require a total
system change to better the efficiency so it saves limbs in relation to the base feet position, or ignore efficiency and go for current model
(would prefer efficiency due to how much this system is going to work during gameplay).
"""

class PlayerRenderer():
    SCALE = 5
    FPS = 14
    MSPF = 1000/FPS
    with open("anim_data.json", "r") as file:
        animation_data = json.load(file)
    with open("sprite_offsets.json", "r") as file:
        offset_data = json.load(file)
    def __init__(self, player:Player, anim):
        self.player = player
        self.player.renderer = self

        self.limbs = {
            "head" : [anim],
            "torso" : [anim],
            "left foot" : [anim],
            "right foot" : [anim],
            "left hand" : [anim],
            "right hand" : [anim],
            "left melee" : [anim],
            "right melee" : [anim],
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
        # [frame_num, clock, time since last frame, sing_run]
        self.anims= {
            anim : [0, pygame.time.Clock(), 0, False],
        }

    def __get_direction_anim_name(self, anim:str):
        """Switches left-right if facing left.
        Returns the anim name fixed for current direction.
        """
        if not self.player.direction:
            if "left" in anim:
                return anim.replace("left", "right")
            elif "right" in anim:
                return anim.replace("right", "left")
        return anim
    
    def __get_direction_limb_name(self, limb:str):
        """Switches left-right if facing left.
        Returns the limb name fixed for current direction.
        """
        if not self.player.direction:
            if "left" in limb:
                return limb.replace("left", "right")
            elif "right" in limb:
                return limb.replace("right", "left")
        return limb

    def __get_cache_frame_name(self, anim):
        """Returns the possible key to the anim frame data.
        This should be used both to find values in the cache as well as making the key for new values in the cache.
        """
        return f"{anim}FRAME{self.anims[anim][0]}{["left","right"][int(self.player.direction)]}"

    def load_anim(self, anim:str, single_run:bool, insert_index=0):
        """Loads in an animation for all applicable limbs.
        """
        anim_data = PlayerRenderer.animation_data[anim]
        self.anims.update({anim: [0,pygame.time.Clock(), 0, single_run]})
        for limb_name in anim_data:
            if limb_name in self.player.inventory and self.player.inventory[limb_name]:
                self.limbs[limb_name].insert(insert_index, anim)

    def unload_anim(self, anim:str):
        """Unloads and animation for all applicable limbs.
        If this results in an animation uncovering from not playing, then it will be reset to frame 0.
        """
        anim_data = PlayerRenderer.animation_data[anim]
        self.anims.pop(anim)
        #Test which animations are loaded (playing) currently
        loaded = []
        for other_anim in self.anims:
            loaded.append(any([self.limbs[l][0] == other_anim for l in self.limbs]))
        #Stop playing current aniamtion
        for limb_name in anim_data:
            try:
                self.limbs[limb_name].remove(anim)
            except:
                pass
        #Test which animations will now be loaded (playing)
        for i, other_anim in enumerate(self.anims):
            #If an animation has been loaded due to an animation being unloaded, reset it
            if any([self.limbs[l][0] == other_anim for l in self.limbs]) and not loaded[i]:
                self.anims[other_anim][1].tick()
                self.anims[other_anim][0] = 0

    def load_frame(self, limb_name, anim, player_pos):
        """Loads in object for a frame.
        Returns [relative position (to pos), rotation, sequence, img]."""
        #Get relevant animation and limb (just anim and limb_name if right, otherwise gets counterpart)
        new_anim = self.__get_direction_anim_name(anim)
        new_limb = self.__get_direction_limb_name(limb_name)
        #Get frame data
        frame_data = PlayerRenderer.animation_data[new_anim][new_limb][self.anims[anim][0]]
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
        #Relative position
        true_pos = -relative_center + real_pos
        #Get rotated image and the fix the rel_pos to keep center consistent
        rotated_img = pygame.transform.rotate(img, rot)
        rect = img.get_rect(topleft = true_pos)
        rel_pos = rotated_img.get_rect(center=rect.center).topleft
        #Flip animation if facing the other way
        if not self.player.direction:
            rotated_img = pygame.transform.flip(rotated_img, flip_x=True, flip_y=False)
            rel_pos = [-rel_pos[0]-rotated_img.get_width(), rel_pos[1]]
        #Add animation to cache
        self.cache[limb_name].update({self.__get_cache_frame_name(anim):[rel_pos, rotated_img, seq]})
        #Get actual player pos
        final_pos = [rel_pos[0]+player_pos[0], rel_pos[1]+player_pos[1]]

        return [final_pos, rotated_img, seq]
    
    def next_frame(self):
        """DOES NOT YET ALLOW FOR SPRITES WITH THEIR OWN SPRITE SHEETS.
        Checks to see if limb animations should be progressed and, if so, progresses them.
        """
        unloads = []
        #Loop through animations:
        for animation in self.anims:
            #If showing this animation:
            if any([animation==self.limbs[l][0] for l in self.limbs]):
                #Tick clock
                self.anims[animation][2] += self.anims[animation][1].tick()
                #Next frame if necessary
                if self.anims[animation][2] >= PlayerRenderer.MSPF:
                    self.anims[animation][2] = 0
                    self.anims[animation][0] += 1
                    #If the animation has now ended
                    new_anim = self.__get_direction_anim_name(animation)
                    if len(PlayerRenderer.animation_data[new_anim][list(PlayerRenderer.animation_data[new_anim].keys())[0]]) == self.anims[animation][0]:
                        if self.anims[animation][3]: #Not looping
                            unloads.append(animation)
                        else: #Looping
                            self.anims[animation][0] = 0
        #Unload any animations flagged for unloading.
        [self.unload_anim(animation) for animation in unloads]

    def render_frame(self, surface, player_pos):
        """Renders the current limb frames to the surface.
        Will load in data from the cache where possible, otherwise will load in the frame.
        """
        offset = [0,-30*PlayerRenderer.SCALE+self.player.collider.rect.height]
        render_data = []

        for limb in self.limbs:
            try:
                animation = self.limbs[limb][0]
                #Loads if cached
                if self.__get_cache_frame_name(animation) in self.cache[limb]:
                    rel_pos, rotated_img, seq = self.cache[limb][self.__get_cache_frame_name(animation)]
                    true_pos = [rel_pos[0]+player_pos[0], rel_pos[1]+player_pos[1]]
                #Otherwise, creates frame
                else:
                    if self.player.direction:
                        true_pos, rotated_img, seq = self.load_frame(limb, animation, player_pos)
                    else:
                        true_pos, rotated_img, seq = self.load_frame(limb, animation, player_pos)

                render_data.append([rotated_img, true_pos, seq])
            except AttributeError:
                pass
        #Render limbs in order of sequence number.
        render_data = sorted(render_data, key=lambda o:o[2])
        for limb in render_data:
            surface.blit(limb[0], [limb[1][0]+offset[0], limb[1][1]+offset[1]])