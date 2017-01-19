import math
import os
import sys

import pygame
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

display_width = 640
display_height = 480

title = 'Physics Engine'
crashed = False

windowSurfaceObj = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('{0}'.format(title))

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)

fontObj = pygame.font.SysFont('Times New Roman', 32)


def collision(a, b, size):
    # returns true if the two values are within a certain range of each other
    if math.fabs(a - b) <= size:
        return True
    else:
        return False


def update_dict(spritename, dict):
    # adds png to sprite dictionary
    dict[spritename] = pygame.image.load('resources/{0}.png'.format(spritename))


def render(x, y, sprite):
    # just blit rewritten for convenience
    windowSurfaceObj.blit(sprite, (x, y))


def display_data(x, y, data, font, color):
    # render a variable onscreen
    datatext = font.render("{0}".format(data), True, color)
    render(x, y, datatext)


def liquid_collision(liquid, char):
    # detect if a character is in contact with a body of liquid and adjust it accordingly
    for l in range(len(liquid)):
        if collision(char.y, liquid[l][1], 18) & collision(char.x, liquid[l][0], 18):
            char.yvelocity *= 0.5
            char.inLiquid = True
            break
        else:
            char.inLiquid = False


def ramp_collision(ramp, char):
    # detect if a character is in contact with sloped blocks and adjust it accordingly
    for r in range(len(ramp)):
        if collision(char.y, ramp[r][1], 18) & collision(char.x, ramp[r][0], 18):
            if ramp[r][3]:
                char.y = ramp[r][1] - 18 + (char.x - ramp[r][0])
            else:
                char.y = ramp[r][1] - 18 - (char.x - ramp[r][0])
            player.grounded = True
            break


def solid_collision(solid, char):
    # detect if a character is in contact with solid blocks and adjust it accordingly
    for s in range(len(solid)):
        if collision(char.y, solid[s][1], 18) & collision(player.x, solid[s][0], 18):
            if char.y > solid[s][1]:
                char.y = solid[s][1] + 36
                char.yvelocity = 0
            else:
                char.y = solid[s][1] - 18
                char.grounded = True
                char.yvelocity = 0
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


def update_tiles(tile, name, frames, dict):
    frame = (tile[4] + 1) % frames
    tile[4] = frame
    tile[2] = dict['{0}{1}'.format(name, frame)]


def manage_updates(tile, name, frames, dict, nextupdate=-1):
    if tile[5] >= 0:
        tile[5] -= 1
    if tile[5] == 0:
        update_tiles(tile, name, frames, dict)
        tile[5] = nextupdate


def object_collision(object, char):
    for o in range(len(object)):
        if collision(char.y, object[o][1], 18) & collision(player.x, object[o][0], 35):
            if object[o][3] == 'spring':
                char.y -= 2
                char.yvelocity = 25
                object[o][5] = 30
                update_tiles(object[o], 'spring', 2, blockDict)


def render_visible(tiles, char):
    # render all tiles on the screen relative to a character
    for t in tiles:
        if (math.fabs(t[0] - char.x) < 356) & (math.fabs(t[1] - char.y) < 276):
            render(t[0] + 320 - char.x, t[1] + 258 - char.y, t[2])


def generate_rect(startx, starty, length, height, appearance, blocktype, dict):
    # generate a rectangular structure of the defined block with a certain texture
    for x in range(startx, startx + length * 36, 36):
        blocktype.append([x, starty, dict['{0}Top'.format(appearance)]])
    for x in range(startx, startx + length * 36, 36):
        for y in range(starty + 36, starty + 36 + height * 36, 36):
            blocktype.append([x, y, dict['{0}Center'.format(appearance)]])


def generate_ramp(startx, starty, length, appearance, blocktype, blocktype2, direction, dict):
    # generate a ramp of
    tlen = length
    if direction:
        while tlen > 0:
            blocktype.append([startx + tlen * 36, starty + tlen * 36, dict['{0}SlopeRight'.format(appearance)], True])
            if tlen < length:
                blocktype2.append(
                    [startx + tlen * 36, starty + (tlen + 1) * 36, dict['{0}SlopeMidRight'.format(appearance)], True])
            if tlen + 1 < length:
                tlen2 = tlen + 1
                while tlen2 < length:
                    blocktype2.append(
                        [startx + tlen * 36, starty + (tlen2 + 1) * 36, dict['{0}Center'.format(appearance)], True])
                    tlen2 += 1
            tlen -= 1
    else:
        while tlen > 0:
            blocktype.append([startx - tlen * 36, starty + tlen * 36, dict['{0}SlopeLeft'.format(appearance)], False])
            if tlen < length:
                blocktype2.append(
                    [startx - tlen * 36, starty + (tlen + 1) * 36, dict['{0}SlopeMidLeft'.format(appearance)], False])
            if tlen + 1 < length:
                tlen2 = tlen + 1
                while tlen2 < length:
                    blocktype2.append(
                        [startx - tlen * 36, starty + (tlen2 + 1) * 36, dict['{0}Center'.format(appearance)], True])
                    tlen2 += 1
            tlen -= 1


blockDict = {}
# autofill dictionary with sprites from resources
for filename in os.listdir('resources'):
    update_dict(filename[:-4], blockDict)


class PlayerObj:
    # player related info stored here
    x = 0
    y = 0
    yvelocity = 0
    direction = 0
    grounded = False
    inLiquid = False
    sprite = pygame.sprite.Sprite()
    sprite.image = 0
    walk = blockDict['frog']
    jump = blockDict['frog_leap']


player = PlayerObj()

# block format: [x,y,type]
blocks = []
generate_rect(-3600, 216, 200, 6, 'grass', blocks, blockDict)
generate_rect(-524, 144, 10, 1, 'grass', blocks, blockDict)
generate_rect(-660, 72, 1, 2, 'grass', blocks, blockDict)

# object format: [x,y,appearance,object type,current frame,frames in animation]
objects = []
objects.append([136, 180, blockDict['spring1'], 'spring', 1, -1])

# liquid format: [x,y,type]
liquids = []
generate_rect(300, -36, 5, 6, 'water', liquids, blockDict)

# slope format: [x,y,type,left/right](right = true left = false)
slopes = []
generate_ramp(-200, 108, 2, 'grass', slopes, blocks, True, blockDict)
generate_ramp(-524, 108, 2, 'grass', slopes, blocks, False, blockDict)

while not crashed:
    render(0, 0, blockDict['colored_land'])
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if pygame.key.get_pressed()[pygame.K_SPACE] != 0 and (player.grounded or player.inLiquid):
        player.yvelocity = 14
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
    if player.yvelocity > -18:
        if not player.grounded:
            player.yvelocity -= 1
        else:
            player.yvelocity = 0
    player.y -= player.yvelocity
    solid_collision(blocks, player)
    liquid_collision(liquids, player)
    ramp_collision(slopes, player)
    object_collision(objects, player)
    for o in range(len(objects)):
        manage_updates(objects[o], 'spring', 2, blockDict)
    render_visible(slopes, player)
    render_visible(blocks, player)
    render_visible(liquids, player)
    render_visible(objects, player)
    display_data(10, 10, player.grounded, fontObj, white)
    display_data(10, 40, player.inLiquid, fontObj, white)
    display_data(10, 70, player.yvelocity, fontObj, white)
    display_data(10, 100, player.x, fontObj, white)
    display_data(10, 130, player.y, fontObj, white)
    render(320, 240, pygame.transform.flip(player.sprite.image, player.direction, 0))
    pygame.display.update()
    fpsClock.tick(30)
