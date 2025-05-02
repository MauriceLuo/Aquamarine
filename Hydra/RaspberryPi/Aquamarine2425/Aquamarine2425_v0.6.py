##########################################
#  This is the visualiation of ROV data  #
# Made by Jason Ho on Oct 3, 2024, 19:06 #
##########################################


# Import libraries
import pygame
import sys
import serial
import time
import math

# Initialize Pygame and fonts
pygame.init()
pygame.font.init()
pygame.display.set_caption("This took half a day's worth of life away from me")

my_font = pygame.font.SysFont("Comic Sans MS", 30)

window = pygame.display.set_mode((2240, 800))

# Init thruster png
thruster = pygame.image.load("thruster.png")
pygame.Surface.convert_alpha(thruster)

# Init the joystick
pygame.joystick.init()

print(pygame.joystick.get_count())

joy = pygame.joystick.Joystick(0)
joy.init()

print(f"{joy.get_name()} is connected")


# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
grey = (170, 170, 170)
Dgrey = (140, 140, 140)
Lgrey = (200, 200, 200)

deadzoneX = 0.1
deadzoneY = 0.1

# -----------------PyGame inilisation complete-----------------#


previous_time = time.time()


testLoop = True
print("Intialising PySerial, please wait...")


print(f"Initialised in {round(time.time() - previous_time, 2)} seconds.")
time.sleep(2)

# -----------------PySerial inilisation complete-----------------#


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


def apply_deadzone(input_value, deadzone=0.02):
    """
    Applies a deadzone to the input value, mapping values outside the deadzone
    to the range [-1, 0] or [0, 1].

    input_value: The input value to process (expected range: -1.00 to 1.00).
    deadzone: The range of the deadzone (default: 0.02).

    Returns:
        The adjusted value after applying the deadzone.
    """
    if -deadzone <= input_value <= deadzone:
        # Inside the deadzone
        return 0.0
    elif input_value > deadzone:
        # Above the deadzone, map to the range [0, 1]
        return map_value(input_value, deadzone, 1.00, 0.0, 1.00)
    elif input_value < -deadzone:
        # Below the deadzone, map to the range [0, -1]
        return map_value(input_value, -1.00, -deadzone, -1.00, 0.0)

# Function to draw the grid


def draw_grid(markerCoord):

    graphSize = 512
    graphSurface = pygame.Surface((graphSize, graphSize))
    graphPosition = (1500, 200)

    mult = graphSize/1024

    horMin = graphSize//2 * (1-deadzoneX)
    horMax = graphSize//2 * (1+deadzoneX)

    verMin = graphSize//2 * (1-deadzoneY)
    verMax = graphSize//2 * (1+deadzoneY)

    graphSurface.fill(white)

    # Gray out specific areas

    pygame.draw.rect(graphSurface, Lgrey,
                     (0, horMin, graphSize, horMax-horMin))
    pygame.draw.rect(graphSurface, Lgrey,
                     (verMin, 0, verMax-verMin, graphSize))
    pygame.draw.rect(graphSurface, Dgrey,
                     (verMin, horMin, verMax-verMin, horMax-horMin))

    # Draw minor gridlines
    for i in range(int(64*mult), graphSize, int(64*mult)):
        pygame.draw.line(graphSurface, grey, (i, 0), (i, graphSize))
        pygame.draw.line(graphSurface, grey, (0, i), (graphSize, i))

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
    window.blit(graphSurface, graphPosition)


def draw_polar(markerCoord):

    polarSize = 256  # diameter
    polarSurface = pygame.Surface((polarSize, polarSize))
    polarSurface.fill(white)
    mult = polarSize / 256

    centre = (polarSize // 2, polarSize // 2)

    max_radius = polarSize/2

    pygame.draw.circle(polarSurface, Lgrey, centre, max_radius, 2)

    sub_arc_num = 4
    for radius in range(0, int(max_radius), int(max_radius/sub_arc_num)):
        pygame.draw.circle(polarSurface, Lgrey, centre, radius, 1)

    pygame.draw.rect(polarSurface, white,
                     (0, polarSize // 2, polarSize, polarSize))

    for deg in range(0, 181, 30):

        x = math.floor(polarSize // 2+max_radius*math.cos(math.radians(deg)))
        y = math.ceil(polarSize // 2-max_radius*math.sin(math.radians(deg)))
        pygame.draw.line(polarSurface, Lgrey, centre, (x, y), 1)

    # Draw marker

    x = map_value(markerCoord, 0, 256, -max_radius*0.75, max_radius*0.75)
    y = int(math.sqrt(pow(max_radius*0.75, 2)-pow(x, 2)))
    print(x, y)

    pygame.draw.circle(polarSurface, red, (x+max_radius, max_radius-y), 5)

    window.blit(polarSurface, (1200, 200))


def getMarkerCoord(type, data):
    if type == 'grid':
        x = float(data[0])
        y = float(data[1])

        return ((x, y))

    if type == 'polar':
        return (float(data[2]))


def drawROV(X, Y, size, data):
    # X and Y are values denoting the coordinates of the ROV
    # size should be a value denoting the size of the ROV
    # data should be an array with 4 values ranging from -1.00~1.00
    rov = pygame.Surface((size, size))
    rov.fill(white)

    thrusterSize = 128
    mult = thrusterSize/256

    leftFront = pygame.transform.scale_by(thruster, mult)

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
                rov, Lgrey, (x, (thrusterSize+y)-per, thrusterSize, per))

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
                    pygame.draw.line(rov, black, startPos, endPos, 3)

            if (float(data[i]) > 0):
                for x_offset, y_offset in offsets["front"]:
                    startPos = (
                        frontTipCoord[0] + x_offset - k * (x_offset * 2), frontTipCoord[1] + y_offset)
                    endPos = (startPos[0] + max - k *
                              (max * 2), startPos[1] - max)
                    pygame.draw.line(rov, black, startPos, endPos, 3)

            window.blit(rov, (X, Y))
            i = i + 1

# Main loop


def main():

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        joyX = -round(joy.get_axis(0), 3)
        joyY = round(joy.get_axis(1), 3)
        twist = apply_deadzone(-round(joy.get_axis(2), 3), 0.05)
        slider = round(joy.get_axis(3), 3)

        theta = math.atan2(apply_deadzone(joyY, deadzoneY),
                           apply_deadzone(joyX, deadzoneX))
        power = math.hypot(apply_deadzone(joyX, deadzoneX),
                           apply_deadzone(joyY, deadzoneY))

        sin = math.sin(theta - math.pi/4)
        cos = math.cos(theta - math.pi/4)
        maximum = max(abs(sin), abs(cos))

        leftFront = power * (cos/maximum) + twist
        rightFront = power * (sin/maximum) - twist
        leftBack = power * (sin/maximum) + twist
        rightBack = power * (cos/maximum) - twist

        if power + abs(twist) > 1:
            leftFront /= power + abs(twist)
            rightFront /= power + abs(twist)
            leftBack /= power + abs(twist)
            rightBack /= power + abs(twist)

        print(f"{leftFront}, {rightFront}, {leftBack}, {rightBack}")
        time.sleep(0.05)

        data = (map_value(joyX, -1, 1, 1024, 0), map_value(joyY, -
                1, 1, 0, 1024), map_value(twist, -1, 1, 256, 0))

        # x = (x + 1) % size
        window.fill(white)

        drawROV(100, 100, 500, (leftFront, rightFront, leftBack, rightBack))

        # text_surface = my_font.render('30', False, black)
        # thruster.blit(text_surface, (40,30))

        # data = (dataList[0], dataList[1], dataList[2])

        draw_grid(getMarkerCoord('grid', data))
        draw_polar(getMarkerCoord('polar', data))

        # draw_point(x, y)
        pygame.display.flip()
        # pygame.time.delay(100)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
