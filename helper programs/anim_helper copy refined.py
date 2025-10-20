import pygame
import os
import json
import time
from copy import copy
pygame.font.init()
font = pygame.font.SysFont("consolas", 20)

import math

#Borderless fullscreen
def make_display():
    global display
    pygame.display.init()
    display = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0], pygame.NOFRAME)

make_display()

dir = os.getcwd()
filename = os.path.join(dir, "anim_data_refined.json")

#By how much sprites are scaled up, and then positions are scaled down for saving
SCALE = 10

def custom_dump(obj, fp, indent: int = 4, inline_level: int = 3):
    """Use to write data to a json file with a custom formatting.
    Arguments:
        obj : the actual object you want to save
        fp : the file opened that will be written to
        indent : how many spaces per indent
        inline_level : at this level and further in the structure, data will be written in one line"""
    def inline(o):
        if isinstance(o, list):
            return "[" + ", ".join([inline(value) for value in o]) + "]"
        elif isinstance(o, dict):
            return "{" + ", ".join([f"{json.dumps(key)}: {inline(value)}" for key,value in o.items()]) + "}"
        return json.dumps(o)
    def write(o, depth):
        curr_indent = ' ' * indent*depth
        #If a dictionary
        if isinstance(o, dict):
            #If at end of depth, one line
            if depth >= inline_level:
                fp.write(inline(o))
                return
            #Otherwise, write it in multiple lines
            fp.write("{\n")
            for i, (key,value) in enumerate(o.items()):
                fp.write(" " * indent*(depth+1) + f"{json.dumps(key)}: ")
                write(value, depth + 1)
                if i != len(o.items()) -1:
                    fp.write(",\n")
            fp.write("\n" + curr_indent + "}")
        #If a list
        elif isinstance(o, list):
            #If at end of depth and full of non dict/lists, one line
            if depth >= inline_level or all([not isinstance(x, (dict, list)) for x in o]):
                fp.write(inline(o))
                return
            #Otherwise, write it in multiple lines
            fp.write("[\n")
            for i, value in enumerate(o):
                fp.write(" " * indent*(depth+1))
                write(value, depth + 1)
                if i != len(o) -1:
                    fp.write(",\n")
            fp.write("\n" + curr_indent + "]")
        else:
            fp.write(json.dumps(o))
    
    write(obj, 0)
    fp.write("\n")

class Frame:
    def __init__(self, surface:pygame.Surface, objects:dict):
        self.surface = surface
        self.objects:dict[Sprite] = objects
        self.opacity = 255
        self.render()
    @staticmethod
    def copy(frame:"Frame"):
        surface = frame.surface.copy()
        objects = {copy(key):copy(value) for key,value in frame.objects.items()}
        return Frame(surface, objects)

    def render(self):
        self.surface.fill(0)
        for objects in self.objects:
            objects.draw(self.surface)
    def draw(self, surface:pygame.Surface, opacity=255):
        #Setting here prevents repeating alpha setting later when unnecessary
        if self.opacity != opacity:
            self.opacity = opacity
            self.surface.set_alpha(opacity)
        surface.blit(self.surface, [0,0])


class Sprite:
    def __init__(self, img_name, pos, rot, text=None):
        self.img = pygame.transform.scale_by(pygame.image.load("sprites/"+img_name), SCALE)
        self.pos = pos
        self.rot = rot
        self.text = text
        if self.text:
            self.text = font.render(self.text, True, [255,255,255], [0,0,0])
        sprite_rect = self.img.get_rect()
        self.width, self.height = sprite_rect.size
        self.hw, self.hh = self.width/2, self.height/2
        self.highlighted = False
    
    def get_rect(self):
        return self.img.get_rect(topleft=self.pos)

    def draw(self, surface:pygame.Surface):
        """Draws the Sprite.
        Accounts for rotation, and rotates from the center."""
        center = self.img.get_rect().center
        rotated_img = pygame.transform.rotate(self.img, self.rot)
        new_center = rotated_img.get_rect().center
        new_pos = [self.pos[0], self.pos[1]]
        new_pos[0] -= new_center[0]-center[0]
        new_pos[1] -= new_center[1]-center[1]

        surface.blit(rotated_img, new_pos)
    
    def draw_highlight(self, surface, width):
        sprite_rect = self.img.get_rect()
        w,h = sprite_rect.size
        pygame.draw.rect(
            surface,
            [255,255,0],
            pygame.Rect([self.pos[0]-width, self.pos[1]-width], [w+width*2, h+width*2]),
            width)
        self.highlighted = True
    
    def distance_to(self, pos):
        x1, y1, x2, y2 = self.pos[0]+self.hw, self.pos[1]+self.hh, pos[0], pos[1]
        return ((x1-x2)**2 + (y1-y2)**2)**0.5

def draw_text_overlay(surface:pygame.Surface):
    for objects in current_frame.objects:
        if objects.text:
            surface.blit(objects.text, objects.pos)


sprites = {
    "head" : "debug_head.png",
    "torso" : "debug_torso.png",
    "left foot" : "debug_foot.png",
    "right foot" : "debug_foot.png",
    "left hand" : "debug_hand.png",
    "right hand" : "debug_hand.png"
}

#Store sprite, pos, rect
objects = {Sprite(sprites["torso"], [0,0], 0) : "torso",
           Sprite(sprites["head"], [200,0], 0) : "head",  
           Sprite(sprites["left foot"], [300,0], 0, text="LF") : "left foot", 
           Sprite(sprites["right foot"], [300,50], 0, text="RF") : "right foot", 
           Sprite(sprites["left hand"], [400, 0], 0, text="LH") : "left hand", 
           Sprite(sprites["right hand"], [400, 50], 0, text="RH") : "right hand"}


frames:list[Frame] = []
overlay = pygame.Surface(display.get_size(), pygame.SRCALPHA)
mode_name = pygame.Surface(display.get_size(), pygame.SRCALPHA)
show_first_frame = False
drag_sprite = None
displacement = None
rotating_sprite = None
rot_change = None
rot_start = None
render_text = True
num_skin_layers = 3
editing_frame_index = None

anim_playing = False
editing = False
sort_out_editing_fixes = False

mode_colors = {
    "animate" : [80, 170, 120],
    "edit" : [120, 80, 170],
    "play" : [170, 120, 80]
}

mode_color = mode_colors["animate"]

current_frame = Frame(pygame.Surface(display.get_size(), pygame.SRCALPHA), objects)

def create_frame():
    """Copies the current frame to the frame list.
    """
    global frames
    copy_frame = Frame.copy(current_frame)
    frames = [copy_frame] + frames

def onion_skin(surface:pygame.Surface, current_index=0):
    """Draws onion skin layers onto surface.
    """
    select_frames = frames[current_index:current_index+num_skin_layers]
    for i, frame in enumerate(select_frames):
        frame.draw(surface, 90-60*i/num_skin_layers)
    if show_first_frame and len(frames) > 0:
        frames[-1].draw(surface, 80)

def set_mode(mode_name):
    """Apply relevant variable changes for mode selection.
    Mode names include 'playing', 'editing' and 'animating'.
    """
    global anim_playing, editing, frame_num, mode_color, frames, editing_frame_index, fps, current_frame
    #If no longer editing
    if editing and mode_name != "editing":
        current_frame = frames[0]
        frames = frames[1:]
    if mode_name == "playing":
        anim_playing = True
        editing = False
        frame_num = len(frames)-1
        mode_color = mode_colors["play"]
        fps = 12
    elif mode_name == "editing":
        frames = [current_frame] + frames
        editing = True
        anim_playing = False
        mode_color = mode_colors["edit"]
        editing_frame_index = 0
        fps = 100
    elif mode_name == "animating":
        editing = False
        anim_playing = False
        mode_color = mode_colors["animate"]
        fps = 100
    else:
        raise ValueError (f"Mode name '{mode_name}' not recognised.")

def load_anim():
    """Validates user input for animation name, then loads this animation from the JSON file.
    """
    def load_sprites(anim_data:dict, frame_num:int):
        """Loads all sprite data for a specific frame."""
        objects = {}
        width, height = display.get_width()/2, display.get_height()/2
        for sprite_data in list(anim_data.items()):
            name, data = sprite_data
            frame_data = data[frame_num]
            relative_pos = frame_data["pos"]
            real_pos = relative_pos[0]*SCALE+width, relative_pos[1]*SCALE+height
            rotation = frame_data["rot"]
            objects.update({Sprite(sprites[name], real_pos, rotation):name})
        return objects

    global frames, current_frame
    print("\nWARNING:  LOADING A NEW ANIM NOW WILL ERASE THE CURRET ANIMATION IF NOT SAVED.")
    with open(filename, "r") as file:
        data = json.load(file)
    found = False
    while not found:
        anim_name = input("Enter the name of the anim to load or 'END' to end:  ")
        if anim_name not in data and anim_name != "END":
            print(f"anim name '{anim_name}' not found. Try again")
        elif anim_name == "END":
            print("Returning to current animation in 3 seconds.")
            time.sleep(3)
            make_display()
            return
        else:
            affirmed = False
            while not affirmed:
                affirmation = input(f"Are you sure you want to load '{anim_name}'? [y,n] If your current animation is unsaved, it will be erased.  ")
                if affirmation == "y":
                    make_display()
                    affirmed = True
                    frames = []
                    anim_data = data[anim_name]
                    frames = [Frame(pygame.Surface(display.get_size(), pygame.SRCALPHA), load_sprites(anim_data, i)) for i in range(len(list(anim_data.values())[0]))][::-1]
                    current_frame = frames[0]
                    frames = frames[1:]
                    print("Loaded new anim.")
                    return
                elif affirmation == "n":
                    affirmed = True
                else:
                    print("Input was neither 'y' or 'n'.")

                        
def get_rot(pos1, pos2):
    """Angle from pos1 to pos2.
    """
    centre = pygame.Vector2(pos1)
    return -math.degrees(math.atan2((centre.y-pos2[1]),(centre.x-pos2[0])))

def blit_frame_num(surface, color):
    if anim_playing:
        text = f"{len(frames)-frame_num}/{len(frames)+1}"
    elif editing:
        text = f"{len(frames)-editing_frame_index}/{len(frames)}"
    else:
        text = f"{len(frames)+1}/{len(frames)+1}"
    surface.blit(font.render(text, True, color), [0,0])

clock = pygame.time.Clock()
running = True
saving = False
fps = 100

#Mainloop
while running:
    #Get pressed keys
    keys = pygame.key.get_pressed()
    #Pop top item off stack after making editing fixes
    if sort_out_editing_fixes and not editing:
        current_frame = frames[0]
        frames = frames[1:]
    #USER INPUT
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            #End program
            if event.key == pygame.K_DELETE:
                running = False
            #Show/hide text
            elif event.key == pygame.K_s:
                render_text = not render_text
            #Create a frame (animating mode)
            elif event.key == pygame.K_RETURN and not editing and not anim_playing:
                create_frame()
            #Play animation/stop animation
            elif event.key == pygame.K_SPACE:
                if anim_playing:
                    set_mode("animating")
                else:
                    set_mode("playing")
            #Editing mode/exit editing mode
            elif event.key == pygame.K_TAB:
                if editing:
                    set_mode("animating")
                else:
                    set_mode("editing")
            #Complete rotation / rotate sprite
            elif event.key == pygame.K_r:
                if rotating_sprite:
                    rotating_sprite = None
                    rot_change = None
                    rot_start = None
                else:
                    possible_sprites = list(filter(lambda x: x.highlighted, current_frame.objects))
                    if possible_sprites != []:
                        rotating_sprite = possible_sprites[0]
                        rot_change = get_rot(rotating_sprite.get_rect().center, mouse_pos)
                        rot_start = rotating_sprite.rot
            #Cancel rotation
            elif event.key == pygame.K_ESCAPE and rotating_sprite:
                rotating_sprite.rot = rot_start
                current_frame.render()
                rotating_sprite = None
                rot_change = None
                rot_start = None
            #Reset rotation
            elif event.key == pygame.K_BACKSPACE and rotating_sprite:
                rotating_sprite.rot = 0
                current_frame.render()
                rotating_sprite = None
                rot_change = None
                rot_start = None
            #Go back 1 frame (edit mode)
            elif event.key == pygame.K_LEFT and editing:
                editing_frame_index = min(editing_frame_index+1, len(frames)-1)
                current_frame = frames[editing_frame_index]
            #Go forward 1 frame (edit mode)
            elif event.key == pygame.K_RIGHT and editing:
                editing_frame_index = max(editing_frame_index-1, 0)
                current_frame = frames[editing_frame_index]
            #Show first frame as a translucent overlay
            elif event.key == pygame.K_f and not anim_playing:
                show_first_frame = not show_first_frame
            #Change layer order
            elif event.key in [pygame.K_UP, pygame.K_DOWN] and pygame.K_LSHIFT not in keys: #############  <-------------------------
                possible_sprites = list(filter(lambda x: x.highlighted, current_frame.objects))
                if possible_sprites != []:
                    selected_sprite = possible_sprites[0]
                    pass
                    """Need to make it so that sprites are put in a specific order.
                    Then need to add to saving and loading to maintain this order in save data.
                    """
        #Start to drag sprite (if clicked on a sprite)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            possible_sprites = list(filter(lambda x: x.highlighted, current_frame.objects))
            if possible_sprites != []:
                drag_sprite = possible_sprites[0]
                sx,sy = drag_sprite.pos
                mx, my = mouse_pos
                displacement = [sx-mx, sy-my]
        #Stop dragging sprite
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            drag_sprite = None
            last_mouse_pos = None
        #Change onion skin amount
        elif event.type == pygame.MOUSEWHEEL or (event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_DOWN) and keys[pygame.K_LSHIFT]):
            if event.type == pygame.MOUSEWHEEL:
                difference = event.y
            else:
                difference = 1 if event.key == pygame.K_UP else -1
            num_skin_layers = min(len(frames) ,max(0, num_skin_layers+difference))

    if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
        running = False
        saving = True
        continue
    elif keys[pygame.K_LCTRL] and keys[pygame.K_l]:
        pygame.display.quit()
        load_anim()
        set_mode("animating")
        continue

    if anim_playing and len(frames) != 0:
        display.fill(mode_color)
        frames[frame_num].draw(display)
        frame_num = (frame_num - 1) % len(frames)

    else:
        display.fill(mode_color)
        overlay.fill(0)

        mouse_pos = pygame.mouse.get_pos()
        #Drag object if mouse button is being held down
        if drag_sprite:
            drag_sprite.pos = [mouse_pos[0]+displacement[0], mouse_pos[1]+displacement[1]]
            current_frame.render()
        #Undo last rotation, then find angle between object and mouse_po
        elif rotating_sprite:
            rotating_sprite.rot -= rot_change
            rot_change = get_rot(rotating_sprite.get_rect().center, mouse_pos)
            rotating_sprite.rot += rot_change
            current_frame.render()
        #Highlight
        shortest_distance = 10000
        closest = None
        current_frame.draw(display)
        for sprite in current_frame.objects:
            sprite.highlighted = False
            dist_to_mouse = sprite.distance_to(mouse_pos)
            if dist_to_mouse < shortest_distance or closest == None:
                shortest_distance = dist_to_mouse
                closest = sprite
        if closest.get_rect().collidepoint(mouse_pos):
            closest.draw_highlight(overlay, int(SCALE/2))

        #Onion skinning
        if editing:
            onion_skin(display, editing_frame_index)
        else:
            onion_skin(display)
        #Overlay
        if render_text:
            draw_text_overlay(overlay)
        display.blit(overlay, [0,0])
    
    blit_frame_num(display, "white")    
    clock.tick(fps)
    pygame.display.update()

###### SAVE DATA
pygame.display.quit()

if saving:
    if frames[0] != current_frame:
        frames = [current_frame] + frames
    #Format frame data (ie lists of sprite data) into full anim data
    save_data = {}
    for i, frame in enumerate(frames):
        torso = list(frame.objects.keys())[list(frame.objects.values()).index("torso")]
        for objects in frame.objects.items():
            obj_data = {
                "pos" : [(objects[0].pos[0]-torso.pos[0])/SCALE, (objects[0].pos[1]-torso.pos[1])/SCALE],
                "rot" : objects[0].rot
            }
            if objects[1] in save_data:
                save_data[objects[1]].append(obj_data)
            else:
                save_data.update({objects[1]:[obj_data]})
    #Reverse the list to put it in 'correct' order (first frame listed = first frame of animation)
    for obj_name in list(save_data.keys()):
        save_data[obj_name] = save_data[obj_name][::-1]


    try:
        with open(filename, "r") as file:
            data = json.load(file)
    except:
        data = {}

    #Ask uder for animation name
    found = False
    while not found:
        anim_name = input("Name of animation: ")
        affirmed = False
        while not affirmed:
            affirmation = input(f"Are you sure you want to name it '{anim_name}'? [y,n] ").lower()
            if affirmation == "y":
                affirmed = True
                if anim_name in data:
                    affirmation = input(f"There already exists an animation named '{anim_name}'. Enter 'y' to override and save.").lower()
                    if affirmation == "y":
                        data.pop(anim_name)
                        found = True
                else:
                    found = True
            elif affirmation == "n":
                affirmed = True
                found = False
            else:
                print(f"Input must be 'y' or 'n', not {affirmation}.")

    #Ask user for modules to not save
    removed = []
    for obj in save_data:
        valid = False
        while not valid:
            keep = input(f"Do you want to save data for {obj} [y,n]?  ").lower()
            if keep == "y":
                valid = True
            elif keep == "n":
                removed.append(obj)
                valid = True
            else:
                print("Input must be 'y' or 'n'.")

    #Removes unwanted modules from save data
    [save_data.pop(obj) for obj in removed]
    save_data = {anim_name:save_data}

    #Add new data to old data
    data.update(save_data)
    save_data = data

    #Save data to file
    with open(filename, "w") as file:
        custom_dump(save_data, file)


"""NEED TO IMPLEMENT ORDER OF ITEMS, SUCH THAT THE USER CAN PICK WHICH ITEM GOES ON TOP.
This will make for better rendering that makes physical sense (e.g. one hand is not rendered in front of another).
You should at this point also make a weapon object, or allow for a weapon object. The user should specify the name of the object, as well as supplying an image file.
You may want to implement weapon snapping, so the user can specify which limb the weapon should snap to to make animation easier.
You could, at some point, make extra anim objects like smear frames but this should be a final touch.

Possibility for other helpful changes such as objects retaining motion through frames, but would be hard to implement now.
Need to update documentation (include the two other variants of this code if useful).
Implement this animation system into the rest of the game:
 - have the animations referenced wherever necessary in weapon files, but also specified somewhere else for constant anims e.g. walking
"""