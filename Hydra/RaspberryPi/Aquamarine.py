import serial
import time
import pygame
import Manipulator_Library as mani
import GUI
import joystick
from config import *
from utils import *


if __name__ == '__main__':

    pygame.init()
    pygame.joystick.init()

    print(pygame.joystick.get_count())

    joy = joystick.Joystick(0, 1)
    controller = mani.DualArmSystem(    # Manipulator initialize
        left_config,
        right_config,
        1,
        [9, 10]
    )

    print("Joysticks initialized")

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

    lastButtonState = 0
    isAutoLevel = 0

    dt = 0.05
    last_time = time.time()
    while True:
        if (time.time() - last_time >= dt):
            last_time = time.time()
            pygame.event.get()  # gets values from the joystick
            # ser.write("R+\n".encode())  # sends in binary

            controller.update()  # Update Manipulator PWM
            mani_status = controller.get_status()  # Get Manipulator PWM

            joy.update()
            thruster_status = joy.get_status()

            currentButtonState = thruster_status["pidButton"]
            if lastButtonState == 0 and currentButtonState == 1:
                isAutoLevel = 1 - isAutoLevel

            lastButtonState = currentButtonState

            rs485.write(
                f"{thruster_status['leftFront']}"
                f"{thruster_status['rightFront']}"
                f"{thruster_status['leftBack']}"
                f"{thruster_status['rightBack']}"
                f"{thruster_status['vertical']}"
                f"{mani_status['left']['rotate']}"
                f"{mani_status['left']['arm']}"
                f"{mani_status['left']['wrist']}"
                f"{mani_status['left']['manipulator']}"
                f"{mani_status['right']['rotate']}"
                f"{mani_status['right']['arm']}"
                f"{mani_status['right']['wrist']}"
                f"{mani_status['right']['manipulator']}"
                f"{isAutoLevel}\n".encode()
            )

            print(
                f"{thruster_status['leftFront']},"
                f"{thruster_status['rightFront']},"
                f"{thruster_status['leftBack']},"
                f"{thruster_status['rightBack']},"
                f"{thruster_status['vertical']},"
                f"{mani_status['left']['rotate']},"
                f"{mani_status['left']['arm']},"
                f"{mani_status['left']['wrist']},"
                f"{mani_status['left']['manipulator']},"
                f"{mani_status['right']['rotate']},"
                f"{mani_status['right']['arm']},"
                f"{mani_status['right']['wrist']},"
                f"{mani_status['right']['manipulator']},"
                f"{isAutoLevel}"
            )

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

            GUI.main(roll, pitch, yaw, 0)

            # print("No respond")
            # print("Error occured")
            # print(f"Decoded Values: {response}")
            # time.sleep(0.05)
        else:
            time.sleep(0.005)
