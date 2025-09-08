from typing import Tuple, List, Optional, Union
from random import choices, choice, randint, uniform

from hitbox import *
from enemy import Enemy

class Map:
    room_neighbor_vectors = [[1,0], [0,-1], [-1,0], [0,1]]
    def __init__(self, size:int, center:Tuple[int, int]=None):
        if center == None:
            self.center = [size//2, size//2]
        else:
            self.center = center
        self.size = size
        self.rooms: List[List[Optional[Room]]] = [[None for _ in range(size)] for _ in range(size)]
        #self.rooms[self.center[0]][self.center[1]] = StaircaseRoom(center, self.center, self.size)

    def create_room(self, position:Tuple[int, int], x_scale, y_scale):
        print("Neighbors:")
        print([[position[0]+v[0],position[1]+v[1]]
                for v in Map.room_neighbor_vectors
                if (0 <= position[0]+v[0] < self.size
                    and 0 <= position[1]+v[1] < self.size)])
        new_room = Room(position, self.center, self.size, [self.rooms[position[0]+v[0]][position[1]+v[1]]
                                                            if (0 <= position[0]+v[0] < self.size
                                                                and 0 <= position[1]+v[1] < self.size)
                                                            else Room.edge_string
                                                            for v in Map.room_neighbor_vectors])
        new_room.generate_grid([16,9],[4,4])  ############################################################################    MAGIC NUMBERS (should change with self.size [which relates to the level])
        new_room.generate_doors()
        new_room.generate_hitboxes(x_scale, y_scale)
        new_room.generate_enemies(x_scale, y_scale)###################################
        self.rooms[position[0]][position[1]] = new_room
        print("Rooms:")
        for j in range(self.size):
            for i in range(self.size):
                print("|R" if isinstance(self.rooms[i][j], Room) else "| ", end="")
            print("|")
        print()
    
    def load_room(self, position:Tuple[int, int], x_scale, y_scale):
        """Creates the room at position if it has not been generated.
        If the room has been generated, it is loaded in and returned."""
        x,y = position
        if not isinstance(self.rooms[x][y], Room):
            self.create_room(position, x_scale, y_scale)
        room = self.rooms[x][y]
        Collider.all = room.wall_colliders.copy()
        Interactor.all = [d_int for d_int in room.door_interactors if d_int != None]
        Enemy.all = room.enemies.copy()############################################################################

        return room
    
    def move_room(self, position:Tuple[int, int], door_interactor:DoorInteractor, x_scale, y_scale):
        """Finds the next room over as if travelling through the passed DoorInteractor.
        Will create the room if not already generated.
        Returns the new room index [x,y], the new Room object as well as the arrived-at DoorInteractor."""
        x,y = position
        room = self.rooms[x][y]
        door_interactor_index = room.door_interactors.index(door_interactor)
        relative_pos = Map.room_neighbor_vectors[door_interactor_index]
        new_pos = [x+relative_pos[0], y+relative_pos[1]]
        new_room = self.load_room(new_pos, x_scale, y_scale)
        return new_pos, new_room, new_room.door_interactors[(door_interactor_index+2)%4]


class Room:
    cell_neighbor_vectors = [[1,0], [0,-1], [-1,0], [0,1]]
    edge_string = "EDGE"
    def __init__(self, pos:Tuple[int, int], map_center:Tuple[int,int], map_size:int, neighbor_rooms:Tuple[Union["Room",str,None], Union["Room",str,None], Union["Room",str,None], Union["Room",str,None]]=None):
        if neighbor_rooms == None:
            self.doors = [True, True, True, True]
        else:
            #Generate the max number of doors
            try:
                distance_to_center = (((pos[0]-map_center[0])**2+(pos[1]-map_center[1])**2)**0.5)*10/map_size
                weights = [max(0.05*distance_to_center**5,5),4*distance_to_center,50/distance_to_center,100/distance_to_center**3]
                random_num_doors = choices(range(1,5), weights, k=1)[0]
            except:
                self.doors = [True, True, True, True]
                return
            #[no comparison needed for next two list comprehensions since doors are signified by bools]
            #Find the required number of doors (given the neighboring rooms)
            required_doors = [n.doors[(i+2)%4] != None
                              if isinstance(n, Room)
                              else False
                              for i, n in enumerate(neighbor_rooms)]
            #Find which walls cannot have doors (given the neighbouring rooms or if at the border of the map)
            absent_doors = [n.doors[(i+2)%4] == None
                              if isinstance(n, Room)
                              else n == Room.edge_string
                              for i, n in enumerate(neighbor_rooms)]
            #Take minimum of (maximum of req and random) and absent to get the true number of doors
            num_doors = min(max(random_num_doors, required_doors.count(True)), 4-absent_doors.count(True))

            #Create required doors:
            self.doors = []
            available_doors = []
            for i, door in enumerate(required_doors):
                if door: #If a room connects to this one
                    self.doors.append(True)
                    num_doors -= 1
                else:
                    self.doors.append(False)
                    if not absent_doors[i]: #If the related room can connect and is empty
                        available_doors.append(i)
            
            #Create extra doors:
            while len(available_doors) and num_doors:
                i = choice(available_doors)
                self.doors[i] = True
                available_doors.remove(i)
                num_doors -= 1
        
            print(["|D|" if d else "| |" for d in self.doors], random_num_doors, required_doors, absent_doors)
    
    @staticmethod
    def get_neighbors(grid_size_x, grid_size_y, x, y):
        """Returns all neighbor cells (non-diagonal) within grid bounds"""
        #if statement to keep index within the grid:
        return [[x+r[0], y+r[1]] for r in Room.cell_neighbor_vectors 
                if 0 <= x+r[0] < grid_size_x
                    and 0 <= y+r[1] < grid_size_y]

    @staticmethod
    def get_empty_neighbors(grid, grid_size_x, grid_size_y, x, y):
        """Returns all non-room neighbor cells (non-diagonal) within grid bounds"""
        neighbors = Room.get_neighbors(grid_size_x, grid_size_y, x, y)
        return [n for n in neighbors if not grid[n[0]][n[1]]]
    
    @staticmethod
    def is_within_extra_boundary(grid_size_x, grid_size_y, x, y):
        """Returns True if the [x,y] coordinate is within the extra boundary.
        The extra boundary is 1 cell smaller on each side of the grid than the grid size."""
        return 0 < x < grid_size_x-1 and 0 < y < grid_size_y-1

    def generate_grid(self, grid_size = [10,10], min_room_size = [4,4]):
        grid_size_x, grid_size_y = grid_size
        min_width, min_height = min_room_size
        grid = [[False for _ in range(grid_size_y)] for _ in range(grid_size_x)]
        top_left = [randint(1, grid_size_x-2-min_width), randint(1, grid_size_y-2-min_height)]
        width = randint(min_width, grid_size_x-2-top_left[0])
        height = randint(min_height, grid_size_y-2-top_left[1])
        bottom_right = [top_left[0]+width, top_left[1]+height]
        #Set values in grid to True if within the rectangle defined above
        for i in range(grid_size_x):
            if top_left[0] <= i < bottom_right[0]:
                for j in range(grid_size_y):
                    if top_left[1] <= j < bottom_right[1]:
                        grid[i][j] = True

        #Add extra cells to the room
        extra_cells_num = (grid_size[0]*grid_size[1]-width*height)//16
        if extra_cells_num != 0:            
            #Find empty cells that connect to the live cells (walls that connect to the room cells)
            expandable_cells = []
            for i in range(grid_size_x):
                for j in range(grid_size_y):
                    if grid[i][j]:
                        empty_neighbors = Room.get_empty_neighbors(grid, grid_size_x, grid_size_y, i, j)
                        #Keep the live cell options at least 1 cell away from the boundary
                        empty_neighbors = [n for n in empty_neighbors if (Room.is_within_extra_boundary(grid_size_x, grid_size_y, n[0], n[1])
                                                                          and n not in expandable_cells)]
                        expandable_cells += empty_neighbors

            #Add extra_cells_num of these cells to the room
            while extra_cells_num > 0 and len(expandable_cells) > 0:
                new_cell = choice(expandable_cells)
                grid[new_cell[0]][new_cell[1]] = True
                expandable_cells.remove(new_cell)
                extra_cells_num -= 1
                #Check new neighbors if they have expandable cells
                for neighbor in Room.get_empty_neighbors(grid, grid_size_x, grid_size_y, new_cell[0], new_cell[1]):
                    #If the neighbor wall cell is now expandable (connected to the main room)
                    if (Room.is_within_extra_boundary(grid_size_x, grid_size_y, neighbor[0], neighbor[1])
                        and neighbor not in expandable_cells):
                        expandable_cells.append(neighbor)

        self.grid = grid
        self.grid_size_x = grid_size_x
        self.grid_size_y = grid_size_y
        self.grid_size = [self.grid_size_x, self.grid_size_y]

#######################################################################################
        for r in range(grid_size_y):
            for column in grid:
                print(f"\033[93m◼\033[0m" if column[r] else "◼", end="  ")
            print()
        print(f"Width: {width}\tHeight: {height}\tTop-left: {top_left}")

    def generate_doors(self):
        """Picks live cells to put the room's doors in. Doors will not generate in the same cell."""

        doors = [None, None, None, None]

        if self.doors[1]: #Up
            door_options = [[i, column.index(True)] 
                            for i, column in enumerate(self.grid) 
                            if True in column]
            doors[1] = choice(door_options)
        
        if self.doors[3]: #Down
            door_options = [[i, self.grid_size_y-1-column[::-1].index(True)]
                            for i, column in enumerate(self.grid) 
                            if True in column and [i, self.grid_size_y-1-column[::-1].index(True)] not in doors]
            doors[3] = choice(door_options)
        
        #Transpose grid to more easily check left and right door in rows
        transposed_grid = [list(x) for x in zip(*self.grid)]

        if self.doors[2]: #Left
            door_options = [[row.index(True), i]
                            for i, row in enumerate(transposed_grid) 
                            if True in row and [row.index(True), i] not in doors]
            doors[2] = choice(door_options)
        
        if self.doors[0]: #Right
            door_options = [[self.grid_size_x-1-row[::-1].index(True), i] 
                            for i, row in enumerate(transposed_grid) 
                            if True in row and [self.grid_size_x-1-row[::-1].index(True), i] not in doors]
            doors[0] = choice(door_options)

        self.doors = doors
        print(self.doors)


    #Method for generating colliders that merges colliders together if adjacent
    #Removed since it seemed unnecessary
    #May be implemented and tested later if framerate issues pop up
    """
    def generate_colliders(self, graphical_size:Tuple[int|float, int|float]):
        self.wall_colliders = []
        x_scale = graphical_size[0]/self.grid_size_x
        y_scale = graphical_size[1]/self.grid_size_y
        #Generate information for the colliders:
        for i in range(self.grid_size_x):
            self.wall_colliders.append([])
            for j in range(self.grid_size_y):
                #Will not generate wall colliders if the wall is unreachable (ie it is surrounded by walls)
                if not self.grid[i][j] and Room.get_empty_neighbors(self.grid, self.grid_size_x, self.grid_size_y, i, j) != Room.get_neighbors(self.grid_size_x, self.grid_size_y, i,j):
                    self.wall_colliders[i].append([[i*x_scale, j*y_scale], [x_scale, y_scale]])
                else:
                    self.wall_colliders[i].append(None)
        
        #Merge wall colliders together if horizontally connected
        #Merge vertically:
        for column in self.wall_colliders:
            for i in range(len(column)-1, 0, -1):
                if column[i-1] != None and column[i] != None:
                    if column[i-1][0][0] == column[i][0][0] and column[i-1][0][1] == column[i][0][1]-y_scale:
                        column[i-1][1][1] += column[i][1][1]
                        column[i] = None
        #Swap rows and columns:
        self.wall_colliders = [list(x) for x in zip(*self.wall_colliders)]
        #Merge horizontally:
        for row in self.wall_colliders:
            for i in range(len(row)-1, 0, -1):
                if row[i-1] != None and row[i] != None:
                    if row[i-1][0][1] == row[i][0][1] and row[i-1][0][0] == row[i][0][0]-x_scale and row[i-1][1][1] == row[i][1][1]:
                        row[i-1][1][0] += row[i][1][0]
                        del row[i]
    
        new_colliders = []
        for column in self.wall_colliders:
            for i, w in enumerate(column):
                if w != None:
                    new_colliders.append(WallCollider(w[0], w[1]))
        
        self.wall_colliders = new_colliders
    """
    def generate_wall_colliders(self, x_scale, y_scale):
        self.wall_colliders = []
        for i in range(self.grid_size_x):
            for j in range(self.grid_size_y):
                #Will not generate wall colliders if the wall is unreachable (ie it is surrounded by walls) to limit collider checks to only necessary rooms
                if not self.grid[i][j] and Room.get_empty_neighbors(self.grid, self.grid_size_x, self.grid_size_y, i, j) != Room.get_neighbors(self.grid_size_x, self.grid_size_y, i,j):
                    self.wall_colliders.append(WallCollider([i*x_scale, j*y_scale], [x_scale, y_scale]))
    
    def generate_door_interactors(self, x_scale, y_scale):
        self.door_interactors = [DoorInteractor([door[0]*x_scale, door[1]*y_scale], [x_scale, y_scale], [x_scale/3, y_scale/3], i) if door != None else None for i,door in enumerate(self.doors)]

    def generate_hitboxes(self, x_scale, y_scale):
        self.generate_wall_colliders(x_scale, y_scale)
        self.generate_door_interactors(x_scale, y_scale)
    
    def generate_enemies(self, x_scale, y_scale): ###############MUST BE CHANGED TO ALLOW FOR LEVEL SCALING AND SUCH
        self.enemies = []
        for i in range(self.grid_size_x):
            for j in range(self.grid_size_y):
                if self.grid[i][j]:
                    if randint(1,20) == 1:
                        self.enemies.append(Enemy("e1", [i*x_scale, j*y_scale]))


class StaircaseRoom(Room):
    pass