import serial
import time
import pygame
import sys
ser = serial.Serial('/dev/tty.usbserial-1220', baudrate = 115200, timeout = 1)
time.sleep(3)
numPoints = 8
dataList = [0]*numPoints
pygame.init()
pygame.font.init()
pygame.display.set_caption("This took half a day's worth of life away from me")

# Set up display with a size of 1023x1023

window = pygame.display.set_mode((20, 20))

running = True

from queue import Queue

# Add this at the beginning of the script
data_queue = Queue()

def read_serial():
    while running:
        if ser.is_open:
            try:
                ser.write(b'g')
                data = ser.readline().decode().strip()
                if data:
                    data_queue.put(data)
            except serial.SerialException as e:
                print(f"Serial error: {e}")

# In the Pygame loop, retrieve data from the queue
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    while not data_queue.empty():
        data = data_queue.get()
        print(f"Received: {data}")

    pygame.display.flip()