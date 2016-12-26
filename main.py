import pygame, sys, math
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
backgroundObj = pygame.image.load('resources/colored_land.png')

fontObj = pygame.font.SysFont('Times New Roman', 32)


def collision(a, b, size):
    # returns true if the two values are within a certain range of each other
    if math.fabs(a - b) <= size:
        return True
    else:
        return False


def render(x, y, sprite):
    # just blit rewritten for convenience
    windowSurfaceObj.blit(sprite, (x, y))


def displayData(x, y, data):
    dataText = fontObj.render("{0}".format(data), True, white)
    render(x, y, dataText)


def liquidCollision(liquid, char):
    for l in range(len(liquid)):
        if collision(char.y, liquid[l][1], 24) & collision(char.x, liquid[l][0], 24):
            char.yvelocity *= 0.3
            char.inLiquid = True
            break
        else:
            char.inLiquid = False


def solidCollision(solid, char):
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


def renderVisible(tiles, char):
    for t in tiles:
        if (math.fabs(t[0] - char.x) < 356) & (math.fabs(t[1] - char.y) < 276):
            render(t[0] + 320 - char.x, t[1] + 258 - char.y, t[2])


class player:
    x = 0
    y = 0
    yvelocity = 0
    direction = 0
    grounded = False
    inLiquid = False
    sprite = pygame.sprite.Sprite()
    sprite.image = pygame.image.load('resources/frog.png')
    walk = pygame.image.load('resources/frog.png')
    jump = pygame.image.load('resources/frog_leap.png')


grassLeft = pygame.image.load('resources/grassLeft.png')
grassMid = pygame.image.load('resources/grassMid.png')
grassRight = pygame.image.load('resources/grassRight.png')
grassCenter = pygame.image.load('resources/grassCenter.png')

waterTop = pygame.image.load('resources/waterTop.png')
waterCenter = pygame.image.load('resources/water.png')

# block format: [x,y, type]
blocks = []
liquids = []
for x in range(-3600, 3600, 36):
    blocks.append([x, 218, grassMid])
for x in range(-3600, 3600, 36):
    for y in range(254, 436, 36):
        blocks.append([x, y, grassCenter])
for x in range(300, 500, 36):
    for y in range(2, 218, 36):
        liquids.append([x, y, waterCenter])
blocks.append([0, 160, grassMid])
blocks.append([36, 60, grassMid])
blocks.append([220, 80, grassMid])
blocks.append([100, 160, grassMid])
blocks.append([-100, 183, grassMid])

while not crashed:
    render(0, 0, backgroundObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if pygame.key.get_pressed()[pygame.K_SPACE] != 0:
        if player.grounded == True or player.inLiquid == True:
            player.yvelocity = 14
            player.y -= 2
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
    solidCollision(blocks, player)
    liquidCollision(liquids, player)
    renderVisible(blocks, player)
    renderVisible(liquids, player)
    displayData(10, 10, player.grounded)
    displayData(10, 40, player.inLiquid)
    displayData(10, 70, player.x)
    displayData(10, 100, player.y)
    render(320, 240, pygame.transform.flip(player.sprite.image, player.direction, 0))
    pygame.display.update()
    fpsClock.tick(30)
