from hitbox import *

class Entity:
    sub_motion = 3
    def __init__(self, pos):
        self.collider = EntityCollider(pos, [50,50])

        self.direction = True

        self.__unscaled_motion_vector = pygame.Vector2()
        self.__sub_motion_vector = pygame.Vector2()
    
    def update_position(self, new_pos):
        """Sets the position of the player.
        """
        self.collider.rect.center = new_pos

    def move(self, speed):
        """Moves collider.
        Returns the new rect center position
        """
        #Will only do movement checks if actually moving
        if self.__sub_motion_vector != [0,0]:
            remainder_motion_size = speed % Entity.sub_motion
            remainder_vector = self.__sub_motion_vector.copy()
            remainder_vector.scale_to_length(remainder_motion_size)

            num_sub_motions = int(speed / Entity.sub_motion)
            for _ in range(num_sub_motions):
                self.collider.move_and_collide(self.__sub_motion_vector)

            return self.collider.move_and_collide(remainder_vector)
        return self.collider.rect.center

    def update_direction(self):
        if self.__sub_motion_vector.x < 0:
            self.direction = False
        elif self.__sub_motion_vector.x > 0:
            self.direction = True

    def add_to_motion_vector(self, adding_vector:list):
        """Adds adding_vector to this entity's __motion_vector, and then bounds it to a certain length."""
        self.__unscaled_motion_vector += adding_vector
        self.__sub_motion_vector = self.__unscaled_motion_vector.copy()
        if self.__unscaled_motion_vector != [0,0]:
            self.__sub_motion_vector.scale_to_length(Entity.sub_motion)
        self.update_direction()
    
    def update_motion_vector(self, new_vector:list):
        """Assigns new_vector to this entity's motion_vector."""
        self.__unscaled_motion_vector = pygame.Vector2(new_vector)
        self.__sub_motion_vector = self.__unscaled_motion_vector.copy()
        if self.__unscaled_motion_vector != [0,0]:
            self.__sub_motion_vector.scale_to_length(Entity.sub_motion)
        self.update_direction()
    
    def get_sub_motion_vector(self):
        return self.__sub_motion_vector