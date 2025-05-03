import pygame
import math
from config import *
from utils import *
class Joystick:
    def __init__(self, joystick_num, pidbutton_num):
        self.joystick_num = joystick_num
        self.pidbutton_num = pidbutton_num
        
        self.joystick = pygame.joystick.Joystick(self.joystick_num)
        self.joystick.init
        
        
    def update(self):
        
        self.joyX = round(self.joystick.get_axis(0), 3)
        self.joyY = -round(self.joystick.get_axis(1), 3)
        self.twist = apply_deadzone(round(self.joystick.get_axis(2), 3), 0.35, 0.35)
        self.slider = apply_deadzone(round(self.joystick.get_axis(3), 3), 0.25, 0.25)

        self.theta = math.atan2(apply_deadzone(self.joyY, 0.25,0.25),
                        apply_deadzone(self.joyX, 0.25,0.25))
        self.power = math.hypot(apply_deadzone(self.joyX, 0.25,0.25),
                        apply_deadzone(self.joyY, 0.25,0.25))

        self.sin = math.sin(self.theta - math.pi/4)
        self.cos = math.cos(self.theta - math.pi/4)
        self.maximum = max(abs(self.sin), abs(self.cos))

        assert(self.maximum != 0)
        self.leftFront = self.power * (self.cos/self.maximum) + self.twist
        self.rightFront = self.power * (self.sin/self.maximum) - self.twist
        self.leftBack = self.power * (self.sin/self.maximum) + self.twist
        self.rightBack = self.power * (self.cos/self.maximum) - self.twist

        if self.power + abs(self.twist) > 1:
            assert((self.power + abs(self.twist)) != 0)
            self.leftFront /= self.power + abs(self.twist)
            self.rightFront /= self.power + abs(self.twist)
            self.leftBack /= self.power + abs(self.twist)
            self.rightBack /= self.power + abs(self.twist)

        self.leftFront = int(constrain(map_range(-self.leftFront, -1.00, 1.00, 1200, 1800),1200,1775)*4) #front two motors reversed
        self.rightFront = int(constrain(map_range(-self.rightFront, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        self.leftBack = int(constrain(map_range(self.leftBack, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        self.rightBack = int(constrain(map_range(self.rightBack, -1.00, 1.00, 1200, 1800),1200,1775)*4)

        if self.joystick.get_button(0) > 0:
            self.vertical = int(constrain(map_range(-self.slider, -1.00, 1.00, 1200, 1800),1200,1775)*4)
        else:
            self.vertical = 6000
        
        self.pidButton = self.joystick.get_button(self.pidbutton_num)
        
    def get_status(self):
        ThrusterPWM = {
            'leftFront': self.leftFront,
            'rightFront': self.rightFront,
            'leftBack': self.leftBack,
            'rightBack': self.rightBack,
            'vertical': self.vertical,
            'pidButton': self.pidButton
        }
        return ThrusterPWM