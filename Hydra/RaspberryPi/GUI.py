##########################################
#  This is the visualiation of ROV data  #
# Made by Jason Ho on Apr 21, 2025, 00:10 #
##########################################


# Import libraries
import pygame
import time
import math
import numpy as np
from config import *
from utils import *

# Initialize Pygame and fonts
#pygame.init()
pygame.font.init()
pygame.display.set_caption("This took half a day's worth of life away from me")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)
my_font = pygame.font.SysFont("Comic Sans MS", 30)

window = pygame.display.set_mode((0, 0), flags=pygame.RESIZABLE, depth=24)



# Init thruster png
thruster = pygame.image.load("thrusterUPDATED.png")
pygame.Surface.convert_alpha(thruster)

# Init the joystick
"""
pygame.joystick.init()

print(pygame.joystick.get_count())

joy = pygame.joystick.Joystick(0)
joy.init()

print(f"{joy.get_name()} is connected")
"""

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (102, 178, 255)
GREY = (170, 170, 170)
DGREY = (140, 140, 140)
LGREY = (200, 200, 200)
SKY = (246, 255, 255)
# --- Artificial Horizon Colors ---
BROWN = (163, 240, 225)
GREEN = (0, 255, 0)

deadzoneX = 0.25
deadzoneY = 0.25



# -----------------PyGame inilisation complete-----------------#


previous_time = time.time()


testLoop = True
print("Intialising PySerial, please wait...")


print(f"Initialised in {round(time.time() - previous_time, 2)} seconds.")
time.sleep(2)

# -----------------PySerial inilisation complete-----------------#

length = pygame.display.get_window_size()[0]
width = pygame.display.get_window_size()[1]



print(pygame.display.get_window_size()[0], pygame.display.get_window_size()[1])



def draw_grid(markerCoord):

    graphSize = 512
    graphSurface = pygame.Surface((graphSize, graphSize))
    graphPosition = (length - 612, 350)

    mult = graphSize/1024

    assert((1-deadzoneX) != 0)
    assert((1+deadzoneX) != 0)
    
    horMin = graphSize//2 * (1-deadzoneX)
    horMax = graphSize//2 * (1+deadzoneX)
    
    verMin = graphSize//2 * (1-deadzoneY)
    verMax = graphSize//2 * (1+deadzoneY)

    graphSurface.fill(WHITE)

    # Gray out specific areas

    pygame.draw.rect(graphSurface, LGREY,
                     (0, horMin, graphSize, horMax-horMin))
    pygame.draw.rect(graphSurface, LGREY,
                     (verMin, 0, verMax-verMin, graphSize))
    pygame.draw.rect(graphSurface, DGREY,
                     (verMin, horMin, verMax-verMin, horMax-horMin))

    # Draw minor gridlines
    for i in range(int(64*mult), graphSize, int(64*mult)):
        pygame.draw.line(graphSurface, GREY, (i, 0), (i, graphSize))
        pygame.draw.line(graphSurface, GREY, (0, i), (graphSize, i))

    # Draw axes
    pygame.draw.line(graphSurface, BLACK, (0, graphSize // 2),
                     (graphSize, graphSize // 2), 1)
    pygame.draw.line(graphSurface, BLACK, (graphSize // 2, 0),
                     (graphSize // 2, graphSize), 1)
    pygame.draw.rect(graphSurface, BLACK, (0, 0, graphSize, graphSize), 1)

    # Draw marker

    x = int(markerCoord[0]*mult)
    y = int(markerCoord[1]*mult)

    pygame.draw.circle(graphSurface, RED, (x, y), 5)
    window.blit(graphSurface, graphPosition)


def draw_polar(markerCoord):

    polarSize = 256  # diameter
    polarSurface = pygame.Surface((polarSize, polarSize))
    polarSurface.fill(SKY)
    mult = polarSize / 256

    centre = (polarSize // 2, polarSize // 2)

    max_radius = polarSize/2

    pygame.draw.circle(polarSurface, WHITE, centre, max_radius)
    pygame.draw.circle(polarSurface, LGREY, centre, max_radius, 2)

    sub_arc_num = 4
    assert(sub_arc_num != 0)
    for radius in range(0, int(max_radius), int(max_radius/sub_arc_num)):
        pygame.draw.circle(polarSurface, LGREY, centre, radius, 1)

    pygame.draw.rect(polarSurface, SKY,
                     (0, polarSize // 2, polarSize, polarSize))

    for deg in range(0, 181, 30):

        assert(2+max_radius*math.cos(math.radians(deg)) != 0)
        assert(2-max_radius*math.cos(math.radians(deg)) != 0)
        x = math.floor(polarSize // 2+max_radius*math.cos(math.radians(deg)))
        y = math.ceil(polarSize // 2-max_radius*math.sin(math.radians(deg)))
        pygame.draw.line(polarSurface, LGREY, centre, (x, y), 1)

    # Draw marker

    x = map_range(markerCoord, 0, 256, -max_radius*0.75, max_radius*0.75)
    y = int(math.sqrt(pow(max_radius*0.75, 2)-pow(x, 2)))


    pygame.draw.circle(polarSurface, RED, (x+max_radius, max_radius-y), 5)

    window.blit(polarSurface, (length - 484, 100))


def draw_slider(markerCoord):

    sliderLength = 64 #height
    sliderHeight = 512 # wiudth

    sliderSurface = pygame.Surface((sliderLength, sliderHeight))
    sliderSurface.fill(WHITE)

    centre = (sliderLength // 2, sliderHeight //2)

    pygame.draw.rect(sliderSurface, BLACK, (0,0,sliderLength, sliderHeight), 3, 2)

    x = centre[0]
    y = int(markerCoord)
    pygame.draw.circle(sliderSurface, RED, (x, y), 5)

    window.blit(sliderSurface, (length - 700, 100))



def getMarkerCoord(type, data):
    if type == 'grid':
        x = float(data[0])
        y = float(data[1])

        return ((x, y))

    if type == 'polar':
        return (float(data[2]))

    if type == 'slider':
        return (float(data[3]))








                
def drawROV(X, Y, data):
    # X and Y are values denoting the coordinates of the ROV
    # size should be a value denoting the size of the ROV
    # data shoud be an array with 4 values ranging from -1.00~1.00
    rov = pygame.Surface((375, 500))
    rov.fill(SKY)

    thrusterSize = 128
    mult = thrusterSize/256

    leftFront = pygame.transform.scale(thruster, (thrusterSize, thrusterSize))

    i = 0
    for y in [100, 300]:
        for x in [20, 220]:
            k = 0 if (y == 100 and x == 20) or (y == 300 and x == 220) else 1

            per = abs(float(data[i])*thrusterSize)
            frontTipCoord = (x+220 * mult + k *
                             (thrusterSize - 440 * mult), y+40 * mult)
            rearTipCoord = (x+24 * mult + k *
                            (thrusterSize - 48 * mult), y+234 * mult)

            # lines = ((x + thrusterSize // 2, y),(x + thrusterSize // 2 + 11, y),(x + thrusterSize // 2 + 113, y),(x + thrusterSize - 15, y))
            pygame.draw.rect(
                rov, LGREY, (x, (thrusterSize+y)-per, thrusterSize, per))

            rov.blit(pygame.transform.flip(leftFront, k, 0), (x, y))

            # Define the offsets for the lines
            offsets = {
                "rear": [
                    (-6, -65),
                    (1, -54),
                    (2, -40),
                    (40, -2),
                    (54, 1),
                    (65, 6)
                ],
                "front": [
                    (-50, -15),
                    (-43, -8),
                    (-36, -1),
                    (0, 35),
                    (7, 42),
                    (14, 49)
                ]
            }

            max = math.floor(int(per)/6)

            if (float(data[i]) < 0):
                for x_offset, y_offset in offsets["rear"]:
                    startPos = (
                        rearTipCoord[0] + x_offset - k * (x_offset * 2), rearTipCoord[1] + y_offset)
                    endPos = (startPos[0] - max + k *
                              (max * 2), startPos[1] + max)
                    pygame.draw.line(rov, BLACK, startPos, endPos, 3)

            if (float(data[i]) > 0):
                for x_offset, y_offset in offsets["front"]:
                    startPos = (
                        frontTipCoord[0] + x_offset - k * (x_offset * 2), frontTipCoord[1] + y_offset)
                    endPos = (startPos[0] + max - k *
                              (max * 2), startPos[1] - max)
                    pygame.draw.line(rov, BLACK, startPos, endPos, 3)

            window.blit(rov, (X, Y))
            i = i + 1





def wrap_angle(angle):
    angle = angle % 360
    if angle > 180:
        angle -= 360
    return angle


def draw_artificial_horizon(roll, pitch, yaw):
    surface_size = (500, 300)
    surface = pygame.Surface(surface_size)
    surface.fill(SKY)

    radius = 150
    center = (radius, radius)
    oversize = radius * 5
    pitch_offset = int(pitch * 2)

    # Sky & ground
    horizon = pygame.Surface((oversize, oversize), pygame.SRCALPHA)
    pygame.draw.rect(horizon, BLUE, (0, 0, oversize,
                     oversize // 2 + pitch_offset))
    pygame.draw.rect(horizon, BROWN, (0, oversize // 2 +
                     pitch_offset, oversize, oversize))
    pygame.draw.line(horizon, BLACK, (0, oversize // 2 + pitch_offset),
                     (oversize, oversize // 2 + pitch_offset), 4)

    # Rotate and mask
    rotated = pygame.transform.rotate(horizon, -roll)
    rotated_rect = rotated.get_rect(center=center)

    circular_surface = pygame.Surface(
        (radius * 2, radius * 2), pygame.SRCALPHA)
    mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255), center, radius)
    circular_surface.blit(rotated, rotated_rect)
    circular_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

    # Paste to modular surface
    surface.blit(circular_surface, (0, 0))
    pygame.draw.circle(surface, BLACK, center, radius, 4)

    # Red cross
    pygame.draw.line(surface, RED, (radius - 20, radius),
                     (radius + 20, radius), 2)
    pygame.draw.line(surface, RED, (radius, radius - 20),
                     (radius, radius + 20), 2)

    # Yaw compass
    pygame.draw.circle(surface, BLACK, (350, 250), 50, 2)
    yaw_rad = math.radians(yaw)
    end_x = 350 + 40 * math.sin(yaw_rad)
    end_y = 250 - 40 * math.cos(yaw_rad)
    pygame.draw.line(surface, GREEN, (350, 250), (end_x, end_y), 3)
    pygame.draw.circle(surface, RED, (int(end_x), int(end_y)), 5)

    # Text
    surface.blit(font.render(f"Roll: {int(roll)}°", True, BLACK), (300, 10))
    surface.blit(font.render(f"Pitch: {int(pitch)}°", True, BLACK), (300, 40))
    surface.blit(font.render(f"Yaw: {int(yaw)}°", True, BLACK), (300, 70))

    return surface


def main(roll, pitch, yaw, joy):

    window.fill(SKY)

    joyX = -round(joy.get_axis(0), 3)
    joyY = round(joy.get_axis(1), 3)
    twist = apply_deadzone(-round(joy.get_axis(2), 3), 0.35, 0.35)
    slider = round(joy.get_axis(3), 3)
    """
    joyX = 0.5
    joyY = 0.8
    twist = 0
    slider = 0
    """
    theta = math.atan2(apply_deadzone(joyY, deadzoneY, deadzoneY),
                        apply_deadzone(joyX, deadzoneX, deadzoneX))
    power = math.hypot(apply_deadzone(joyX, deadzoneX, deadzoneX),
                        apply_deadzone(joyY, deadzoneY, deadzoneY))

    sin = math.sin(theta - math.pi/4)
    cos = math.cos(theta - math.pi/4)
    maximum = max(abs(sin), abs(cos))

    assert(maximum != 0)
    leftFront = power * (cos/maximum) + twist
    rightFront = power * (sin/maximum) - twist
    leftBack = power * (sin/maximum) + twist
    rightBack = power * (cos/maximum) - twist

    if power + abs(twist) > 1:
        assert(power + abs(twist) != 0)
        leftFront /= power + abs(twist)
        rightFront /= power + abs(twist)
        leftBack /= power + abs(twist)
        rightBack /= power + abs(twist)

    
    data = (map_range(joyX, -1, 1, 1024, 0), map_range(joyY, -
            1, 1, 0, 1024), map_range(twist, -1, 1, 256, 0), map_range(slider, -1, 1, 0, 512))

    # x = (x + 1) % size
    # window.fill(WHITE)

    drawROV(100, 0, (leftFront, rightFront, leftBack, rightBack))
    # pygame.draw.rect(window, BLACK, (100,100,375,500), 3, 3)

    # text_surface = my_font.render('30', False, BLACK)
    # thruster.blit(text_surface, (40,30))

    # data = (dataList[0], dataList[1], dataList[2])

    
    draw_polar(getMarkerCoord('polar', data))
    draw_grid(getMarkerCoord('grid', data))
    draw_slider(getMarkerCoord('slider',data))

    roll = np.clip(roll, -180, 180)
    pitch = np.clip(pitch, -180, 180)
    yaw = np.clip(yaw, -180, 180)

    horizon_surface = draw_artificial_horizon(roll, pitch, yaw)
    window.blit(horizon_surface, (100, 500))  # Position the horizon widget

    pygame.display.flip()
    # pygame.time.delay(100)
    clock.tick(30)



if __name__ == "__main__":
    pygame.init()
    pygame.joystick.init()

    joy = pygame.joystick.Joystick(0)
    joy.init()
    main(0,0,0,joy)
