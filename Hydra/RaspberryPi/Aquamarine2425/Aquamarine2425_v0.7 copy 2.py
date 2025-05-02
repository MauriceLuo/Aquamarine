##########################################
#  This is the visualiation of ROV data  #
# Made by Jason Ho on Apr 21, 2025, 00:10 #
##########################################

# Import libraries
import pygame
import sys
import math

# Initialize Pygame and fonts
pygame.init()
pygame.font.init()
pygame.display.set_caption("Optimized ROV Visualization")
clock = pygame.time.Clock()

my_font = pygame.font.SysFont("Comic Sans MS", 30)
window = pygame.display.set_mode((0, 0), flags=pygame.RESIZABLE, depth=24)

# Init thruster png
thruster = pygame.image.load("thrusterUPDATED.png")
thruster = pygame.Surface.convert_alpha(thruster)

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
grey = (170, 170, 170)
Dgrey = (140, 140, 140)
Lgrey = (200, 200, 200)
sky = (246, 255, 255)

deadzoneX = 0.25
deadzoneY = 0.25

# Pre-create surfaces
graphSize = 512
graphSurface = pygame.Surface((graphSize, graphSize))
polarSize = 256
polarSurface = pygame.Surface((polarSize, polarSize))
rovSurface = pygame.Surface((375, 500))

# Load and scale background once
bg = pygame.transform.scale(pygame.image.load("rovbg.jpeg"),
                            (pygame.display.get_window_size()[0],
                             pygame.display.get_window_size()[1]))


def map_value(value, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def apply_deadzone(input_value, deadzone=0.02):
    """Applies a deadzone to the input value"""
    if -deadzone <= input_value <= deadzone:
        return 0.0
    elif input_value > deadzone:
        return map_value(input_value, deadzone, 1.00, 0.0, 1.00)
    else:
        return map_value(input_value, -1.00, -deadzone, -1.00, 0.0)


def draw_grid(markerCoord):
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
    step = int(64*mult)
    for i in range(step, graphSize, step):
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
    window.blit(graphSurface, (800, 200))


def draw_polar(markerCoord):
    mult = polarSize / 256
    centre = (polarSize // 2, polarSize // 2)
    max_radius = polarSize/2

    polarSurface.fill(sky)
    pygame.draw.circle(polarSurface, white, centre, max_radius)
    pygame.draw.circle(polarSurface, Lgrey, centre, max_radius, 2)

    sub_arc_num = 4
    radius_step = int(max_radius/sub_arc_num)
    for radius in range(0, int(max_radius), radius_step):
        pygame.draw.circle(polarSurface, Lgrey, centre, radius, 1)

    pygame.draw.rect(polarSurface, sky,
                     (0, polarSize // 2, polarSize, polarSize))

    for deg in range(0, 181, 30):
        x = math.floor(polarSize // 2+max_radius*math.cos(math.radians(deg)))
        y = math.ceil(polarSize // 2-max_radius*math.sin(math.radians(deg)))
        pygame.draw.line(polarSurface, Lgrey, centre, (x, y), 1)

    # Draw marker
    x = map_value(markerCoord, 0, 256, -max_radius*0.75, max_radius*0.75)
    y = int(math.sqrt(pow(max_radius*0.75, 2)-pow(x, 2)))
    pygame.draw.circle(polarSurface, red, (x+max_radius, max_radius-y), 5)

    window.blit(polarSurface, (500, 200))


def getMarkerCoord(type, data):
    if type == 'grid':
        return (data[0], data[1])
    if type == 'polar':
        return float(data[2])


# Pre-compute thruster parameters
thrusterSize = 128
mult = thrusterSize/256
leftFront = pygame.transform.scale(thruster, (thrusterSize, thrusterSize))

# Pre-compute offsets for thruster lines
rear_offsets = [
    (-6, -65), (1, -54), (2, -40),
    (40, -2), (54, 1), (65, 6)
]
front_offsets = [
    (-50, -15), (-43, -8), (-36, -1),
    (0, 35), (7, 42), (14, 49)
]


def drawROV(X, Y, size, data):
    rovSurface.fill(sky)

    positions = [(100, 20), (100, 220), (300, 20), (300, 220)]

    for i, (y, x) in enumerate(positions):
        k = 0 if (y == 100 and x == 20) or (y == 300 and x == 220) else 1
        per = abs(float(data[i])*thrusterSize)

        frontTipCoord = (x+220 * mult + k *
                         (thrusterSize - 440 * mult), y+40 * mult)
        rearTipCoord = (x+24 * mult + k *
                        (thrusterSize - 48 * mult), y+234 * mult)

        # Draw thrust indicator rectangle
        pygame.draw.rect(rovSurface, Lgrey,
                         (x, (thrusterSize+y)-per, thrusterSize, per))

        # Draw thruster
        rovSurface.blit(pygame.transform.flip(leftFront, k, 0), (x, y))

        max_line = math.floor(int(per)/6)

        # Draw thrust lines
        if (float(data[i]) < 0):
            for x_offset, y_offset in rear_offsets:
                startPos = (rearTipCoord[0] + x_offset - k *
                            (x_offset * 2), rearTipCoord[1] + y_offset)
                endPos = (startPos[0] - max_line + k *
                          (max_line * 2), startPos[1] + max_line)
                pygame.draw.line(rovSurface, black, startPos, endPos, 3)

        if (float(data[i]) > 0):
            for x_offset, y_offset in front_offsets:
                startPos = (
                    frontTipCoord[0] + x_offset - k * (x_offset * 2), frontTipCoord[1] + y_offset)
                endPos = (startPos[0] + max_line - k *
                          (max_line * 2), startPos[1] - max_line)
                pygame.draw.line(rovSurface, black, startPos, endPos, 3)

    window.blit(rovSurface, (X, Y))


def main():
    window.blit(bg, (0, 0))
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simulate joystick input
        joyX = 0.7
        joyY = 0
        twist = 0
        slider = 0

        theta = math.atan2(apply_deadzone(joyY, deadzoneY),
                           apply_deadzone(joyX, deadzoneX))
        power = math.hypot(apply_deadzone(joyX, deadzoneX),
                           apply_deadzone(joyY, deadzoneY))

        sin = math.sin(theta - math.pi/4)
        cos = math.cos(theta - math.pi/4)
        maximum = max(abs(sin), abs(cos))

        if maximum == 0:  # Handle division by zero
            maximum = 1

        leftFront = power * (cos/maximum) + twist
        rightFront = power * (sin/maximum) - twist
        leftBack = power * (sin/maximum) + twist
        rightBack = power * (cos/maximum) - twist

        if power + abs(twist) > 1:
            divisor = power + abs(twist)
            leftFront /= divisor
            rightFront /= divisor
            leftBack /= divisor
            rightBack /= divisor

        # Generate data for visualization
        data = (
            map_value(joyX, -1, 1, 1024, 0),
            map_value(joyY, -1, 1, 0, 1024),
            map_value(twist, -1, 1, 256, 0)
        )

        # Draw components
        window.blit(bg, (0, 0))
        drawROV(100, 100, 500, (leftFront, rightFront, leftBack, rightBack))
        draw_grid(getMarkerCoord('grid', data))
        draw_polar(getMarkerCoord('polar', data))

        pygame.display.flip()
        clock.tick(60)
        print(clock.get_fps())

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
