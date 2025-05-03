import serial # type: ignore
import time
import pygame
import math
import Manipulator_Library as mani
import Aquamarine_GUI as gui
from config import *
from utils import *


if __name__ == '__main__':
        
    pygame.init()
    pygame.joystick.init()

    print(pygame.joystick.get_count())

    joy = pygame.joystick.Joystick(0)
    joy.init()

    print(f"{joy.get_name()} is connected")


    rs485 = serial.Serial('/dev/ttyAMA0', 57600, timeout=0)
    if (rs485.isOpen() == False):
        rs485.open()
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

        leftFront = int(constrain(map_range(-leftFront, -1.00, 1.00, 1200, 1800),1200,1775)*4) #front two motors reversed
        rightFront = int(constrain(map_range(-rightFront, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        leftBack = int(constrain(map_range(leftBack, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        rightBack = int(constrain(map_range(rightBack, -1.00, 1.00, 1200, 1800),1200,1775)*4)

        if joy.get_button(0) > 0:
            vertical = int(constrain(map_range(-slider, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        else:
            vertical = 6000
        
        currentButtonState = joy.get_button(1)
        if lastButtonState == 0 and currentButtonState == 1:
            isAutoLevel = 1 - isAutoLevel

        lastButtonState = currentButtonState
        
        #print(f"{leftFront}{rightFront}{leftBack}{rightBack}{vertical}")
        
        rs485.write(f"{leftFront}{rightFront}{leftBack}{rightBack}{vertical}{status['left']['rotate']}{status['left']['arm']}{status['left']['wrist']}{status['left']['manipulator']}{status['right']['rotate']}{status['right']['arm']}{status['right']['wrist']}{status['right']['manipulator']}{isAutoLevel}\n".encode())

        print(f"{leftFront},{rightFront},{leftBack},{rightBack},{vertical},{status['left']['rotate']},{status['left']['arm']},{status['left']['wrist']},{status['left']['manipulator']},{status['right']['rotate']},{status['right']['arm']},{status['right']['wrist']},{status['right']['manipulator']},{isAutoLevel}")
        
        """
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
                pitch = -receivedOutput[1]
                yaw = receivedOutput[2]
        except:
            print("invaild packet")
        """

        gui.main(roll, pitch, yaw, joy)
        
        #print(roll, pitch, yaw, joyX, joyY, twist, slider, leftFront/4, rightFront/4, leftBack/4, rightBack/4)

        #print("No respond")
        # print("Error occured")
        #print(f"Decoded Values: {response}")
        time.sleep(0.05)


