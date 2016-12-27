import math
import pygame
import sys
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


def load_image(spriteName):
    return pygame.image.load('resources/{0}.png'.format(spriteName))


def render(x, y, sprite):
    # just blit rewritten for convenience
    windowSurfaceObj.blit(sprite, (x, y))


def display_data(x, y, data, font, color):
    # render a variable onscreen
    dataText = font.render("{0}".format(data), True, color)
    render(x, y, dataText)


def liquid_collision(liquid, char):
    # detect if a character is in contact with a body of liquid and adjust it accordingly
    for l in range(len(liquid)):
        if collision(char.y, liquid[l][1], 24) & collision(char.x, liquid[l][0], 24):
            char.yvelocity *= 0.5
            char.inLiquid = True
            break
        else:
            char.inLiquid = False


def ramp_collision(ramp, char):
    # detect if a character is in contact with sloped blocks and adjust it accordingly
    for r in range(len(ramp)):
        if collision(char.y, ramp[r][1], 18) & collision(char.x, ramp[r][0], 18):
            if ramp[r][3] == True:
                char.y = ramp[r][1] - (20 - math.fabs(char.x - ramp[r][0]))
            elif char.x - ramp[r][0] < -1:
                char.y = ramp[r][1] + math.fabs(char.x - ramp[r][0]) + 2
            else:
                char.y = ramp[r][1] - math.fabs(char.x - ramp[r][0]) - 18
            player.grounded = True


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
            break
        else:
            char.grounded = False
    for s in range(len(solid)):
        if collision(char.y, solid[s][1], 17) & collision(char.x, solid[s][0], 35):
            if char.x > solid[s][0]:
                char.x = solid[s][0] + 36
            else:
                char.x = solid[s][0] - 36


def render_visible(tiles, char):
    # render all tiles on the screen relative to a character
    for t in tiles:
        if (math.fabs(t[0] - char.x) < 356) & (math.fabs(t[1] - char.y) < 276):
            render(t[0] + 320 - char.x, t[1] + 258 - char.y, t[2])


class player:
    # player related info stored here
    x = 0
    y = 0
    yvelocity = 0
    direction = 0
    grounded = False
    inLiquid = False
    sprite = pygame.sprite.Sprite()
    sprite.image = 0
    walk = load_image('frog')
    jump = load_image('frog_leap')


backgroundObj = load_image('colored_land')
grassLeft = load_image('grassLeft')
grassMid = load_image('grassMid')
grassRight = load_image('grassRight')
grassCenter = load_image('grassCenter')
grassSlopeLeft = load_image('grassSlopeLeft')
grassSlopeRight = load_image('grassSlopeRight')
waterTop = load_image('waterTop')
waterCenter = load_image('waterCenter')

# block format: [x,y, type]
blocks = []
for x in range(-3600, 3600, 36):
    blocks.append([x, 218, grassMid])
for x in range(-3600, 3600, 36):
    for y in range(254, 436, 36):
        blocks.append([x, y, grassCenter])
blocks.append([0, 160, grassMid])
blocks.append([36, 60, grassMid])
blocks.append([220, 80, grassMid])
blocks.append([100, 160, grassMid])
blocks.append([-164, 183, grassCenter])
blocks.append([-200, 183, grassCenter])
liquids = []
for x in range(300, 500, 36):
    for y in range(2, 218, 36):
        liquids.append([x, y, waterCenter])

slopes = []
slopes.append([-128, 183, grassSlopeRight, True])
slopes.append([-164, 147, grassSlopeRight, True])
slopes.append([-200, 147, grassSlopeLeft, False])
slopes.append([-236, 183, grassSlopeLeft, False])

while not crashed:
    render(0, 0, backgroundObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if pygame.key.get_pressed()[pygame.K_SPACE] != 0:
        if player.grounded == True or player.inLiquid == True:
            player.yvelocity = 14
            player.y -= 1
            player.grounded = False
    if pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
        player.x += 7
        player.direction = 1
    if pygame.key.get_pressed()[pygame.K_LEFT] != 0:
        player.x -= 7
        player.direction = 0
    if player.grounded == True:
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
    render_visible(slopes, player)
    render_visible(blocks, player)
    render_visible(liquids, player)
    display_data(10, 10, player.grounded, fontObj, white)
    display_data(10, 40, player.inLiquid, fontObj, white)
    display_data(10, 70, player.x, fontObj, white)
    display_data(10, 100, player.y, fontObj, white)
    render(320, 240, pygame.transform.flip(player.sprite.image, player.direction, 0))
    pygame.display.update()
    fpsClock.tick(30)
