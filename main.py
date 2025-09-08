from map import Map, Room
from player import Player
from renderer import Renderer
from enemy import Enemy
import json
import time

from hitbox import *

class Game:
    def __init__(self):
        self.map = Map(5)
        self.current_pos = [self.map.center[0], self.map.center[1]]
        print(self.current_pos)
        self.renderer = Renderer([16*102, 9*102])
        #Temporary section to set player's position to within the room
        self.test_run()
        self.player = Player([0,0])
        curr_room = self.map.rooms[self.current_pos[0]][self.current_pos[1]]
        door = curr_room.door_interactors[0]
        door_rect = door.rect
        x,y = door_rect.center
        direction = curr_room.door_interactors.index(door)
        match direction:
            case 0:
                pos = [door_rect.right-self.player.collider.hdim[0], y]
            case 1:
                pos = [x, door_rect.top+self.player.collider.hdim[1]]
            case 2:
                pos = [door_rect.left+self.player.collider.hdim[0], y]
            case 3:
                pos = [x, door_rect.bottom-self.player.collider.hdim[1]]
        self.player.update_position(pos)
    def solve_interaction(self, player:Player, interactor:Interactor):
        if type(interactor) == DoorInteractor:
            #Change room
            self.current_pos, curr_room, new_door = self.map.move_room(self.current_pos, interactor, 100,100)
            g.renderer.debug_render_room(curr_room.wall_colliders, curr_room.door_interactors)
            #Snap player to door
            door_rect = new_door.rect
            x,y = door_rect.center
            direction = curr_room.door_interactors.index(new_door)
            match direction:
                case 0:
                    player.update_position([door_rect.right-player.collider.hdim[0], y])
                case 1:
                    player.update_position([x, door_rect.top+player.collider.hdim[1]])
                case 2:
                    player.update_position([door_rect.left+player.collider.hdim[0], y])
                case 3:
                    player.update_position([x, door_rect.bottom-player.collider.hdim[1]])
            
    def test_run(self) -> Room:
        r = self.map.load_room(self.current_pos, 100, 100)
        self.renderer.debug_render_room(r.wall_colliders, r.door_interactors)
        return r

g = Game()

#Allow behaviour tree to access game object
import behaviour_tree
behaviour_tree.GAME = g

def get_player():
    return g.player

with open("C:/Users/james/Documents/Python/NEA/controls.json", "r") as file:
    controls = json.load(file)

last_update = time.time()
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key ==  controls["down"]:
                g.player.add_to_motion_vector([0,1])
            elif event.key == controls["up"]:
                g.player.add_to_motion_vector([0,-1])
            elif event.key == controls["right"]:
                g.player.add_to_motion_vector([1,0])
            elif event.key == controls["left"]:
                g.player.add_to_motion_vector([-1,0])
        elif event.type == pygame.KEYUP:
            if event.key == controls["down"]:
                g.player.add_to_motion_vector([0,-1])
            elif event.key == controls["up"]:
                g.player.add_to_motion_vector([0,1])
            elif event.key == controls["right"]:
                g.player.add_to_motion_vector([-1,0])
            elif event.key == controls["left"]:
                g.player.add_to_motion_vector([1,0])
            elif event.key == controls["interact"]:
                if g.player.interactor.closest_interactor:
                    g.solve_interaction(g.player, g.player.interactor.closest_interactor) #############Deal with this somehow (door has no input on what should happen, this is map level)
                                                               #############Could involve a main method in game that solves interactions, where it actually just gets the class
                                                               #############of the interactor, no interact() method required. It is then solved by the main game since
                                                               #############solving the interaction is not an Interactor level process.
    
    g.player.move()
    Enemy.behave_all()

    Enemy.update_all()    
    
    g.renderer.debug_render_frame(g.player.collider, g.player.interactor)
    
    clock.tick(100)
    pygame.display.set_caption(str(round(clock.get_fps())))