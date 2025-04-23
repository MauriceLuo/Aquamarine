import pygame
import time
import subprocess

pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())

ps3 = pygame.joystick.Joystick(0)
ps3.init()
print(ps3.get_numhats())

def clear() -> None:
    command = ['cmd']
    args = ['/c','cls']
    cli = command + args
    subprocess.run(cli)
    return None

while True:
    clear()
    pygame.event.get()
    print(f"{ps3.get_hat(0)}/n")
    print(ps3.get_hat(0)[1])
    time.sleep(0.05)