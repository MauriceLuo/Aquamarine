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
thrusterIdle = pygame.image.load("thruster.png")
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
Lgray = (200,200,200)

deadzoneHor = (450,574)
deadzoneVer = (400,624)


import serial
import time

ser = serial.Serial('/dev/tty.usbserial-1220', baudrate = 9600, timeout = 1)
time.sleep(3)


numPoints = 5
dataList = [0]*numPoints

def getValues():
    ser.write(b'g')
    arduinoData = ser.readline().decode().split('\r\n')
    if arduinoData[0] == '':
        arduinoData[0] = 0
    
    int(math.ceil(arduinoData[0]))    
    return arduinoData[0]

def getArduino():
    for i in range(0,numPoints):
        data = getValues()
        dataList[i] = data

    return(dataList)

# Function to draw the grid
def draw_grid(markerCoord):
    
    graphSize = 512
    graphSurface = pygame.Surface((graphSize, graphSize))
    graphPosition = (1500,200)
    
    mult = graphSize/1024
    
    horMin = deadzoneHor[0]*mult
    horMax = (deadzoneHor[1]-deadzoneHor[0])*mult
    
    verMin = deadzoneVer[0]*mult
    verMax = (deadzoneVer[1]-deadzoneVer[0])*mult
    
    graphSurface.fill(white)

    # Gray out specific areas

    pygame.draw.rect(graphSurface, Lgray, (0, horMin, graphSize, horMax))
    pygame.draw.rect(graphSurface, Lgray, (verMin,0 , verMax, graphSize))
    
    # Draw minor gridlines
    for i in range(int(64*mult), graphSize, int(64*mult)):
        pygame.draw.line(graphSurface, gray, (i, 0), (i, graphSize))
        pygame.draw.line(graphSurface, gray, (0, i), (graphSize, i))

    # Draw axes
    pygame.draw.line(graphSurface, black, (0, graphSize // 2), (graphSize, graphSize // 2), 1)
    pygame.draw.line(graphSurface, black, (graphSize // 2, 0), (graphSize // 2, graphSize), 1)
    pygame.draw.rect(graphSurface, black, (0,0,graphSize,graphSize), 1)
    
    # Draw marker
    
    x = int(markerCoord[0]*mult)
    y = int(markerCoord[1]*mult)
    
    pygame.draw.circle(graphSurface, red, (x, y), 5)
    
    print(x,y, horMin, horMax)
    window.blit(graphSurface, graphPosition)
"""
    if(y>horMax+horMin or y< horMin):
        if(x>verMax+verMin or x < verMin):
        
         pygame.draw.line(graphSurface, red, (graphSize // 2,graphSize // 2),(x, y),2)
""" 
    



def draw_polar(markerCoord):
    
    polarSize = 256
    polarSurface = pygame.Surface((polarSize, polarSize))
    polarSurface.fill(white)
    mult = polarSize / 512



    centre = (polarSize //2 ,polarSize //2)

    max_radius = 256*mult

    pygame.draw.circle(polarSurface,Lgray,centre, max_radius, 2)

    sub_arc_num = 4
    for radius in range(0, int(max_radius), int(max_radius/sub_arc_num)):
        pygame.draw.circle(polarSurface,Lgray, centre, radius, 1)

    pygame.draw.rect(polarSurface, white, (0, polarSize // 2, polarSize, polarSize))

    for deg in range(0, 181, 30):

        x = math.floor(polarSize //2+max_radius*math.cos(math.radians(deg)))
        y = math.ceil(polarSize //2-max_radius*math.sin(math.radians(deg)))
        pygame.draw.line(polarSurface,Lgray,centre, (x, y), 1)

    # Draw marker
    
    x = (markerCoord*1.50588 + 64)*mult
    y = 256*mult -int(math.sqrt(pow(max_radius*0.75,2)-pow(x-max_radius,2)))
    
    pygame.draw.circle(polarSurface, red, (x, y), 5)

    window.blit(polarSurface, (1200,200))
    
    
def getMarkerCoord(type):
    if type == 'grid':
        return((float(dataList[0]), float(dataList[1])))
    
    if type == 'polar':
        return(float(dataList[2]))
    
    
    
def drawROV(X, Y, size):
    rov = pygame.Surface((size,size))
    rov.fill(white)
    
    per = int(dataList[2])
    thrusterSize = 128
    mult = thrusterSize/256
    thruster = thrusterIdle
    
               
    if per > 128:
        per = 128
        
    leftFront = pygame.transform.scale_by(thruster, mult)
    rightFront = pygame.transform.flip(pygame.transform.scale_by(thruster, mult), 1,0)
    leftRear = rightFront
    rightRear = leftFront
    
    
    x,y = 20, 100
    
    lines = ((x + thrusterSize // 2, y+5),(x + thrusterSize // 2 + 11, y + 15),(x + thrusterSize - 5, y + thrusterSize // 2),(x + thrusterSize - 15, y + thrusterSize// 2 - 11))
    pygame.draw.rect(rov, Lgray, (x, (thrusterSize+y)-per, thrusterSize, per))
    rov.blit(leftFront, (x,y))

    
    if per > 20:
        pert = per - 20
        
        pygame.draw.line(rov,black,lines[0], (lines[0][0]+math.floor(pert/4), lines[0][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[1], (lines[1][0]+math.floor(pert/4), lines[1][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[2], (lines[2][0]+math.floor(pert/4), lines[2][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[3], (lines[3][0]+math.floor(pert/4), lines[3][1] - math.floor(pert/4)), 4)

    
    x,y = 220, 100
    lines = ((x + thrusterSize // 2, y+5),(x + thrusterSize // 2 - 11, y + 15),(x + 5, y + thrusterSize // 2),(x + 15, y + thrusterSize// 2 - 11))
    pygame.draw.rect(rov, Lgray, (x, (thrusterSize+y)-per, thrusterSize, per))
    rov.blit(rightFront, (x,y))
    
    if per > 20:
        pert = per - 20
        
        pygame.draw.line(rov,black,lines[0], (lines[0][0]-math.floor(pert/4), lines[0][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[1], (lines[1][0]-math.floor(pert/4), lines[1][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[2], (lines[2][0]-math.floor(pert/4), lines[2][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[3], (lines[3][0]-math.floor(pert/4), lines[3][1] - math.floor(pert/4)), 4)


    x,y = 20, 300
    lines = ((x + thrusterSize // 2, y+5),(x + thrusterSize // 2 - 11, y + 15),(x + 5, y + thrusterSize // 2),(x + 15, y + thrusterSize// 2 - 11))
    pygame.draw.rect(rov, Lgray, (x, (thrusterSize+y)-per, thrusterSize, per))
    rov.blit(leftRear, (x,y))
    
    if per > 20:
        pert = per - 20
        
        pygame.draw.line(rov,black,lines[0], (lines[0][0]-math.floor(pert/4), lines[0][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[1], (lines[1][0]-math.floor(pert/4), lines[1][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[2], (lines[2][0]-math.floor(pert/4), lines[2][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[3], (lines[3][0]-math.floor(pert/4), lines[3][1] - math.floor(pert/4)), 4)

    
    x,y = 220, 300
    lines = ((x + thrusterSize // 2, y+5),(x + thrusterSize // 2 + 11, y + 15),(x + thrusterSize - 5, y + thrusterSize // 2),(x + thrusterSize - 15, y + thrusterSize// 2 - 11))
    pygame.draw.rect(rov, Lgray, (x, (thrusterSize+y)-per, thrusterSize, per))
    rov.blit(rightRear, (x,y))
    
    if per > 20:
        pert = per - 20
        
        pygame.draw.line(rov,black,lines[0], (lines[0][0]+math.floor(pert/4), lines[0][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[1], (lines[1][0]+math.floor(pert/4), lines[1][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[2], (lines[2][0]+math.floor(pert/4), lines[2][1] - math.floor(pert/4)), 4)
        pygame.draw.line(rov,black,lines[3], (lines[3][0]+math.floor(pert/4), lines[3][1] - math.floor(pert/4)), 4)

    
    
    window.blit(rov, (X,Y))
        
# Main loop
def main():
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        #x = (x + 1) % size
        window.fill(white)
    
        
        drawROV(100,100,500)
        
        #pygame.Surface.convert_alpha(thruster)
        #text_surface = my_font.render('30', False, black)
        #thruster.blit(text_surface, (40,30))
    
        
        
        draw_grid(getMarkerCoord('grid'))
        draw_polar(getMarkerCoord('polar'))
        
        #draw_point(x, y)
        pygame.display.flip()
        #pygame.time.delay(100)
        
        getArduino()
        print(dataList[2])
            

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


