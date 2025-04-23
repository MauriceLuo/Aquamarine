import pygame
import time
import sys

# 初始化變數
axis_y = 0
axis_x = 0
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
mani_max = 90
mani_min = 0
mani_pwm = 0
rotate = 0
rotate_min = -90
rotate_max = 90
rotate_pwm = 1500

# 按鈕和軸的映射
rotate_axis = 0
arm_axis = 1
wrist_up_button = 2
wrist_down_button = 3

# 初始化 Pygame 和搖桿
pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())

ps3 = pygame.joystick.Joystick(0)
ps3.init()

print(ps3.get_numhats())
print(ps3.get_numbuttons())
print(ps3.get_numaxes())

def constrain(input_value, maximum, minimum):
    """限制輸入值在最大和最小值之間"""
    return max(minimum, min(maximum, input_value))

def map_range(x, in_min, in_max, out_min, out_max):
    """將一個範圍的值映射到另一個範圍"""
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def deadzone_normalise(input_value, minimum, maximum):
    """
    對輸入值應用死區。在 `minimum` 和 `maximum` 之間的值設為 0。
    低於 `minimum` 的值映射到 [-1.0, 0]。
    高於 `maximum` 的值映射到 [0, 1.0]。
    """
    if minimum < -1.0 or maximum > 1.0 or minimum >= maximum:
        raise ValueError("Invalid minimum or maximum range")
    
    if minimum <= input_value <= maximum:
        return 0.0
    elif input_value < minimum:
        return float(map_range(input_value, -1.0, minimum, -1.0, 0.0))
    else:  # input_value > maximum
        return float(map_range(input_value, maximum, 1.0, 0.0, 1.0))

def update_arm_and_wrist(axis_value):
    """根據搖桿輸入更新手臂和手腕的位置"""
    global arm, wrist, offset
    arm += axis_value * 10
    arm = constrain(arm, arm_max, arm_min)
    wrist = arm_max - arm
    wrist = constrain(wrist, wrist_max, wrist_min)
    offset = constrain(offset, (wrist_max - wrist), (wrist_min - wrist))
    return arm, wrist, offset

def update_manipulator(hat_value):
    """根據搖桿的 hat 輸入更新機械爪的位置"""
    global mani, mani_pwm
    mani += hat_value[0]
    mani = constrain(mani, mani_max, mani_min)
    mani_pwm = map_range(mani, mani_min, mani_max, 850, 1600)
    return mani, mani_pwm

def update_rotation(axis_value):
    """根據搖桿輸入更新旋轉角度"""
    global rotate, rotate_pwm
    rotate += axis_value * 10
    rotate = constrain(rotate, rotate_max, rotate_min)
    rotate_pwm = map_range(rotate, rotate_min, rotate_max, 1000, 2000)
    return rotate, rotate_pwm

def print_status():
    """打印當前狀態"""
    print('y axis:', axis_y)
    print('arm:', arm)
    print('wrist:', constrain(wrist + offset, wrist_max, wrist_min))
    print('offset:', offset)
    print('arm pwm:', arm_pwm)
    print('wrist pwm:', wrist_pwm)
    print('manipulator:', mani_pwm)
    print('rotate:', rotate_pwm)
 
def main_loop():
     """主迴圈"""
     global axis_y, axis_x, arm_pwm, wrist_pwm, offset
 
     while True:
         pygame.event.get()  # 處理事件
 
         # 更新 offset 和 manipulator
         offset += ps3.get_hat(0)[1]
         update_manipulator(ps3.get_hat(0))
 
         # 更新手臂和手腕
         axis_y = deadzone_normalise(round(ps3.get_axis(arm_axis), 2), deadzone_min, deadzone_max)
         update_arm_and_wrist(axis_y)
 
         # 更新旋轉
         axis_x = deadzone_normalise(round(ps3.get_axis(rotate_axis), 2), deadzone_min, deadzone_max)
         update_rotation(axis_x)
 
         # 計算 PWM 值
         arm_pwm = map_range(arm, arm_min, arm_max, 702, 2000)
         wrist_pwm = map_range(constrain(wrist + offset, wrist_max, wrist_min), wrist_min, wrist_max, 2000, 608)
 
         # 打印狀態
         print_status()
 
         # 等待 0.05 秒
         time.sleep(0.05)
 
if __name__ == "__main__":
    main_loop()