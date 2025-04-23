"""

Maestro Channel PWM Range

Wrist:
- Min = 608 µs (170º)
- Level = 702.50 µs (115º)
- Max = 2000 µs

Arm:
- Min = 702 µs (0º)
- Max = 2000 µs

Mani:
- Opened = 800~900 µs
- Closed = 1600 µs

"""


import pygame
import time
import sys

axis_y = 0
axis_x = 0
# global arm     #degree: 0 <= arm <= 260
# global wrist   #degree: 0 <= wrist <= 170
deadzone_min = -0.1
deadzone_max = 0.1
arm = 0
wrist = 115
offset = 0
offset_max = 55
offset_min = -115
arm_max = 158.4590517
arm_min = 0
wrist_max = 170
wrist_min = 0
arm_pwm = 0
wrist_pwm = 0
mani = 0
mani_max = 90       #mani角度，这里不确定是不是90度
mani_min = 0
mani_pwm = 0
rotate = 0
rotate_min = -90    #这里也是
rotate_max = 90     #还有这里
rotate_pwm = 1500   #加上这里

rotate_axis = 0
arm_axis = 1
wrist_up_button = 2
wrist_down_buttom = 3

pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())

ps3 = pygame.joystick.Joystick(0)
ps3.init()

print(ps3.get_numhats())
print(ps3.get_numbuttons())
print(ps3.get_numaxes())

def constrain(input,maximum,minimum):
    # global arm     #degree: 0 <= arm <= 260
    # global wrist   #degree: 0 <= wrist <= 170
    # if arm >= 0 and arm <= 260 and wrist >= 0 and wrist <= 170:
    #     return
    # if arm < 0:
    #     arm = 0
    # if arm > 260:
    #     arm = 260
    # if wrist < 0:
    #     wrist = 0
    # if wrist >170:
    #     wrist = 170
    output = max(minimum,min(maximum,input))
    return output
    # if arm == 0:
    #     wrist = 115
    # if arm >= 170:
    #     wrist = 170

def map_range(x, in_min, in_max, out_min, out_max):
    """Maps a value from one range to another."""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def deadzoneNormalise(input_value, minimum, maximum):
    """
    Applies a deadzone to the input value. Values between `minimum` and `maximum` are set to 0.
    Values below `minimum` are mapped from [-1.0, minimum] to [-1.0, 0].
    Values above `maximum` are mapped from [maximum, 1.0] to [0, 1.0].
    """
    if minimum < -1.0 or maximum > 1.0 or minimum >= maximum:
        raise ValueError("Invalid minimum or maximum range")
    
    if minimum <= input_value <= maximum:
        return 0.0
    elif input_value < minimum:
        return float(map_range(input_value, -1.0, minimum, -1.0, 0.0))
    else:  # input_value > maximum
        return float(map_range(input_value, maximum, 1.0, 0.0, 1.0))

def deadzone(x):
    if x >= deadzone_min and x <= deadzone_max:
        return 0
    else:
        return x

while True:
    pygame.event.get()      #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # if ps3.get_button(wrist_up_button):
    #     offset += 1
    # if ps3.get_button(wrist_down_buttom):
    #     offset -= 1
    offset += ps3.get_hat(0)[1]
    mani += ps3.get_hat(0)[0]
    mani = constrain(mani,mani_max,mani_min)
    mani_pwm = map_range(mani,mani_min,mani_max,850,1600)
    axis_y = deadzoneNormalise(round(ps3.get_axis(arm_axis),2),deadzone_min,deadzone_max)
    axis_x = deadzoneNormalise(round(ps3.get_axis(rotate_axis),2),deadzone_min,deadzone_max)
    rotate += axis_x*10
    rotate = constrain(rotate,rotate_max,rotate_min)
    rotate_pwm = map_range(rotate,rotate_min,rotate_max,1000,2000)  #这里不确定后面两个的数值，需要看底板的servo做修改
    # offset = constrain(offset, offset_max,offset_min)
    arm += axis_y*10
    arm = constrain(arm,arm_max,arm_min)
    wrist = arm_max - arm
    wrist = constrain(wrist, wrist_max,wrist_min)
    offset = constrain(offset,(wrist_max - wrist),(wrist_min - wrist))
    arm_pwm = map_range(arm,arm_min,arm_max,702,2000)
    wrist_pwm = map_range(constrain(wrist+offset,wrist_max,wrist_min),wrist_min,wrist_max,2000,608)
    print(ps3.get_axis(arm_axis))
    print('y axis:',axis_y)
    print('arm:',arm)
    print('wrist:',constrain(wrist+offset,wrist_max,wrist_min))
    print('offset:',offset)
    print('arm pwm:',arm_pwm)
    print('wrist pwm:',wrist_pwm)
    print('manipulator:',mani_pwm)
    print('rotate:',rotate_pwm)
    time.sleep(0.05)

