import time
import pygame
import sys

import math

# Initialize Pygame and fonts
pygame.init()
pygame.font.init()
pygame.display.set_caption("This took half a day's worth of life away from me")

# Set up display with a size of 1023x1023

window = pygame.display.set_mode((2240, 800))

# Init thruster png
thrusterIdle = pygame.image.load("1.png")
thrusterPos = pygame.image.load("2.png")
thrusterNeg = pygame.image.load("3.png")
pygame.Surface.convert_alpha(thrusterIdle)
pygame.Surface.convert_alpha(thrusterPos)
pygame.Surface.convert_alpha(thrusterNeg)

my_font = pygame.font.SysFont("Comic Sans MS", 30)

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
gray = (170, 170, 170)
Lgray = (200, 200, 200)

deadzoneHor = (450, 574)
deadzoneVer = (400, 624)


time.sleep(3)


numPoints = 5
dataList = [0]*numPoints


def map_value(value, in_min, in_max, out_min, out_max):
    """
    Maps a value from one range to another.

    value: The input value to map.
    in_min: The lower bound of the input range.
    in_max: The upper bound of the input range.
    out_min: The lower bound of the output range.
    out_max: The upper bound of the output range.

    Returns:
        The mapped value.
    """
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Function to draw the grid


def draw_grid(markerCoord):

    graphSize = 512
    graphSurface = pygame.Surface((graphSize, graphSize))
    graphPosition = (1500, 200)

    mult = graphSize/1024

    horMin = deadzoneHor[0]*mult
    horMax = (deadzoneHor[1]-deadzoneHor[0])*mult

    verMin = deadzoneVer[0]*mult
    verMax = (deadzoneVer[1]-deadzoneVer[0])*mult

    graphSurface.fill(white)

    # Gray out specific areas

    pygame.draw.rect(graphSurface, Lgray, (0, horMin, graphSize, horMax))
    pygame.draw.rect(graphSurface, Lgray, (verMin, 0, verMax, graphSize))

    # Draw minor gridlines
    for i in range(int(64*mult), graphSize, int(64*mult)):
        pygame.draw.line(graphSurface, gray, (i, 0), (i, graphSize))
        pygame.draw.line(graphSurface, gray, (0, i), (graphSize, i))

    # Draw axes
    pygame.draw.line(graphSurface, black, (0, graphSize // 2),
                     (graphSize, graphSize // 2), 1)
    pygame.draw.line(graphSurface, black, (graphSize // 2, 0),
                     (graphSize // 2, graphSize), 1)
    pygame.draw.rect(graphSurface, black, (0, 0, graphSize, graphSize), 1)

    # Draw marker

    x = int(markerCoord[0]*mult)
    y = int(markerCoord[1]*mult)

    pygame.draw.circle(graphSurface, red, (x, y), 5)

    print(x, y, horMin, horMax)
    window.blit(graphSurface, graphPosition)


"""
    if(y>horMax+horMin or y< horMin):
        if(x>verMax+verMin or x < verMin):

         pygame.draw.line(graphSurface, red,
                          (graphSize // 2,graphSize // 2),(x, y),2)
"""


def draw_polar(markerCoord):

    polarSize = 256
    polarSurface = pygame.Surface((polarSize, polarSize))
    polarSurface.fill(white)
    mult = polarSize / 512

    centre = (polarSize // 2, polarSize // 2)

    max_radius = 256*mult

    pygame.draw.circle(polarSurface, Lgray, centre, max_radius, 2)

    sub_arc_num = 4
    for radius in range(0, int(max_radius), int(max_radius/sub_arc_num)):
        pygame.draw.circle(polarSurface, Lgray, centre, radius, 1)

    pygame.draw.rect(polarSurface, white,
                     (0, polarSize // 2, polarSize, polarSize))

    for deg in range(0, 181, 30):

        x = math.floor(polarSize // 2+max_radius*math.cos(math.radians(deg)))
        y = math.ceil(polarSize // 2-max_radius*math.sin(math.radians(deg)))
        pygame.draw.line(polarSurface, Lgray, centre, (x, y), 1)

    # Draw marker

    x = (markerCoord*1.50588 + 64)*mult
    y = 256*mult - int(math.sqrt(pow(max_radius*0.75, 2)-pow(x-max_radius, 2)))

    pygame.draw.circle(polarSurface, red, (x, y), 5)

    window.blit(polarSurface, (1200, 200))


def getMarkerCoord(type):
    if type == 'grid':
        return ((map_value(float(dataList[0]), -1, 1, 0, 1024), map_value(float(dataList[1]), -1, 1, 0, 1024)))

    if type == 'polar':
        return (map_value(float(dataList[2]), -1, 1, 0, 255))


def drawROV(x, y, size):
    rov = pygame.Surface((size, size))
    rov.fill(white)

    per = int(dataList[2])
    thruster = thrusterIdle

    if per < 20:
        thruster = thrusterIdle
    else:
        # thruster = thrusterNeg
        thruster = thrusterPos

    if per > 128:
        per = 128

    leftFront = pygame.transform.scale_by(thruster, 0.5)
    rightFront = pygame.transform.flip(
        pygame.transform.scale_by(thruster, 0.5), 1, 0)
    leftRear = rightFront
    rightRear = leftFront

    pygame.draw.rect(rov, Lgray, (0, 128-per, 128, per))
    rov.blit(leftFront, (0, 0))

    pygame.draw.rect(rov, Lgray, (200, 128-per, 128, per))
    rov.blit(rightFront, (200, 0))

    pygame.draw.rect(rov, Lgray, (0, 328-per, 128, per))
    rov.blit(leftRear, (0, 200))

    pygame.draw.rect(rov, Lgray, (200, 328-per, 128, per))
    rov.blit(rightRear, (200, 200))

    window.blit(rov, (x, y))

# Main loop


def main():

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # x = (x + 1) % size
        window.fill(white)

        drawROV(100, 100, 500)

        # pygame.Surface.convert_alpha(thruster)
        # text_surface = my_font.render('30', False, black)
        # thruster.blit(text_surface, (40,30))

        draw_grid(getMarkerCoord('grid'))
        draw_polar(getMarkerCoord('polar'))

        # draw_point(x, y)
        pygame.display.flip()
        # pygame.time.delay(100)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
