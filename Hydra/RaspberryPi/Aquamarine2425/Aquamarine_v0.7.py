import serial
import time
import pygame
import sys
import math
import manipulator_library_v2 as mani
import Aquamarine2425_gui_v0_10 as gui

pygame.init()
pygame.joystick.init()

print(pygame.joystick.get_count())

joy = pygame.joystick.Joystick(0)
joy.init()

print(f"{joy.get_name()} is connected")



def map_value(value, old_min, old_max, new_min, new_max):
    # Calculate the mapped value
    mapped_value = new_min + ((value - old_min) / (old_max - old_min)) * (new_max - new_min)
    return mapped_value


def apply_deadzone(input_value, deadzonemax, deadzonemin):
    if -deadzonemin <= input_value <= deadzonemax:
        # Inside the deadzone
        return 0.000
    elif input_value > deadzonemax:
        # Above the deadzone, scale to 0~1
        return (input_value - deadzonemax) / (1.000 - deadzonemax)
    elif input_value < -deadzonemin:
        # Below the deadzone, scale to 0~-1
        return (input_value + deadzonemin) / (1.000 - deadzonemin)

def constrain(value, min_val,max_val):
    return max(min_val,min(max_val, value))

left_config = {
    'is_right': False,
    'deadzone': 0.15,
    
    # 手臂配置
    #init_pwm=config['arm_init_pwm'],
    #pwm_range=config['arm_pwm_range'],
    #invert=config['is_right'],
    #step=config.get('arm_step', 15.0),
    #deadzone=config.get('deadzone', 0.1)
    'arm_axis': 1,
    'arm_pwm_range': (807, 2000),
    'arm_init_pwm': 807,
    'arm_step': 20,

    # 旋转配置
    #init_pwm=config['rotate_init_pwm'],
    #pwm_range=config['rotate_pwm_range'],
    #invert=config['is_right'],
    #step=config.get('rotate_step', 15.0),
    #deadzone=config.get('deadzone', 0.1)
    'rotate_init_pwm': 1500,
    'rotate_pwm_range': (1000, 2000),
    'rotate_step': 20,
    'rotate_axis': 0,
    
    # 手腕配置
    #init_pwm=config['wrist_init_pwm'],
    #pwm_range=config['wrist_pwm_range'],
    #arm_controller=self.arm,
    #arm_pwm_range=config['arm_pwm_range'],
    #invert=config.get('is_right', False),
    #wrist_step = config['wrist_step'],
    #control_config=config['wrist_control']
    'wrist_init_pwm': 985,
    'wrist_pwm_range': (730, 1560),
    'wrist_step': 20,
    'wrist_control': {
        'type': 'hat',
        'hat_index': 0,
        'hat_axis': 1,
        'up': (0, 1),    # 上方向
        'down': (0, -1), # 下方向
    },

    # 机械爪配置
    #control_config=config['mani_control'],
    #pwm_range=config['mani_pwm_range'],
    #init_pwm=config['mani_init_pwm'],
    #step=config.get('mani_step', 50),
    #invert=config.get('is_right', False)
    'mani_control': {
        'type': 'hat',
        'hat_index': 0,
        'hat_axis': 0,
        'open': (1, 0),   # Hat右方向为打开
        'close': (-1, 0)  # Hat左方向为关闭
    },
    'mani_pwm_range': (900, 1650),
    'mani_init_pwm': 900,
    'mani_step': 60
}

right_config = {
    'is_right': True,
    'deadzone': 0.15,

    # 手臂配置
    #init_pwm=config['arm_init_pwm'],
    #pwm_range=config['arm_pwm_range'],
    #invert=config['is_right'],
    #step=config.get('arm_step', 15.0),
    #deadzone=config.get('deadzone', 0.1)
    'arm_init_pwm': 2376,
    'arm_pwm_range': (908, 2376),
    'arm_step': 20,
    'arm_axis': 4,
    
    # 旋转配置
    #init_pwm=config['rotate_init_pwm'],
    #pwm_range=config['rotate_pwm_range'],
    #invert=config['is_right'],
    #step=config.get('rotate_step', 15.0),
    #deadzone=config.get('deadzone', 0.1)
    'rotate_init_pwm': 1413,
    'rotate_pwm_range': (2000, 913),
    'rotate_step':20,
    'rotate_axis': 3,
    
    # 手腕配置
    #init_pwm=config['wrist_init_pwm'],
    #pwm_range=config['wrist_pwm_range'],
    #arm_controller=self.arm,
    #arm_pwm_range=config['arm_pwm_range'],
    #invert=config.get('is_right', False),
    #wrist_step = config['wrist_step'],
    #control_config=config['wrist_control']
    'wrist_control': {
        'type': 'buttons',
        'up': 3,
        'down': 0,
    },
    'wrist_init_pwm': 1590,
    'wrist_pwm_range': (1010, 1930),
    'wrist_step': 20,

    # 机械爪配置
    #control_config=config['mani_control'],
    #pwm_range=config['mani_pwm_range'],
    #init_pwm=config['mani_init_pwm'],
    #step=config.get('mani_step', 50),
    #invert=config.get('is_right', False)
    'mani_control': {
        'type': 'buttons',
        'open': 1,   # 按钮1为打开
        'close': 2   # 按钮2为关闭
    },
    'mani_pwm_range': (810, 1620),
    'mani_init_pwm': 1620,
    'mani_step': 60
}


if __name__ == '__main__':
    rs485 = serial.Serial('/dev/ttyAMA0', 57600, timeout=0)
    if (rs485.isOpen() == False):
        rs485. open()
        rs485.flushInput()
        rs485.flushOutput()
    rs485.flush()

    # the Arduino is designed to reset everytime a serial connection is made over the USB interface, we must give it time to reboot.
    time.sleep(2)

    roll = 0
    pitch = 0
    yaw = 0

    controller = mani.DualArmSystem(left_config, right_config, 1, [9,10])   #Manipulator initialize
    print("Manipulator initialized")
    
    lastButtonState = 0
    isAutoLevel = 0

    while True:
        pygame.event.get()  # gets values from the joystick
        # ser.write("R+\n".encode())  # sends in binary

        controller.update()                 #Update Manipulator PWM
        status = controller.get_status()    #Get Manipulator PWM

        joyX = round(joy.get_axis(0), 3)
        joyY = -round(joy.get_axis(1), 3)
        twist = apply_deadzone(round(joy.get_axis(2), 3), 0.35, 0.35)
        slider = apply_deadzone(round(joy.get_axis(3), 3), 0.25, 0.25)

        theta = math.atan2(apply_deadzone(joyY, 0.25,0.25),
                           apply_deadzone(joyX, 0.25,0.25))
        power = math.hypot(apply_deadzone(joyX, 0.25,0.25),
                           apply_deadzone(joyY, 0.25,0.25))

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
        
        leftFrontGUI = leftFront
        rightFrontGUI = rightFront
        leftBackGUI = leftBack
        rightBackGUI = rightBack

        leftFront = int(constrain(map_value(-leftFront, -1.00, 1.00, 1200, 1800),1200,1775)*4) #front two motors reversed
        rightFront = int(constrain(map_value(-rightFront, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        leftBack = int(constrain(map_value(leftBack, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        rightBack = int(constrain(map_value(rightBack, -1.00, 1.00, 1200, 1800),1200,1775)*4)

        if joy.get_button(0) > 0:
            vertical = int(constrain(map_value(-slider, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        else:
            vertical = 6000
        
        currentButtonState = joy.get_button(1)
        if lastButtonState == 0 and currentButtonState == 1:
            isAutoLevel = 1 - isAutoLevel

        lastButtonState = currentButtonState
        
        #print(f"{leftFront}{rightFront}{leftBack}{rightBack}{vertical}")
        
        rs485.write(f"{leftFront}{rightFront}{leftBack}{rightBack}{vertical}{status['left']['rotate']}{status['left']['arm']}{status['left']['wrist']}{status['left']['manipulator']}{status['right']['rotate']}{status['right']['arm']}{status['right']['wrist']}{status['right']['manipulator']}{isAutoLevel}\n".encode())

        print(f"{leftFront},{rightFront},{leftBack},{rightBack},{vertical},{status['left']['rotate']},{status['left']['arm']},{status['left']['wrist']},{status['left']['manipulator']},{status['right']['rotate']},{status['right']['arm']},{status['right']['wrist']},{status['right']['manipulator']},{isAutoLevel}")
        
        #while rs485.in_waiting <= 0:
        #    time.sleep(0.01)
        response = ""
        try:
            response = rs485.readline().decode("utf-8")
            if response == "":
                print("No response")
                print()
            else:
                print(f"Decoded Values: {response}")
                receivedOutput = [float(value) for value in response.split(',')]
                roll = receivedOutput[0]
                pitch = receivedOutput[1]
                yaw = receivedOutput[2]
        except:
            print("invaild packet")


        gui.main(roll, pitch, yaw, joyX, joyY, twist, slider, leftFrontGUI, rightFrontGUI, leftBackGUI, rightBackGUI)
        
        #print(roll, pitch, yaw, joyX, joyY, twist, slider, leftFront/4, rightFront/4, leftBack/4, rightBack/4)

        #print("No respond")
        # print("Error occured")
        #print(f"Decoded Values: {response}")
        
        time.sleep(0.05)


