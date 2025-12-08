import pygame

class Hitbox:
    def __init__(self, pos, dim):
        self.dim = pygame.Vector2(dim)
        self.rect = pygame.Rect(pos, self.dim)
        self.hdim = self.dim/2
        #from random import randint #################################################################<-debug lines
        #self.c = [randint(100,255),randint(100,255),randint(100,255)] ##############################<-
    @staticmethod
    def get_distance(pos1, pos2):
        return ((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)**0.5

class Collider(Hitbox):
    all:list["Collider"] = []

class Interactor(Hitbox):
    all:list["Interactor"] = []

class HittingBox(Hitbox):
    all:list["HittingBox"] = []

class WallCollider(Collider):
    pass

class EntityCollider(Collider):
    def move_and_collide(self, motion_vector):
        """Moves collider considering collisions.
        Returns the new collider center."""
        #Resolve collisions due to x component of motion_vector
        self.rect.centerx += motion_vector.x
        #Get all colliding colliders due to x component of motion_vector
        x_collisions = self.rect.collideobjectsall(Collider.all, key=lambda c: c.rect)
        if x_collisions:
            if motion_vector.x > 0: #Travelling right
                #Snap to left-most collider side
                nearest_collider = min(x_collisions, key=lambda c: c.rect.left)
                self.rect.centerx = nearest_collider.rect.left - self.hdim.x
            else: #Travelling left
                #Snap to right-most collider side
                nearest_collider = max(x_collisions, key=lambda c: c.rect.right)
                self.rect.centerx = nearest_collider.rect.right + self.hdim.x

        #Resolve collisions due to y component of motion_vector
        self.rect.centery += motion_vector.y
        #Get all colliding colliders due to y component of motion_vector
        y_collisions = self.rect.collideobjectsall(Collider.all, key=lambda c: c.rect)
        if y_collisions:
            if motion_vector.y > 0: #Travelling down
                #Snap to up-most collider side
                nearest_collider = min(y_collisions, key=lambda c: c.rect.top)
                self.rect.centery = nearest_collider.rect.top - self.hdim.y
            else: #Travelling up
                #Snap to down-most collider side
                nearest_collider = max(y_collisions, key=lambda c: c.rect.bottom)
                self.rect.centery = nearest_collider.rect.bottom + self.hdim.y

        return self.rect.center

class DoorInteractor(Interactor):
    def __init__(self, pos, long_dim, short_dim, wall):
        """
        Arguments:
            pos : [x,y] topleft position of the door interactor
            long_dim : the [w,h] lengths of the potential long edges
            short_dim : the [w,h] lengths of the potential short edges
            wall : integer 0-3 denoting the wall direction it is on (right, up, left, down)
        """
        match wall:
            case 0:
                super().__init__([pos[0]+long_dim[0]-short_dim[0], pos[1]], [short_dim[0], long_dim[1]])
            case 1:
                super().__init__(pos, [long_dim[0], short_dim[1]])
            case 2:
                super().__init__(pos, [short_dim[0], long_dim[1]])
            case 3:
                super().__init__([pos[0], pos[1]+long_dim[1]-short_dim[1]], [long_dim[0], short_dim[1]])
            case _:
                raise ValueError (f"wall passed to DoorInteractor initialisation {wall} is not an integer 0<=wall<=3")

class PlayerInteractor(Interactor):
    def __init__(self, pos, dim):
        super().__init__(pos, dim)
        self.closest_interactor = None
    def get_closest_interactor(self):
        """Finds the closest Interactor object in range.
        Sets the closest_interactor object and returns this.
        If there is no interactor in range, the function returns None."""
        closest_interactor = None
        shortest_distance = -1
        for interactor in self.rect.collideobjectsall(Interactor.all, key=lambda i: i.rect):
            distance = Hitbox.get_distance(self.rect.center, interactor.rect.center)
            if distance < shortest_distance or shortest_distance==-1:
                closest_interactor = interactor
                shortest_distance = distance
        self.closest_interactor = closest_interactor
        return self.closest_interactor