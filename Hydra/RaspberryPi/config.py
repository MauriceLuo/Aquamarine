left_config: dict = {
    'is_right': False,
    'deadzone': 0.15,

    # 手臂配置
    # init_pwm=config['arm_init_pwm'],
    # pwm_range=config['arm_pwm_range'],
    # invert=config['is_right'],
    # step=config.get('arm_step', 15.0),
    # deadzone=config.get('deadzone', 0.1)
    'arm_axis': 1,
    'arm_pwm_range': (807, 2000),
    'arm_init_pwm': 807,
    'arm_step': 20,

    # 旋转配置
    # init_pwm=config['rotate_init_pwm'],
    # pwm_range=config['rotate_pwm_range'],
    # invert=config['is_right'],
    # step=config.get('rotate_step', 15.0),
    # deadzone=config.get('deadzone', 0.1)
    'rotate_init_pwm': 1479,
    'rotate_pwm_range': (1000, 2000),
    'rotate_step': 20,
    'rotate_axis': 0,

    # 手腕配置
    # init_pwm=config['wrist_init_pwm'],
    # pwm_range=config['wrist_pwm_range'],
    # arm_controller=self.arm,
    # arm_pwm_range=config['arm_pwm_range'],
    # invert=config.get('is_right', False),
    # wrist_step = config['wrist_step'],
    # control_config=config['wrist_control']
    'wrist_init_pwm': 985,
    'wrist_pwm_range': (730, 1560),
    'wrist_step': 20,
    'wrist_control': {
        'type': 'hat',
        'hat_index': 0,
        'hat_axis': 1,
        'up': (0, 1),    # 上方向
        'down': (0, -1),  # 下方向
    },

    # 机械爪配置
    # control_config=config['mani_control'],
    # pwm_range=config['mani_pwm_range'],
    # init_pwm=config['mani_init_pwm'],
    # step=config.get('mani_step', 50),
    # invert=config.get('is_right', False)
    'mani_control': {
        'type': 'hat',
        'hat_index': 0,
        'hat_axis': 0,
        'open': (1, 0),   # Hat右方向为打开
        'close': (-1, 0)  # Hat左方向为关闭
    },
    'mani_pwm_range': (900, 1700),
    'mani_init_pwm': 900,
    'mani_step': 60
}

right_config: dict = {
    'is_right': True,
    'deadzone': 0.15,

    # 手臂配置
    # init_pwm=config['arm_init_pwm'],
    # pwm_range=config['arm_pwm_range'],
    # invert=config['is_right'],
    # step=config.get('arm_step', 15.0),
    # deadzone=config.get('deadzone', 0.1)
    'arm_init_pwm': 2376,
    'arm_pwm_range': (908, 2376),
    'arm_step': 20,
    'arm_axis': 4,

    # 旋转配置
    # init_pwm=config['rotate_init_pwm'],
    # pwm_range=config['rotate_pwm_range'],
    # invert=config['is_right'],
    # step=config.get('rotate_step', 15.0),
    # deadzone=config.get('deadzone', 0.1)
    'rotate_init_pwm': 1342,
    'rotate_pwm_range': (2000, 913),
    'rotate_step': 20,
    'rotate_axis': 3,

    # 手腕配置
    # init_pwm=config['wrist_init_pwm'],
    # pwm_range=config['wrist_pwm_range'],
    # arm_controller=self.arm,
    # arm_pwm_range=config['arm_pwm_range'],
    # invert=config.get('is_right', False),
    # wrist_step = config['wrist_step'],
    # control_config=config['wrist_control']
    'wrist_control': {
        'type': 'buttons',
        'up': 3,
        'down': 0,
    },
    'wrist_init_pwm': 1540,
    'wrist_pwm_range': (945, 1810),
    'wrist_step': 20,

    # 机械爪配置
    # control_config=config['mani_control'],
    # pwm_range=config['mani_pwm_range'],
    # init_pwm=config['mani_init_pwm'],
    # step=config.get('mani_step', 50),
    # invert=config.get('is_right', False)
    'mani_control': {
        'type': 'buttons',
        'open': 1,   # 按钮1为打开
        'close': 2   # 按钮2为关闭
    },
    'mani_pwm_range': (810, 1620),
    'mani_init_pwm': 1620,
    'mani_step': 60
}