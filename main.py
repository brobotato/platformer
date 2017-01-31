import math, os, sys, pygame
from pygame.locals import *

pygame.init()
fps_clock = pygame.time.Clock()

display_width = 640
display_height = 480

title = 'Physics Engine'
crashed = False

window_surface_obj = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('{0}'.format(title))

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)

font_obj = pygame.font.Font("resources/kenvector_future.ttf", 15)


# returns true if the two values are within a certain range of each other
def collision(a, b, size):
    if math.fabs(a - b) <= size:
        return True
    else:
        return False


# adds png to sprite dictionary
def update_dict(sprite_name, dict):
    dict[sprite_name] = pygame.image.load('resources/{0}.png'.format(sprite_name))


# just blit rewritten for convenience
def render(x, y, sprite):
    window_surface_obj.blit(sprite, (x, y))


# render a variable as text onscreen
def display_data(x, y, data, font, color):
    data_text = font.render("{0}".format(data), True, color)
    render(x, y, data_text)


# move a tile to the next image sequentially, starting at 0 | frames = frames in animation
def update_tiles(tile, name, frames, dict):
    frame = (tile[4] + 1) % frames
    tile[4] = frame
    tile[2] = dict['{0}{1}'.format(name, frame)]


# support for smooth animation transitions
def manage_updates(tile, frames, dict, next_update=-1):
    if tile[5] >= 0:
        tile[5] -= 1
    if tile[5] == 0:
        update_tiles(tile, tile[3], frames, dict)
        tile[5] = next_update


# detect if a character is in contact with a body of liquid and adjust it accordingly
def liquid_collision(liquid, char):
    for l in range(len(liquid)):
        if collision(char.y, liquid[l][1], 18) & collision(char.x, liquid[l][0], 18):
            char.y_v *= 0.5
            char.in_liquid = True
            break
        else:
            char.in_liquid = False


# detect if a character is in contact with sloped blocks and adjust it accordingly
def ramp_collision(ramp, char):
    for r in range(len(ramp)):
        if collision(char.y, ramp[r][1], 18) & collision(char.x, ramp[r][0], 18):
            if ramp[r][3]:
                char.y = ramp[r][1] - 18 + (char.x - ramp[r][0])
            else:
                char.y = ramp[r][1] - 18 - (char.x - ramp[r][0])
            char.grounded = True
            break


# detect if a character is in contact with solid blocks and adjust it accordingly
def solid_collision(solid, char):
    for s in range(len(solid)):
        if collision(char.y, solid[s][1], 18) & collision(char.x, solid[s][0], 18):
            if char.y > solid[s][1]:
                char.y = solid[s][1] + 36
            else:
                char.y = solid[s][1] - 18
                char.grounded = True
            char.y_v = 0
            break
        else:
            char.grounded = False
    for s in range(len(solid)):
        if collision(char.y, solid[s][1], 17) & collision(char.x, solid[s][0], 35):
            if char.x > solid[s][0]:
                char.x = solid[s][0] + 36
            else:
                char.x = solid[s][0] - 36
            break


# detect if a character is in contact with a physics object and act accordingly
def object_collision(object, char):
    for o in range(len(object)):
        if collision(char.y, object[o][1], 18) & collision(player.x, object[o][0], 35):
            if object[o][3] == 'spring':
                char.y -= 2
                char.y_v = 25
                object[o][5] = 30
                update_tiles(object[o], 'spring', 2, block_dict)
            if object[o][3] == 'sign':
                object[o][6].display()


# render all tiles on the screen relative to a character
def render_visible(tiles, char):
    for t in tiles:
        if (math.fabs(t[0] - char.x) < 356) & (math.fabs(t[1] - char.y) < 276):
            render(t[0] + 320 - char.x, t[1] + 258 - char.y, t[2])


# generate a rectangular structure of the defined block with a certain texture
def generate_rect(startx, starty, length, height, appearance, blocktype, dict):
    for x in range(startx, startx + length * 36, 36):
        blocktype.append([x, starty, dict['{0}_top'.format(appearance)]])
    for x in range(startx, startx + length * 36, 36):
        for y in range(starty + 36, starty + 36 + height * 36, 36):
            blocktype.append([x, y, dict['{0}_center'.format(appearance)]])


# generate a ramp of the defined block with a certain texture
def generate_ramp(startx, starty, length, appearance, blocktype, blocktype2, direction, dict):
    tlen = length
    if direction:
        while tlen > 0:
            blocktype.append([startx + tlen * 36, starty + tlen * 36, dict['{0}_s_right'.format(appearance)], True])
            if tlen < length:
                blocktype2.append(
                    [startx + tlen * 36, starty + (tlen + 1) * 36, dict['{0}_s_m_right'.format(appearance)], True])
            if tlen + 1 < length:
                tlen2 = tlen + 1
                while tlen2 < length:
                    blocktype2.append(
                        [startx + tlen * 36, starty + (tlen2 + 1) * 36, dict['{0}_center'.format(appearance)], True])
                    tlen2 += 1
            tlen -= 1
    else:
        while tlen > 0:
            blocktype.append([startx - tlen * 36, starty + tlen * 36, dict['{0}_s_left'.format(appearance)], False])
            if tlen < length:
                blocktype2.append(
                    [startx - tlen * 36, starty + (tlen + 1) * 36, dict['{0}_s_m_left'.format(appearance)], False])
            if tlen + 1 < length:
                tlen2 = tlen + 1
                while tlen2 < length:
                    blocktype2.append(
                        [startx - tlen * 36, starty + (tlen2 + 1) * 36, dict['{0}_center'.format(appearance)], True])
                    tlen2 += 1
            tlen -= 1


# autofill dictionary with sprites from resources
block_dict = {}
for filename in os.listdir('resources'):
    if filename[-4:] == '.png':
        update_dict(filename[:-4], block_dict)


# player related info stored here
class player_obj:
    x = 0
    y = 0
    y_v = 0
    direction = 0
    grounded = False
    in_liquid = False
    sprite = pygame.sprite.Sprite()
    sprite.image = 0
    walk = block_dict['frog']
    jump = block_dict['frog_leap']


class msg_box_obj:
    x = 10
    y = 10
    sprite = pygame.sprite.Sprite()
    sprite.image = block_dict['text_box']

    def __init__(self, msg):
        self.message = font_obj.render("{0}".format(msg), True, white)
        self.message_rect = self.message.get_rect(center=(display_width / 2, 70))

    def display(self):
        render(self.x, self.y, self.sprite.image)
        window_surface_obj.blit(self.message, self.message_rect)


player = player_obj()
test_msg = msg_box_obj('test')

# block format: [x,y,type]
blocks = []
generate_rect(-3600, 216, 200, 6, 'grass', blocks, block_dict)
generate_rect(-524, 144, 10, 1, 'grass', blocks, block_dict)
generate_rect(-660, 72, 1, 2, 'grass', blocks, block_dict)

# object format: [x,y,appearance,object type,current frame,frames in animation]
objects = []
objects.append([136, 180, block_dict['spring0'], 'spring', 1, -1])
objects.append([-236, 108, block_dict['sign1'], 'sign', 1, -1, test_msg])

# liquid format: [x,y,type]
liquids = []
generate_rect(300, -36, 5, 6, 'water', liquids, block_dict)

# slope format: [x,y,type,left/right](right = true left = false)
slopes = []
generate_ramp(-200, 108, 2, 'grass', slopes, blocks, True, block_dict)
generate_ramp(-524, 108, 2, 'grass', slopes, blocks, False, block_dict)

while not crashed:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if pygame.key.get_pressed()[pygame.K_SPACE] != 0 and (player.grounded or player.in_liquid):
        player.y_v = 14
        player.y -= 1
        player.grounded = False
    if pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
        player.x += 7
        player.direction = 1
    if pygame.key.get_pressed()[pygame.K_LEFT] != 0:
        player.x -= 7
        player.direction = 0
    if player.grounded:
        player.sprite.image = player.walk
    else:
        player.sprite.image = player.jump
    if player.y_v > -16:
        if not player.grounded:
            player.y_v -= 1
        else:
            player.y_v = 0
    render(0, 0, block_dict['colored_land'])
    player.y -= player.y_v
    solid_collision(blocks, player)
    liquid_collision(liquids, player)
    ramp_collision(slopes, player)
    object_collision(objects, player)
    for o in range(len(objects)):
        manage_updates(objects[o], 2, block_dict)
    render_visible(slopes, player)
    render_visible(blocks, player)
    render_visible(liquids, player)
    render_visible(objects, player)
    display_data(10, 10, player.grounded, font_obj, white)
    display_data(10, 40, player.in_liquid, font_obj, white)
    display_data(10, 70, player.y_v, font_obj, white)
    display_data(10, 100, player.x, font_obj, white)
    display_data(10, 130, player.y, font_obj, white)
    render(320, 240, pygame.transform.flip(player.sprite.image, player.direction, 0))
    pygame.display.update()
    fps_clock.tick(30)
