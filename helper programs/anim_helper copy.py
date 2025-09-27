import pygame
import os
import json
from copy import copy
pygame.display.init()
pygame.font.init()
font = pygame.font.SysFont("consolas", 20)

#Borderless fullscreen
display = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0], pygame.NOFRAME)

SCALE = 10
num_skin_layers = 3

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
    def __init__(self, img_name, pos, text=None):
        self.img = pygame.transform.scale_by(pygame.image.load("sprites/"+img_name), SCALE)
        self.pos = pos
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
        surface.blit(self.img, self.pos)
    
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
            

#Store sprite, pos, rect
objects = {Sprite("debug_head.png", [0,0]) : "head", 
           Sprite("debug_torso.png", [100,0]) : "torso", 
           Sprite("debug_foot.png", [300,0], text="LF") : "left foot", 
           Sprite("debug_foot.png", [300,50], text="RF") : "right foot", 
           Sprite("debug_hand.png", [400, 0], text="LH") : "left hand", 
           Sprite("debug_hand.png", [400, 50], text="RH") : "right hand"}


frames:list[Frame] = []
overlay = pygame.Surface(display.get_size(), pygame.SRCALPHA)
mode_name = pygame.Surface(display.get_size(), pygame.SRCALPHA)
drag_sprite = None
displacement = None
render_text = True
num_skin_layers = 1
editing_frame_index = None

anim_playing = False
editing = False
sort_out_editing_fixes = False

mode_colors = {
    "animate" : [60, 150, 200],
    "edit" : [250, 130, 150],
    "play" : [240, 120, 240]
}

mode_color = mode_colors["animate"]

current_frame:Frame = Frame(pygame.Surface(display.get_size(), pygame.SRCALPHA), objects)

def create_frame():
    global frames, current_frame
    if current_frame:
        old_frame = current_frame
        frames = [old_frame] + frames
    current_frame = Frame.copy(old_frame)

def onion_skin(surface:pygame.Surface, current_index=0):
    select_frames = frames[current_index:current_index+num_skin_layers]
    for i, frame in enumerate(select_frames):
        frame.draw(surface, 90-60*i/num_skin_layers)


clock = pygame.time.Clock()
running = True
#Mainloop
while running:
    if sort_out_editing_fixes and not editing:
        current_frame = frames[0]
        frames = frames[1:]
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                running = False
            elif event.key == pygame.K_s:
                render_text = not render_text
            elif event.key == pygame.K_RETURN and not editing and not anim_playing:
                create_frame()
            elif event.key == pygame.K_SPACE:
                if anim_playing:
                    anim_playing = False
                    editing = False
                    mode_color = mode_colors["animate"]
                else:
                    anim_playing = True
                    editing = False
                    frame_num = len(frames)-1
                    mode_color = mode_colors["play"]
            elif event.key == pygame.K_TAB:
                if editing:
                    editing = False
                    anim_playing = False
                    mode_color = mode_colors["animate"]
                else:
                    frames = [current_frame] + frames
                    editing = True
                    anim_playing = False
                    mode_color = mode_colors["edit"]
                    editing_frame_index = 0
            elif event.key == pygame.K_LEFT and editing:
                editing_frame_index = min(editing_frame_index+1, len(frames)-1)
                current_frame = frames[editing_frame_index]
            elif event.key == pygame.K_RIGHT and editing:
                editing_frame_index = max(editing_frame_index-1, 0)
                current_frame = frames[editing_frame_index]
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            possible_sprites = list(filter(lambda x: x.highlighted, current_frame.objects))
            if possible_sprites != []:
                drag_sprite = possible_sprites[0]
                sx,sy = drag_sprite.pos
                mx, my = mouse_pos
                displacement = [sx-mx, sy-my]
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            drag_sprite = None
            last_mouse_pos = None
        if event.type == pygame.MOUSEWHEEL or (event.type == pygame.KEYDOWN and (event.key == pygame.K_UP or event.key == pygame.K_DOWN)):
            if event.type == pygame.MOUSEWHEEL:
                difference = event.y
            else:
                difference = 1 if event.key == pygame.K_UP else -1
            num_skin_layers = min(len(frames) ,max(0, num_skin_layers+difference))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LCTRL] and keys[pygame.K_s]:
        running = False
        continue

    if anim_playing and len(frames) != 0:
        display.fill(mode_color)
        frames[frame_num].draw(display)
        frame_num = (frame_num - 1) % len(frames)
        clock.tick(12)

    else:
        display.fill(mode_color)
        overlay.fill(0)

        mouse_pos = pygame.mouse.get_pos()        
        if drag_sprite:
            drag_sprite.pos = [mouse_pos[0]+displacement[0], mouse_pos[1]+displacement[1]]
            current_frame.render()
        
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

        if editing:
            onion_skin(display, editing_frame_index)
        else:
            onion_skin(display)
        if render_text:
            draw_text_overlay(overlay)
        display.blit(overlay, [0,0])
        clock.tick(100)
    pygame.display.update()

###### SAVE DATA

if frames[0] != current_frame:
    frames = [current_frame] + frames

pygame.display.quit()

save_data = []
for i, frame in enumerate(frames):
    frame_data = {}
    torso = list(frame.objects.keys())[list(frame.objects.values()).index("torso")]
    for objects in frame.objects.items():
        obj_data = {objects[1]: {
            "pos" : [(objects[0].pos[0]-torso.pos[0])/SCALE, (objects[0].pos[1]-torso.pos[1])/SCALE]
        }}
        frame_data.update(obj_data)
    save_data.append(frame_data)

##### MAKE IT NOT INDENT THE FINAL LAYERS OF THE DATA TO SHORTEN THE FILE DOWN A BIT

found = False
while not found:
    anim_name = input("Name of animation: ")
    affirmed = False
    while not affirmed:
        affirmation = input(f"Are you sure you want to name it '{anim_name}'? [y,n] ").lower()
        if affirmation == "y":
            affirmed = True
            found = True
        elif affirmation == "n":
            affirmed = True
            found = False
        else:
            print(f"Input must be 'y' or 'n', not {affirmation}.")

save_data = {anim_name:save_data}

dir = os.path.dirname(os.path.abspath(__file__))

try:
    with open(os.path.join(dir, "anim_data.json"), "r") as file:
        data = json.load(file)
        data.update(save_data)
        save_data = data
except:
    pass
with open(os.path.join(dir, "anim_data.json"), "w") as file:
    json.dump(save_data, file, indent=4)
"""Need to allow user to edit frames. Use left and right arrow keys to change frame.
Will likely need to create a frame class that stores copies of the original images. This may make it better for blitting onion skins, since only the images need to be blitted.
Need to allow for rotation.
Need to allow for saving and loading of animations.
"""