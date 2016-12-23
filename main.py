import pygame, sys, math
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

display_width = 640
display_height = 480

title = 'Physics Engine'
crashed = False

windowSurfaceObj = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption(('{0}').format(title))

red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)
white = pygame.Color(255, 255, 255)
black = pygame.Color(0, 0, 0)
backgroundObj = pygame.image.load('resources/colored_land.png')

fontObj = pygame.font.SysFont('Times New Roman', 32)

grassLeft = pygame.image.load('resources/grassLeft.png')
grassMid = pygame.image.load('resources/grassMid.png')
grassRight = pygame.image.load('resources/grassRight.png')
grassCenter = pygame.image.load('resources/grassCenter.png')


def collision(a, b, size):
    # returns true if the two values are within a certain range of each other
    if math.fabs(a - b) <= size:
        return True
    else:
        return False


def render(x, y, sprite):
    # just blit rewritten for convenience
    windowSurfaceObj.blit(sprite, (x, y))


class player:
    x = 0
    y = 0
    grounded = False
    yvelocity = 0
    sprite = pygame.sprite.Sprite()
    sprite.image = pygame.image.load('resources/frog.png')


# block format: x,y, type
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
blocks.append([-100, 183, grassMid])

while not crashed:
    render(0, 0, backgroundObj)
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    if pygame.key.get_pressed()[pygame.K_SPACE] != 0:
        if player.grounded == True:
            player.yvelocity = 14
            player.y -= 2
            player.grounded = False
    if pygame.key.get_pressed()[pygame.K_RIGHT] != 0:
        player.x += 7
    if pygame.key.get_pressed()[pygame.K_LEFT] != 0:
        player.x -= 7
    if player.yvelocity > -32:
        if not player.grounded:
            player.yvelocity -= 1
        else:
            player.yvelocity = 0
    player.y -= player.yvelocity
    for b in range(len(blocks)):
        if collision(player.y, blocks[b][1], 18) & collision(player.x, blocks[b][0], 18):
            if player.y > blocks[b][1]:
                player.y = blocks[b][1] + 36
                player.yvelocity = 0
            else:
                player.y = blocks[b][1] - 18
                player.grounded = True
            break
        else:
            player.grounded = False
    for b in range(len(blocks)):
        if collision(player.y, blocks[b][1], 17) & collision(player.x, blocks[b][0], 35):
            if player.x > blocks[b][0]:
                player.x = blocks[b][0] + 35
            else:
                player.x = blocks[b][0] - 35
    for b in blocks:
        if (math.fabs(b[0]-player.x) < 356) & (math.fabs(b[1]-player.y) < 276):
            render(b[0] + 320 - player.x, b[1] + 258 - player.y, b[2])
    grounded = fontObj.render("{0}".format(player.grounded), True, white)
    render(10, 10, grounded)
    x = fontObj.render("{0}".format(player.x), True, white)
    render(10, 40, x)
    y = fontObj.render("{0}".format(player.y), True, white)
    render(10, 70, y)
    render(320, 240, player.sprite.image)
    pygame.display.update()
    fpsClock.tick(30)
