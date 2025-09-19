import pygame
pygame.display.init()
pygame.font.init()
font = pygame.font.SysFont("consolas", 20)

#Borderless fullscreen
display = pygame.display.set_mode(pygame.display.get_desktop_sizes()[0], pygame.NOFRAME)

SCALE = 10

class Sprite():
    all:list["Sprite"] = []
    def __init__(self, name, img_name, pos, text=None):
        Sprite.all.append(self)
        self.name = name
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
        if self.text and render_text:
            surface.blit(self.text, self.pos)
    
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

#Store sprite, pos, rect
head_sprite = Sprite("head", "debug_head.png", [0,0])
torso_sprite = Sprite("torso", "debug_torso.png", [100,0])
left_foot_sprite = Sprite("left foot", "debug_foot.png", [300,0], text="LF")
right_foot_sprite = Sprite("right foot", "debug_foot.png", [300,50], text="RF")
left_hand_sprite = Sprite("left hand", "debug_hand.png", [400, 0], text="LH")
right_hand_sprite = Sprite("right hand", "debug_hand.png", [400, 50], text="RH")


drag_sprite = None
displacement = None
render_text = True

clock = pygame.time.Clock()
running = True
#Mainloop
while running:
    display.fill([60, 150, 200])
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DELETE:
                running = False
            elif event.key == pygame.K_s:
                render_text = not render_text
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            possible_sprites = list(filter(lambda x: x.highlighted, Sprite.all))
            if possible_sprites != []:
                drag_sprite = possible_sprites[0]
                sx,sy = drag_sprite.pos
                mx, my = mouse_pos
                displacement = [sx-mx, sy-my]
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            drag_sprite = None
            last_mouse_pos = None

    mouse_pos = pygame.mouse.get_pos()        
    if drag_sprite:
        drag_sprite.pos = [mouse_pos[0]+displacement[0], mouse_pos[1]+displacement[1]]
    
    shortest_distance = 10000
    closest = None
    for sprite in Sprite.all:
        sprite.highlighted = False
        sprite.draw(display)
        dist_to_mouse = sprite.distance_to(mouse_pos)
        if dist_to_mouse < shortest_distance or closest == None:
            shortest_distance = dist_to_mouse
            closest = sprite
    if closest.get_rect().collidepoint(mouse_pos):
        closest.draw_highlight(display, int(SCALE/2))

    pygame.display.update()
    clock.tick(100)