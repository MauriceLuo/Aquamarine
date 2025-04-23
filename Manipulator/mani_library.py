import pygame
import time
import numpy as np
import subprocess

class JointController:
    def __init__(self, pwm_range, init_pwm, invert=False, speed=10.0, deadzone=0.1):
        self.pwm_min, self.pwm_max = sorted(pwm_range)
        self.invert = invert
        self.speed = speed  # PWM变化速度（μs/单位输入）
        self.deadzone = deadzone
        self.current_pwm = np.clip(init_pwm, self.pwm_min, self.pwm_max)

    def update(self, axis_value):
        # 应用死区
        if abs(axis_value) < self.deadzone:
            axis_value = 0.0
        
        # 计算PWM变化
        delta_pwm = axis_value * self.speed
        if self.invert:
            delta_pwm *= -1
        
        # 更新并限制范围
        self.current_pwm = np.clip(
            self.current_pwm + delta_pwm,
            self.pwm_min,
            self.pwm_max
        )

    @property
    def pwm(self):
        return int(self.current_pwm)

class WristController:
    def __init__(self, control_config, base_pwm, offset_range, pwm_range, 
                 arm_controller=None, comp_ratio=0.0, invert=False):
        self.control_config = control_config
        self.base_pwm = base_pwm
        self.offset_range = offset_range
        self.pwm_range = pwm_range
        self.arm_controller = arm_controller
        self.comp_ratio = comp_ratio
        self.invert = invert
        
        # 控制参数
        self.step_size = control_config.get('step_size', 10)
        self.offset = 0
        self._base_pwm_initial = base_pwm

    def update(self, joystick):
        # 手柄控制部分
        delta = 0
        if self.control_config['type'] == 'buttons':
            up = joystick.get_button(self.control_config['up'])
            down = joystick.get_button(self.control_config['down'])
            delta = up - down
        elif self.control_config['type'] == 'hat':
            hat = joystick.get_hat(self.control_config['hat_index'])
            if hat == self.control_config['up']:
                delta += 1
            elif hat == self.control_config['down']:
                delta -= 1

        # 更新偏移量
        self.offset = np.clip(
            self.offset + delta * self.step_size,
            self.offset_range[0],
            self.offset_range[1]
        )

        # 自动补偿（可选）
        if self.arm_controller:
            arm_delta = self.arm_controller.pwm - self._base_pwm_initial
            comp = arm_delta * self.comp_ratio * (-1 if self.invert else 1)
            self.base_pwm = self._base_pwm_initial + comp

    @property
    def pwm(self):
        final = self.base_pwm + (self.offset if not self.invert else -self.offset)
        return int(np.clip(final, *self.pwm_range))

class ManipulatorController:
    def __init__(self, control_config, pwm_range, init_pwm, step_size=50):
        self.pwm_min, self.pwm_max = sorted(pwm_range)
        self.control_config = control_config
        self.step_size = step_size
        self.current_pwm = np.clip(init_pwm, self.pwm_min, self.pwm_max)

    def update(self, joystick):
        delta = 0
        if self.control_config['type'] == 'buttons':
            delta = joystick.get_button(self.control_config['open']) 
            - joystick.get_button(self.control_config['close'])
        elif self.control_config['type'] == 'hat':
            hat = joystick.get_hat(self.control_config['hat_index'])
            delta = hat[0]  # 假设使用左右方向
        
        self.current_pwm = np.clip(
            self.current_pwm + delta * self.step_size,
            self.pwm_min,
            self.pwm_max
        )

    @property
    def pwm(self):
        return int(self.current_pwm)

class RoboticArm:
    def __init__(self, config):
        # 手臂关节
        self.arm = JointController(
            pwm_range=config['arm_pwm_range'],
            init_pwm=config['arm_init_pwm'],
            invert=config['is_right'],
            speed=config.get('arm_speed', 15.0),
            deadzone=config.get('deadzone', 0.1)
        )
        
        # 旋转关节
        self.rotate = JointController(
            pwm_range=config['rotate_pwm_range'],
            init_pwm=config['rotate_init_pwm'],
            invert=config['is_right'],
            speed=config.get('rotate_speed', 10.0),
            deadzone=config.get('deadzone', 0.1)
        )
        
        # 手腕
        self.wrist = WristController(
            control_config=config['wrist_control'],
            base_pwm=config['wrist_init_pwm'],
            offset_range=config['wrist_offset_range'],
            pwm_range=config['wrist_pwm_range'],
            arm_controller=self.arm,
            comp_ratio=config.get('comp_ratio', 0.0),
            invert=config.get('wrist_invert', False)
        )
        
        # 机械爪
        self.manipulator = ManipulatorController(
            control_config=config['mani_control'],
            pwm_range=config['mani_pwm_range'],
            init_pwm=config['mani_init_pwm'],
            step_size=config.get('mani_step_size', 50)
        )

        # 控制映射
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
        
        # 更新夹爪
        self.manipulator.update(joystick)

    def get_pwm(self):
        return {
            'arm': self.arm.pwm,
            'rotate': self.rotate.pwm,
            'wrist': self.wrist.pwm,
            'manipulator': self.manipulator.pwm
        }

class DualArmSystem:
    def __init__(self, left_config, right_config):
        pygame.init()
        pygame.joystick.init()
        
        if pygame.joystick.get_count() < 1:
            raise RuntimeError("未检测到游戏手柄")
            
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        
        self.left_arm = RoboticArm(left_config)
        self.right_arm = RoboticArm(right_config)
        self.last_update = time.time()

    def update(self):
        # 计算时间差
        current_time = time.time()
        delta_time = current_time - self.last_update
        self.last_update = current_time
        
        # 处理游戏手柄事件
        pygame.event.pump()
        
        # 更新左臂状态
        self.left_arm.update(self.joystick)
        
        # 更新右臂状态
        self.right_arm.update(self.joystick)

    def get_status(self):
        return {
            'left': self.left_arm.get_pwm(),
            'right': self.right_arm.get_pwm()
        }

# 配置示例（保持与之前相同的配置结构）
# ... [配置部分与用户提供的原始代码相同] ...
# 完整配置示例
left_config = {
    'is_right': False,
    'deadzone': 0.15,

    # 手臂配置
    'arm_axis': 1,
    'arm_pwm_range': (784, 2000),
    'arm_init_pwm': 784,

    # 旋转配置
    'rotate_axis': 0,
    'rotate_pwm_range': (1000, 2000),
    'rotate_init_pwm': 1500,

    # 手腕配置
    'wrist_init_pwm': 985,
    'wrist_offset_range': (-300, 300),      # 偏移量范围
    'wrist_pwm_range': (730, 1560),         # 新增：整体PWM限制
    'comp_ratio': 1.0,                      # 补偿比例（100%的arm变化量）
    'wrist_comp_invert': True,              # 根据机械结构决定是否需要反转补偿方向
    'wrist_init_offset': 0,
    'wrist_control': {
        'type': 'hat',
        'hat_index': 0,
        'up': (0, 1),    # 上方向
        'down': (0, -1), # 下方向
        'step_size': 15  # 每次调整步长
    },

    # 机械爪配置
    'mani_control': {
        'type': 'hat',
        'hat_index': 0,
        'open': (1, 0),   # Hat右方向为打开
        'close': (-1, 0)  # Hat左方向为关闭
    },
    'mani_pwm_range': (900, 1650),
    'mani_init_pwm': 900,
    'mani_step_size': 60
}

right_config = {
    'is_right': True,
    'deadzone': 0.15,

    # 手臂配置
    'arm_axis': 3,
    'arm_pwm_range': (908, 2380),
    'arm_init_pwm': 908,

    # 旋转配置
    'rotate_axis': 2,
    'rotate_pwm_range': (2000, 1000),
    'rotate_init_pwm': 1500,

    # 手腕配置
    'wrist_control': {
        'type': 'buttons',
        'up': 3,
        'down': 0,
        'step_size': 20
    },
    'wrist_init_pwm': 1590,
    'wrist_offset_range': (-300, 300),
    'wrist_pwm_range': (1010, 1930),        # 限制手腕活动范围
    'comp_ratio': 1.0,                      # 补偿比例（100%的arm变化量）
    'wrist_comp_invert': True,              # 根据机械结构决定是否需要反转补偿方向

    # 机械爪配置
    'mani_control': {
        'type': 'buttons',
        'open': 1,   # 按钮1为打开
        'close': 2   # 按钮2为关闭
    },
    'mani_pwm_range': (810, 1620),
    'mani_init_pwm': 1620,
    'mani_step_size': 40
}


def clear() -> None:
    command = ['cmd']
    args = ['/c','cls']
    cli = command + args
    subprocess.run(cli)
    return None

if __name__ == "__main__":
    controller = DualArmSystem(left_config, right_config)
    
    try:
        while True:
            clear()
            controller.update()
            status = controller.get_status()
            
            # 显示状态信息
            print("\n左臂状态: ")
            print(f"  手臂：{status['left']['arm']}μs (初始：{left_config['arm_init_pwm']}μs)")
            print(f"  旋转：{status['left']['rotate']}μs (初始：{left_config['rotate_init_pwm']}μs)")
            print(f"  手腕：{status['left']['wrist']}μs (初始：{left_config['wrist_init_pwm']}±0μs)")
            print(f"  夹爪：{status['left']['manipulator']}μs (初始：{left_config['mani_init_pwm']}μs)")
            
            print("右臂状态：")
            print(f"  手臂：{status['right']['arm']}μs (初始：{right_config['arm_init_pwm']}μs)")
            print(f"  旋转：{status['right']['rotate']}μs (初始：{right_config['rotate_init_pwm']}μs)")
            print(f"  手腕：{status['right']['wrist']}μs (初始：{right_config['wrist_init_pwm']}±0μs)")
            print(f"  夹爪：{status['right']['manipulator']}μs (初始：{right_config['mani_init_pwm']}μs)")
            
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        pygame.quit()