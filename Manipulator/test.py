import pygame

pygame.init()  # joystick already initialized here
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
ps3 = pygame.joystick.Joystick(0)
ps3.init()

print(f"Available joysticks: {pygame.joystick.get_count()}")
print(f"Initialized joysticks: {joysticks}")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYAXISMOTION:
            print(f"Axis moving: {event}")
        if event.type == pygame.JOYBUTTONDOWN:
            print(f"Button: {event}")
        if event.type == pygame.JOYHATMOTION:
            print(f"Hat: {event}")
    # print(ps3.get_hat(0))

"""
左左右： 0 左-1 右1
左上下： 1 上-1 下1
右左右： 2 左-1 右1
右上下： 3 上-1 下1
左扳机： 4 原始-1 按下1
右扳机： 5 原始-1 按下1



按键：
        3
    2       1
        0

hat(0):
                (0,1)

    (-1,0)               (1,0)

                (0,-1)

"""