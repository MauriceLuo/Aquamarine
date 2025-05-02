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
blue = (0, 0, 255)
gray = (170, 170, 170)
Lgray = (200,200,200)

deadzoneHor = (450,574)
deadzoneVer = (400,624)


import serial
import time

ser = serial.Serial('/dev/tty.usbserial-1220', baudrate = 115200, timeout = 1)
time.sleep(3)
numPoints = 1
dataList = [0]*numPoints

def getValues():
    
    ser.write(b'g')
    arduinoData = ser.readline().decode().split('\r\n')
    
    
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
    
    per = float(dataList[2])
    thrusterSize = 128
    mult = thrusterSize/256
    thruster = thrusterIdle
    
               
    if per > 128:
        per = 128
    
    
        
    leftFront = pygame.transform.scale_by(thruster, mult)
    rightFront = pygame.transform.flip(pygame.transform.scale_by(thruster, mult), 1,0)
    leftRear = rightFront
    rightRear = leftFront
    """
    for j in [100, 300]:  # Iterate over the desired y-values
        for i in [20, 220]:  # Iterate over the desired x-values
            for k in [1, -1]:
                lines = ((x + thrusterSize // 2, y+5), (x + thrusterSize // 2 + 11*k, y + 15), (x + 5, y+thrusterSize // 2), (x + thrusterSize + 15*k, y + thrusterSize // 2 - 11))
    """
    for y in [100, 300]:
        for x in [20, 220]:
            k = 0 if (y == 100 and x == 20) or (y == 300 and x == 220) else 1
            
            frontTipCoord = (x+220 * mult+ k*(thrusterSize - 440* mult), y+40* mult)
            rearTipCoord = (x+24* mult+ k*(thrusterSize - 48* mult),y+234* mult)
    
            
            #lines = ((x + thrusterSize // 2, y),(x + thrusterSize // 2 + 11, y),(x + thrusterSize // 2 + 113, y),(x + thrusterSize - 15, y))
            pygame.draw.rect(rov, Lgray, (x, (thrusterSize+y)-per, thrusterSize, per))
            
            
            rov.blit(pygame.transform.flip(leftFront, k, 0), (x,y))
            
            
            # Define the offsets for the circles
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

            # Draw rear circles
            if (int(dataList[2]) > 20):
                
                max = math.floor(int(dataList[2])/8)
                
                #for back thurst
                for x_offset, y_offset in offsets["rear"]:
                    startPos = (rearTipCoord[0] + x_offset - k * (x_offset * 2), rearTipCoord[1] + y_offset)
                    endPos = (startPos[0] -  max + k * (max * 2), startPos[1] + max)
                    pygame.draw.line(rov, black, startPos, endPos, 3)
                """
                #for front thrust
                for x_offset, y_offset in offsets["front"]:
                    startPos = (frontTipCoord[0] + x_offset - k * (x_offset * 2), frontTipCoord[1] + y_offset)
                    endPos = (startPos[0] + max - k * (max * 2), startPos[1] - max)
                    pygame.draw.line(rov, black, startPos, endPos, 3)
                        

                """ 
    
            window.blit(rov, (X,Y))

#pygame.event.get()

# Main loop
def main():
    

    running = True
    while running:
        getArduino()

        print(dataList)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
       


        #x = (x + 1) % size
        window.fill(white)
    
        
        #drawROV(300,300,500)
        
        
        #text_surface = my_font.render('30', False, black)
        #thruster.blit(text_surface, (40,30))
    
        
        
        #draw_grid(getMarkerCoord('grid'))
        #draw_polar(getMarkerCoord('polar'))
        
        #draw_point(x, y)
        pygame.display.flip()
        #pygame.time.delay(100)
        
        
        
            

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


