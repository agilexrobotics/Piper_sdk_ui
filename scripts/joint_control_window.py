#!/usr/bin/env python3
# -*- coding:utf8 -*-
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSlider, QLabel, QPushButton, QGridLayout
from PyQt5.QtCore import Qt
import time
import random
from functools import partial

class JointControlWindow(QWidget):
    def __init__(self, piper):
        super().__init__()

        self.piper = piper
        self.setWindowTitle("Joint Control")
        self.setGeometry(350, 300, 200, 400)

        # 创建主垂直布局
        self.layout = QGridLayout()

        # 关节角度范围（单位：弧度）
        self.joint_ranges = [
            (-2.618, 2.618),  # Joint 1
            (0, 3.14),  # Joint 2
            (-2.697, 0),  # Joint 3
            (-1.832, 1.832),  # Joint 4
            (-1.22, 1.22),  # Joint 5
            (-2.0944, 2.0944),  # Joint 6
        ]
        self.joint_ranges_random = [
            (-0.3, 0.3),  # Joint 1
            (0, 0.5),  # Joint 2
            (-0.5, 0),  # Joint 3
            (-0.5, 0.5),  # Joint 4
            (-0.5, 0.5),  # Joint 5
            (-0.5, 0.5),  # Joint 6
        ]
        self.sliders = []
        self.labels = []
        self.value_labels = []

        # 使用网格布局
        self.grid_layout = QGridLayout()

        for i, (min_angle, max_angle) in enumerate(self.joint_ranges):
            # 创建实时值标签
            value_label = QLabel(f"Joint {i+1}: 0.000 rad", self)
            self.value_labels.append(value_label)

            # 创建最小值标签
            min_label = QLabel(f"{min_angle:.3f}", self)

            # 创建滑块
            slider = QSlider(Qt.Horizontal, self)
            slider.setRange(int(min_angle * 1000), int(max_angle * 1000))  # 转换为整数
            slider.setValue(0)  # 初始值设为 0
            slider.setSingleStep(10)  # 每次调整 0.01rad
            slider.valueChanged.connect(self.update_joint_value)  # 绑定值变化
            self.sliders.append(slider)

            # 创建最大值标签
            max_label = QLabel(f"{max_angle:.3f}", self)

            # 创建零点设置按钮
            # set_zero_button = QPushButton("Set Zero", self)
            # joint_num = int(i+1)
            # set_zero_button.clicked.connect(partial(self.set_zero, joint_num))

            # 将控件添加到网格布局
            self.grid_layout.addWidget(value_label, i * 3, 0, 1, 3)  # 实时值标签放置在上方
            self.grid_layout.addWidget(min_label, i * 3 + 1, 0)  # 最小值标签
            self.grid_layout.addWidget(slider, i * 3 + 1, 1)  # 滑块
            self.grid_layout.addWidget(max_label, i * 3 + 1, 2)  # 最大值标签
            # self.grid_layout.addWidget(set_zero_button, i * 3 + 1, 2)

        # 创建按钮布局
        button_layout = QGridLayout()

        # 回零按钮
        self.center_button = QPushButton("Center", self)
        self.center_button.clicked.connect(self.center_arm)
        button_layout.addWidget(self.center_button, 0, 0)

        # 随机按钮
        self.random_button = QPushButton("Random", self)
        self.random_button.clicked.connect(self.randomize_arm)
        button_layout.addWidget(self.random_button, 1, 0)

        # 全部设置零点
        # self.all_set_zero_button = QPushButton("All Set Zero", self)
        # self.all_set_zero_button.clicked.connect(partial(self.set_zero, 7))
        # button_layout.addWidget(self.all_set_zero_button, 2, 0)

        # 将按钮布局添加到主布局的底部
        self.layout.addLayout(self.grid_layout, 0, 0)
        self.layout.addLayout(button_layout, 1, 0)  # 放在底部

        self.setLayout(self.layout)

    # 设置零点
    def set_zero(self, joint_num):
        self.piper.JointConfig(joint_num, 0, 0xAE, 500, 0)
        self.piper.DisableArm(joint_num, 0x01)
        time.sleep(0.5)
        self.piper.JointConfig(joint_num, 0xAE, 0xAE, 500, 0)

    def update_joint_value(self):
        joint_angles = [slider.value() / 1000.0 for slider in self.sliders]

        # 更新每个滑块上方的显示值
        for i, angle in enumerate(joint_angles):
            self.value_labels[i].setText(f"Joint {i+1}: {angle:.3f} rad")

        self.control_arm()

    def control_arm(self):
        joint_angles = [slider.value() / 1000.0 for slider in self.sliders]

        factor = 57324.840764  # 1000*180/3.14
        joint_values = [round(angle * factor) for angle in joint_angles]

        self.piper.MotionCtrl_2(0x01, 0x01, 50, 0x00)
        self.piper.JointCtrl(*joint_values)

        # print(f"控制关节角度: {joint_angles} -> 指令值: {joint_values}")
        time.sleep(0.005)

    def center_arm(self):
        for slider in self.sliders:
            slider.setValue(0)
        self.update_joint_value()

    def randomize_arm(self):
        for i, slider in enumerate(self.sliders):
            min_angle, max_angle = self.joint_ranges_random[i]
            random_value = random.randint(int(min_angle * 1000), int(max_angle * 1000))
            slider.setValue(random_value)
        self.update_joint_value()