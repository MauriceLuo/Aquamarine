import pygame
import time

pygame.init()  # joystick already initialized here
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
joy = pygame.joystick.Joystick(0)
joy.init()

print(f"Available joysticks: {pygame.joystick.get_count()}")
print(f"Initialized joysticks: {joysticks}")

running = True
while running:
    pygame.event.get()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYAXISMOTION:
            print(f"Axis moving: {event}")
        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Button: {event}")
        if event.type == pygame.JOYHATMOTION:
            print(f"Hat: {event}") 
    
