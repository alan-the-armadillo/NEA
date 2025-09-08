import pygame

class CollisionHitbox:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x-w/2, y-h/2, w, h)
        self.pos = pygame.Vector2(x,y)
        self.dim = pygame.Vector2(w,h)
        self.hdim = self.dim/2

    def draw(self, surface):
        pygame.draw.rect(surface, "white", self.rect)

class WallCollider(CollisionHitbox):
    all = []
    def __init__(self, x, y, w, h, c):
        WallCollider.all.append(self)
        super().__init__(x, y, w, h, )

class PlayerCollider(CollisionHitbox):
    def __init__(self, x, y, w, h, c):
        super().__init__(x, y, w, h, )
        self.movement_vector = pygame.Vector2(0,0)
    
    def move_and_collide(self):
        #Skip all calculations if the player is not moving
        if self.movement_vector.magnitude() == 0:
            return
        
        #Scale vector to player speed
        new_v = self.movement_vector.copy()
        new_v.scale_to_length(speed)

        #Resolve collisions due to x component of new_v
        self.pos.x += new_v.x
        self.rect.centerx = self.pos.x
        #Get all colliding walls due to x component of new_v
        x_collisions = self.rect.collideobjectsall(WallCollider.all, key=lambda w: w.rect)
        if x_collisions:
            if new_v.x > 0: #Travelling right
                #Snap to left-most wall side
                nearest_wall = min(x_collisions, key=lambda w: w.rect.left)
                self.pos.x = nearest_wall.rect.left - self.hdim.x
            elif new_v.x < 0: #Travelling left
                #Snap to right-most wall side
                nearest_wall = max(x_collisions, key=lambda w: w.rect.right)
                self.pos.x = nearest_wall.rect.right + self.hdim.x
            #Update x location
            self.rect.centerx = self.pos.x

        #Resolve collisions due to y component of new_v
        self.pos.y += new_v.y
        self.rect.centery = self.pos.y
        #Get all colliding walls due to y component of new_v
        y_collisions = self.rect.collideobjectsall(WallCollider.all, key=lambda w: w.rect)
        if y_collisions:
            if new_v.y > 0: #Travelling down
                #Snap to up-most wall side
                nearest_wall = min(y_collisions, key=lambda w: w.rect.top)
                self.pos.y = nearest_wall.rect.top - self.hdim.y
            elif new_v.y < 0: #Travelling up
                nearest_wall = max(y_collisions, key=lambda w: w.rect.bottom)
                self.pos.y = nearest_wall.rect.bottom + self.hdim.y
            #Update y location
            self.rect.centery = self.pos.y

    def update(self):
        self.move_and_collide()

#Setup display
display = pygame.display.set_mode((800,800))
surf = pygame.Surface(display.get_size(), pygame.SRCALPHA)

w = WallCollider(400,400, 300, 300, (255,255,255, 100))
w = WallCollider(600,600, 200, 200, (255,255,255, 100))
p = PlayerCollider(50, 50, 50, 50, (150,130,150, 255))

clock = pygame.time.Clock()
running = True
speed = 5

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            match event.key:
                case pygame.K_s:
                    p.movement_vector.y += 1
                case pygame.K_w:
                    p.movement_vector.y -= 1
                case pygame.K_d:
                    p.movement_vector.x += 1
                case pygame.K_a:
                    p.movement_vector.x -= 1
        elif event.type == pygame.KEYUP:
            match event.key:
                case pygame.K_s:
                    p.movement_vector.y -= 1
                case pygame.K_w:
                    p.movement_vector.y += 1
                case pygame.K_d:
                    p.movement_vector.x -= 1
                case pygame.K_a:
                    p.movement_vector.x += 1
    
    display.fill(0)
    surf.fill(0)
    for w in WallCollider.all:
        w.draw(surf)
    p.update()
    p.draw(surf)
    pygame.draw.circle(surf, "red",p.pos,10)
    display.blit(surf, (0,0))
    pygame.display.update()
    clock.tick(100)