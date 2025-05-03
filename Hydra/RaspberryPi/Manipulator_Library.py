import pygame
import time
import numpy as np
import subprocess
from config import *
from utils import *
    
class RotateControl:
    def __init__(self, init_pwm, pwm_range, invert, step, deadzone):
        self.pwm_max = max(pwm_range)
        self.pwm_min = min(pwm_range)
        self.init_pwm = init_pwm
        self.invert = invert
        self.step = step
        self.deadzone = deadzone
        self.__current_pwm = init_pwm
        
    def update(self, axis_value):
        self.axis_value = deadzone_normalise(axis_value, -self.deadzone, self.deadzone)
        
        """
        if not self.invert:
            delta_pwm = self.axis_value * self.step
        elif self.invert:
        """
        delta_pwm = self.axis_value * self.step * -1
            
        self.__current_pwm = np.clip(
            self.__current_pwm + delta_pwm,
            self.pwm_min,
            self.pwm_max
        )
    
    def reset(self):
        self.__current_pwm = self.init_pwm
        return int(self.__current_pwm)

    def pwm(self):
        return int(self.__current_pwm)


class ArmControl:
    def __init__(self, init_pwm, pwm_range, invert, step, deadzone):
        self.pwm_max = max(pwm_range)
        self.pwm_min = min(pwm_range)
        self.invert = invert
        self.step = step
        self.deadzone = deadzone
        self.init_pwm = init_pwm
        self.__current_pwm = init_pwm
    
    def update(self, axis_value):
        self.axis_value = deadzone_normalise(axis_value, -self.deadzone, self.deadzone)
        
        if not self.invert:
            delta_pwm = self.axis_value * self.step
        elif self.invert:
            delta_pwm = self.axis_value * self.step * -1
        
        self.__current_pwm = np.clip(
            self.__current_pwm + delta_pwm,
            self.pwm_min,
            self.pwm_max
        )
    
    def reset(self):
        self.__current_pwm = self.init_pwm
        return int(self.__current_pwm)
    
    def pwm(self):
        return int(self.__current_pwm)


class WristControl:
    def __init__(self, init_pwm, pwm_range, arm_controller, arm_pwm_range, arm_current_pwm, invert, step, control_config):
        self.init_pwm = init_pwm
        self.__current_pwm = init_pwm
        self.pwm_max = max(pwm_range)
        self.pwm_min = min(pwm_range)
        self.arm_pwm_max = max(arm_pwm_range)
        self.arm_pwm_min = min(arm_pwm_range)
        self.arm_controller = arm_controller
        self.arm_current_pwm = arm_current_pwm
        self.invert = invert
        self.step = step
        self.offset = 0
        self.control_config = control_config
        
    def update(self, joystick):
        if self.control_config['type'] == 'buttons':
            up, down = 0, 0
            up = joystick.get_button(self.control_config['up'])
            down = joystick.get_button(self.control_config['down'])
            delta = up - down
        elif self.control_config['type'] == 'hat':
            hat = joystick.get_hat(self.control_config['hat_index'])
            delta = hat[self.control_config['hat_axis']]
        
        if not self.invert:
            delta_arm = self.arm_controller.pwm() - self.arm_pwm_min
            self.offset = np.clip(
                self.offset + delta * self.step,
                -(self.pwm_max - self.init_pwm - delta_arm),
                -(self.pwm_min - self.init_pwm - delta_arm)
            )
            self.__current_pwm = delta_arm  + self.init_pwm - self.offset
        elif self.invert :
            delta_arm = self.arm_pwm_max - self.arm_controller.pwm()
            self.offset = np.clip(
                self.offset + delta * self.step,
                self.pwm_min - self.init_pwm + delta_arm,
                self.pwm_max - self.init_pwm + delta_arm
            )
            self.__current_pwm = self.init_pwm - delta_arm + self.offset

        self.__current_pwm = np.clip(
            self.__current_pwm,
            self.pwm_min,
            self.pwm_max
        )
        
    def reset(self):
        self.offset = 0
        self.__current_pwm = self.init_pwm
        return int(self.__current_pwm)
    
    def pwm(self):
        return int(self.__current_pwm)

class ManipulatorControl:
    def __init__(self, control_config, pwm_range, init_pwm, step, invert):
        self.control_config = control_config
        self.pwm_max = max(pwm_range)
        self.pwm_min = min(pwm_range)
        self.init_pwm = init_pwm
        self.step = step
        self.__current_pwm = init_pwm
        self.invert =invert
        
    def update(self, joystick):
        if self.control_config['type'] == 'buttons':
            delta = joystick.get_button(self.control_config['open']) - joystick.get_button(self.control_config['close'])
        elif self.control_config['type'] == 'hat':
            hat = joystick.get_hat(self.control_config['hat_index'])
            delta = hat[self.control_config['hat_axis']]
        
        if not self.invert:
            self.__current_pwm = np.clip(
                self.__current_pwm + delta * self.step,
                self.pwm_min,
                self.pwm_max
            )
        elif self.invert:
            self.__current_pwm = np.clip(
                self.__current_pwm + delta * self.step,
                self.pwm_min,
                self.pwm_max
            )
    
    def reset(self):
        self.__current_pwm = self.init_pwm
        return int(self.__current_pwm)
    
    def pwm(self):
        return int(self.__current_pwm)
    
    
class RoboticArm:
    def __init__(self, config):
        # 手臂
        self.arm = ArmControl(
            init_pwm=config['arm_init_pwm'],
            pwm_range=config['arm_pwm_range'],
            invert=config['is_right'],
            step=config.get('arm_step', 15.0),
            deadzone=config.get('deadzone', 0.1)
        )
        
        # 旋转
        self.rotate = RotateControl(
            init_pwm=config['rotate_init_pwm'],
            pwm_range=config['rotate_pwm_range'],
            invert=config['is_right'],
            step=config.get('rotate_step', 15.0),
            deadzone=config.get('deadzone', 0.1)
        )
        
        # 手腕
        self.wrist = WristControl(
            init_pwm=config['wrist_init_pwm'],
            pwm_range=config['wrist_pwm_range'],
            arm_controller=self.arm,
            arm_pwm_range=config['arm_pwm_range'],
            arm_current_pwm=self.arm.pwm,
            invert=config.get('is_right', False),
            step = config['wrist_step'],
            control_config=config['wrist_control']
        )
        
        # Mani
        self.manipulator = ManipulatorControl(
            control_config=config['mani_control'],
            pwm_range=config['mani_pwm_range'],
            init_pwm=config['mani_init_pwm'],
            step=config.get('mani_step', 50),
            invert=config.get('is_right', False)
        )

        # axis
        self.axis_mapping = {
            'arm': config['arm_axis'],
            'rotate': config['rotate_axis']
        }
    
    def update(self, joystick):
         # 更新手臂
        self.arm.update(joystick.get_axis(self.axis_mapping['arm']))
        
        # 更新旋转
        self.rotate.update(joystick.get_axis(self.axis_mapping['rotate']))
        
        # 更新手腕
        self.wrist.update(joystick)
        
        # 更新mani
        self.manipulator.update(joystick)

    def get_pwm(self):
        return {
            'arm': self.arm.pwm() *4,
            'rotate': self.rotate.pwm() *4,
            'wrist': self.wrist.pwm() *4,
            'manipulator': self.manipulator.pwm() *4
        }
    
    def reset(self):
        return {
            'arm': self.arm.reset() *4,
            'rotate': self.rotate.reset() *4,
            'wrist': self.wrist.reset() *4,
            'manipulator': self.manipulator.reset() *4
        }


class DualArmSystem:
    def __init__(self, left_config, right_config, joystick_num, reset_button):
        
        #For testing, no need as a library
        # pygame.init()
        # pygame.joystick.init()
        
        # if pygame.joystick.get_count() < 1:
        #     raise RuntimeError("未检测到游戏手柄")

        self.joystick_num = joystick_num
        self.joystick = pygame.joystick.Joystick(self.joystick_num)
        self.joystick.init()
        self.reset_button = reset_button
        
        self.left_arm = RoboticArm(left_config)
        self.right_arm = RoboticArm(right_config)

    def update(self):
        # 处理游戏手柄事件
        #pygame.event.pump()
        
        # 更新左臂状态
        self.left_arm.update(self.joystick)
        
        # 更新右臂状态
        self.right_arm.update(self.joystick)



    def get_status(self):
        if self.joystick.get_button(self.reset_button[0]) and self.joystick.get_button(self.reset_button[1]):
            return{
            'left': self.left_arm.reset(),
            'right': self.right_arm.reset()
        }
        return {
            'left': self.left_arm.get_pwm(),
            'right': self.right_arm.get_pwm()
        }
        

def clear() -> None:
    command = ['cmd']
    args = ['/c','cls']
    cli = command + args
    subprocess.run(cli)
    return None


if __name__ == "__main__":
    controller = DualArmSystem(left_config, right_config, 0)
    
    try:
        
        while True:
            # clear()
            controller.update()
            status = controller.get_status()
            # 使用固定位置输出
            output = f"""
左臂状态: 
  手臂：{status['left']['arm']}μs (初始：784μs)
  旋转：{status['left']['rotate']}μs (初始：1500μs)
  手腕：{status['left']['wrist']}μs (初始：985±0μs)
  夹爪：{status['left']['manipulator']}μs (初始：900μs)

右臂状态：
  手臂：{status['right']['arm']}μs (初始：908μs)
  旋转：{status['right']['rotate']}μs (初始：1500μs)
  手腕：{status['right']['wrist']}μs (初始：1590±0μs)
  夹爪：{status['right']['manipulator']}μs (初始：1620μs)
"""
            print("\033[2J\033[H" + output)

            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pygame.quit()
