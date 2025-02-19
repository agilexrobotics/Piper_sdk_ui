import os
import sys
import time
import re
from typing import Optional
from PyQt5.QtWidgets import (QWidget, QApplication, QGridLayout, QTextEdit, QFrame, QMessageBox, QInputDialog, QLineEdit)
from PyQt5.QtGui import QPixmap, QTextCursor
from PyQt5.QtCore import Qt, QProcess

from piper_sdk import C_PiperInterface_V2  
from scripts.thread_module import MyClass 
from scripts.WidgetCreator import WidgetCreator

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_variables()   # 初始化变量和标志
        self.init_ui()          # 初始化界面控件
        self.init_layout()      # 布局控件
        self.init_connections() # 连接信号与槽

    def init_variables(self):
        # 初始化各类标志和变量
        self.is_found = False         # 是否查找到端口
        self.is_activated = False     # 端口是否激活
        self.is_enable = False        # 夹爪行程是否设置
        self.master_flag = False      # 主从臂标志（True 表示主臂）
        self.selected_port = 0        # 默认选中第 0 个端口
        self.selected_arm = None      # 主/从臂模式
        self.port_matches = []        # 存储查找到的端口信息，每个元素为 [端口名称, 端口号, 是否激活]
        self.piper = None             # piper 接口对象
        self.piper_interface_flag = {}# 每个端口对应的 piper 接口创建标志
        self.password = None          # 密码
        self.enable_status_thread = None  # 关节使能状态线程
        self.Teach_pendant_stroke = 100   # 示教器行程
        self.start_button_pressed = False  # 信息读取开始标志
        self.start_button_pressed_select = True
        self.flag = None              # 主从切换确认标志
        self.can_fps = 0              # can口的fps
        self.limited_timers = {}  # 存储不同函数的定时器
        self.last_update_enable_status_time = 0 # 记录更新使能状态和can断开警告触发时间
        self.last_canwarning_time = 0 # 记录can断开警告触发时间
        self.last_findcan_time = 0 # 记录查找can触发时间
        self.first_activatecan = False # 记录第一次activate，防止第一次触发can_warning
        self.warning_shown = False # warning是否已弹出

    def init_ui(self):
        self.setWindowTitle('Piper SDK Tools')
        self.resize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint |
                            Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        # 窗口居中
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move((screen_geometry.width() - self.width()) // 2,
                  (screen_geometry.height() - self.height()) // 2)
        self.layout = QGridLayout(self)
        self.text_edit = QTextEdit()  # 用于打印终端信息
        # 实例化控件创建
        self.widget_creator = WidgetCreator()
        # 创建各部分控件
        self.create_can_port_widgets()
        self.create_arm_selection_widgets()
        self.create_activation_widgets()
        self.create_gripper_teaching_widgets()
        self.create_hardware_widgets()
        self.create_read_info_widgets()
        self.create_extra_widgets()
        self.create_logo()

    def init_layout(self):
        # 第一行：查找端口、端口选择、端口名称、激活端口、使能、失能按钮
        self.layout.addWidget(self.button_findcan, 0, 0)
        self.layout.addWidget(self.port_combobox, 0, 1)
        self.layout.addWidget(self.name_edit, 0, 2)
        self.layout.addWidget(self.button_activatecan, 0, 3)
        self.layout.addWidget(self.button_enable, 0, 4)
        self.layout.addWidget(self.button_disable, 0, 5)
        # 第二行：重置、夹爪零点、到达零点、主从臂选择、参数初始化按钮
        self.layout.addWidget(self.button_reset, 1, 0)
        self.layout.addWidget(self.button_gripper_zero, 1, 1)
        self.layout.addWidget(self.button_go_zero, 1, 2)
        self.layout.addWidget(self.arm_combobox, 1, 3)
        self.layout.addWidget(self.button_config_init, 1, 4)
        self.layout.addWidget(self.button_piper_stop, 1, 5)
        # 第三行：添加 夹爪示教器参数设置框 和 信息读取框
        self.layout.addWidget(self.gripper_teaching_frame, 2, 0, 5, 3)
        self.layout.addWidget(self.read_frame, 2, 3, 5, 5)
        # 右上角添加 Logo 和硬件版本显示、can帧率显示、关节使能状态显示
        col = self.layout.columnCount()
        self.layout.addWidget(self.label, 0, col)
        self.layout.addWidget(self.hardware_edit, 1, col)
        self.layout.addWidget(self.button_hardware, 2, col)
        self.layout.addWidget(self.enable_status_edit_frame, 3, col-2, 4, col-2)
        # 底部添加取消、退出按钮及终端信息打印窗口
        downrow=self.layout.rowCount()
        self.layout.addWidget(self.button_cancel, downrow+5, col)
        self.layout.addWidget(self.button_close, downrow+6, col)
        self.layout.addWidget(self.text_edit, downrow, 0, downrow, round(col/2)-1)
        self.layout.addWidget(self.message_edit, downrow, round(col/2)-1, downrow, col-3)
    
    def init_connections(self):
        # 连接各控件信号和对应槽函数
        self.button_findcan.clicked.connect(self.run_findcan)
        self.button_activatecan.clicked.connect(self.run_activatecan)
        self.button_enable.clicked.connect(self.run_enable)
        self.button_disable.clicked.connect(self.run_disable)
        self.button_reset.clicked.connect(self.run_reset)
        self.button_go_zero.clicked.connect(self.run_go_zero)
        self.button_gripper_zero.clicked.connect(self.run_gripper_zero)
        self.button_config_init.clicked.connect(self.run_config_init)
        self.button_piper_stop.clicked.connect(self.run_piper_stop)
        self.slider.valueChanged.connect(self.update_stroke)
        self.button_confirm.clicked.connect(self.confirm_gripper_teaching_pendant_param_config)
        self.button_gripper_clear_err.clicked.connect(self.gripper_clear_err)
        self.button_hardware.clicked.connect(self.readhardware)
        self.button_read_acc_limit.clicked.connect(self.read_max_acc_limit)
        self.button_start_print.clicked.connect(self.Confirmation_of_message_reading_type_options)
        self.button_stop_print.clicked.connect(self.stop_print)
        self.button_installpos_confirm.clicked.connect(self.installation_position_config)
        self.arm_combobox.currentIndexChanged.connect(self.on_arm_mode_combobox_select)
        self.port_combobox.currentIndexChanged.connect(self.on_port_combobox_select)
        self.button_cancel.clicked.connect(self.cancel_process)
        self.button_close.clicked.connect(self.close)
        self.gripper_slider.valueChanged.connect(self.update_gripper)

    # ==============================
    # 创建各部分控件的函数
    # ==============================
    def create_can_port_widgets(self):
        # 查找 CAN 端口相关控件
        self.button_findcan = self.widget_creator.create_button('Find CAN Port')
        self.port_combobox = self.widget_creator.create_combo_box(size=(150, 40))
        self.name_edit = self.widget_creator.create_text_edit(size=(150, 40))
        self.button_activatecan = self.widget_creator.create_button('Activate CAN Port', enabled=self.is_found)

    def create_arm_selection_widgets(self):
        # 主/从臂选择下拉框
        self.arm_combobox = self.widget_creator.create_combo_box(
        items=["Slave", "Master"], 
        size=(150, 40),
        enabled=self.is_found and self.is_activated
        )

    def create_activation_widgets(self):
        # 机械臂操作相关按钮：使能、失能、重置、到零点、夹爪归零、参数初始化
        self.button_enable = self.widget_creator.create_button(text="Enable", enabled=self.is_found and self.is_activated)
        self.button_disable = self.widget_creator.create_button(text="Disable", enabled=self.is_found and self.is_activated)
        self.button_reset = self.widget_creator.create_button(text="Reset", enabled=self.is_found and self.is_activated)
        self.button_go_zero = self.widget_creator.create_button(text="Go Zero", enabled=self.is_found and self.is_activated)
        self.button_gripper_zero = self.widget_creator.create_button(text="Gripper Zero", enabled=self.is_found and self.is_activated)
        self.button_config_init = self.widget_creator.create_button(text="Config Init", enabled=self.is_found and self.is_activated)
        self.button_piper_stop = self.widget_creator.create_button(text="Stop", enabled=self.is_found and self.is_activated)

    def create_gripper_teaching_widgets(self):
        # 夹爪及示教器参数设置框
        self.gripper_teaching_frame = self.widget_creator.create_frame(frame_shape=QFrame.Box,line_width=1)
        # 示教器行程滑块、标签及显示框
        self.slider_label = self.widget_creator.create_label("Teach pendant stroke", size=(150, 15))
        self.slider = self.widget_creator.create_slider(min_value=100, max_value=200, value=100, orientation='horizontal', enabled=self.is_found and self.is_activated)
        self.slider_text_edit = self.widget_creator.create_text_edit(size=(60, 30), read_only=True)
        # 夹爪行程下拉框
        self.gripper_combobox_label = self.widget_creator.create_label("Gripper stroke", size=(150, 15))
        self.gripper_combobox = self.widget_creator.create_combo_box(items=["70", "0", "100"], size=(60, 30), enabled=self.is_found and self.is_activated)
        self.button_confirm = self.widget_creator.create_button(text="Confirm", size=(80, 40), enabled=self.is_found and self.is_activated)
        # 夹爪清错按钮
        self.button_gripper_clear_err = self.widget_creator.create_button(text="Gripper\ndisable\nand\nclear err", size=(60, 80), enabled=self.is_found and self.is_activated)
        # 夹爪控制滑块
        self.gripper_slider_label = self.widget_creator.create_label("Gripper control", size=(150, 15))
        self.gripper_slider = self.widget_creator.create_slider(min_value=0, max_value=70, value=0, orientation='horizontal', enabled=self.is_enable)
        self.gripper_slider_edit = self.widget_creator.create_text_edit(size=(60, 30), read_only=True)
        gripper_teaching_layout = [
            (self.slider_label, 0, 0),
            (self.slider, 1, 0),
            (self.slider_text_edit, 1, 1),
            (self.gripper_combobox_label, 2, 0),
            (self.gripper_combobox, 3, 0),
            (self.button_confirm, 3, 1),
            (self.button_gripper_clear_err, 1, 2, 5, 3),
            (self.gripper_slider_label, 4, 0),
            (self.gripper_slider, 5, 0),
            (self.gripper_slider_edit, 5, 1)
        ]
        self.widget_creator.add_layout_to_frame(self.gripper_teaching_frame, gripper_teaching_layout)
    
    def create_hardware_widgets(self):
        # 硬件版本显示相关控件
        self.button_hardware = self.widget_creator.create_button("hardware version", size=(150, 40), enabled=self.is_found and self.is_activated)
        self.hardware_edit = self.widget_creator.create_text_edit(size=(150, 40), enabled=True, read_only=True)

    def create_read_info_widgets(self):
        # 信息读取区域
        self.read_frame = self.widget_creator.create_frame(frame_shape=QFrame.Box, line_width=1)
        self.Status_information_reading_label = self.widget_creator.create_label('Status information reading',size=(150,40))
        self.button_read_acc_limit = self.widget_creator.create_button('Max Acc Limit', size=(120, 40), enabled=self.is_found and self.is_activated)
        self.read_combobox = self.widget_creator.create_combo_box(
            items=["Angle Speed Limit", "joint Status", "Gripper Status", "Piper Status", "FK"],
            size=(150, 40),
            enabled=self.is_found and self.is_activated and self.start_button_pressed_select
        )
        self.button_start_print = self.widget_creator.create_button('Start', size=(80, 40), enabled=self.is_found and self.is_activated)
        self.button_stop_print = self.widget_creator.create_button('Stop', size=(80, 40), enabled=self.is_found and self.is_activated and self.start_button_pressed)
        self.installpos_combobox_lable = self.widget_creator.create_label('Installation position',size=(120,40))
        self.installpos_combobox = self.widget_creator.create_combo_box(
            items=["Parallel", "Left", "Right"],
            size=(150, 40),
            enabled=self.is_found and self.is_activated
        )
        self.button_installpos_confirm = self.widget_creator.create_button('Confirm', size=(80, 40), enabled=self.is_found and self.is_activated)
        # 创建 QTextEdit
        self.message_edit = QTextEdit()
        # 将信息读取相关控件添加到布局中
        read_layout = [
            (self.Status_information_reading_label, 0, 0 ),
            (self.button_read_acc_limit, 0, 1 ),
            (self.read_combobox, 1, 0 ),
            (self.button_start_print, 1, 1 ),
            (self.button_stop_print, 1, 2 ),
            (self.installpos_combobox_lable, 2, 0 ),
            (self.installpos_combobox, 3, 0 ),
            (self.button_installpos_confirm, 3, 1)
            ]
        self.widget_creator.add_layout_to_frame(self.read_frame, read_layout)
    
    def create_extra_widgets(self):
        # 关节使能状态显示 can帧率显示及取消、退出按钮
        self.enable_status_edit_lable = self.widget_creator.create_label('Enable flag', size=(150, 20))
        self.enable_status_edit = self.widget_creator.create_text_edit(size=(90, 30), enabled=True, read_only=True)
        self.can_fps_edit_lable = self.widget_creator.create_label('Can fps', size=(150, 20))
        self.can_fps_edit = self.widget_creator.create_text_edit(size=(90, 30), enabled=True, read_only=True)
        self.enable_status_edit_frame = self.widget_creator.create_frame(line_width=0)
        enable_status_edit_layout = [(self.enable_status_edit_lable, 0, 0),(self.enable_status_edit, 1, 0),
                                     (self.can_fps_edit_lable, 2, 0),(self.can_fps_edit, 3, 0)]
        self.widget_creator.add_layout_to_frame(self.enable_status_edit_frame,enable_status_edit_layout)
        self.button_cancel = self.widget_creator.create_button('Cancel', size=(150, 40), enabled=True)
        self.button_close = self.widget_creator.create_button('Close', size=(150, 40), enabled=True)

    def create_logo(self):
        # 添加 Logo 图片
        self.label = self.widget_creator.create_label('', size=(150, 40))
        main_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(main_dir, 'image', 'logo-white.png')
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(150, 40, Qt.KeepAspectRatio)  # 调整图片大小
        self.label.setPixmap(pixmap)
        self.label.setStyleSheet("background-color: black;")

    # ==============================
    # 集中更新界面状态的方法
    # ==============================
    def update_ui_states(self):
        self.base_state = self.is_found and self.is_activated
        self.arm_combobox.setEnabled(self.base_state)
        self.button_enable.setEnabled(self.base_state and not self.master_flag)
        self.button_disable.setEnabled(self.base_state and not self.master_flag)
        self.button_reset.setEnabled(self.base_state and not self.master_flag)
        self.button_go_zero.setEnabled(self.base_state and not self.master_flag)
        self.button_gripper_zero.setEnabled(self.base_state and not self.master_flag)
        self.button_config_init.setEnabled(self.base_state and not self.master_flag)
        self.button_piper_stop.setEnabled(self.base_state and not self.master_flag)
        self.slider.setEnabled(self.base_state and not self.master_flag)
        self.gripper_combobox.setEnabled(self.base_state and not self.master_flag)
        self.button_confirm.setEnabled(self.base_state and not self.master_flag)
        self.installpos_combobox.setEnabled(self.base_state and not self.master_flag)
        self.button_installpos_confirm.setEnabled(self.base_state and not self.master_flag)
        self.button_read_acc_limit.setEnabled(self.base_state)
        self.read_combobox.setEnabled(self.base_state and self.start_button_pressed_select)
        self.button_hardware.setEnabled(self.base_state)
        self.button_gripper_clear_err.setEnabled(self.base_state)
        self.name_edit.setEnabled(self.is_activated)
        self.button_start_print.setEnabled(self.base_state)
    
    # ==============================
    # 以下为各功能模块的槽函数和业务逻辑
    # ==============================
    # 弹出主从臂切换确认框
    def prompt_for_master_slave_config(self):
        reply = QMessageBox.question(self, "Attention!!!",
                                     "Please confirm if you want to switch to Slave mode.\nBefore switching to slave, make sure the robot arm has been manually returned to a position near the origin.\nOnce confirmed, the robotic arm will reset automatically.\nBe cautious of any potential drops!!!",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.flag = 1  # 确认后设置标志为 1
            self.text_edit.append(f"Flag set to: {self.flag}")
        else:
            self.text_edit.append("[Error]: Operation cancelled.")
        return self.flag

    # 弹出密码输入框
    def prompt_for_password(self):
        self.password, ok = QInputDialog.getText(self, "Permission Required", "Enter password:", QLineEdit.Password)
        if not ok or not self.password:
            self.text_edit.append("[Error]: No password entered or operation cancelled.")
            return None
        return self.password

    # can断开提醒
    def can_warning(self):
        current_time = time.time()
        if current_time - self.last_canwarning_time >= 5:  # 至少 5 秒间隔
            self.last_canwarning_time = current_time  # 更新触发时间
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)  # 设置消息框图标为警告
            msg.setWindowTitle("Warnning")  # 设置消息框标题
            msg.setText("No information for the CAN port.")  # 设置提示框的内容
            msg.setStandardButtons(QMessageBox.Ok)  # 设置标准按钮（“确定”按钮）
            msg.buttonClicked.connect(self.on_warning_ok)
            msg.exec_()  # 显示消息框
        else:
            return
    
    def on_warning_ok(self, button):
        # 当点击“确定”按钮时，重置标志位
        self.warning_shown = False

    # 输出终端信息
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.text_edit.append(data)

    # 查找端口
    def run_findcan(self):
        self.first_activatecan = True
        current_time = time.time()
        if current_time - self.last_findcan_time >= 0.1:  # 至少 0.1 秒间隔
            self.last_findcan_time = current_time  # 更新触发时
        else:
            return
        # 检查密码是否已设置
        if not self.password:
            self.password = self.prompt_for_password()
            if not self.password:
                return
        self.port_combobox.clear()  # 清空下拉框中的旧数据
        script_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir, 'find_all_can_port.sh')
        self.process = QProcess(self)
        command_find = f"echo {self.password} | sudo -S bash {script_path}"
        self.process.start('bash', ['-c', command_find])
        time.sleep(0.01)
        def updateprint():
            data = self.process.readAllStandardOutput().data().decode('utf-8')
            self.text_edit.append(data)
            # 正则表达式提取端口信息
            matches = re.findall(r'接口名称:\s*(\w+)\s*端口号:\s*([\w.-]+:\d+\.\d+)\s*是否已激活:\s*(\S+)', data)
            if matches:
                for match in matches:
                    self.text_edit.append(f"Port Name: {match[0]}  Port: {match[1]}  Activated: {match[2]}\n")
                    match_num = next((row for row in self.port_matches if row[1] == match[1]), None)
                    if match_num:
                        index = self.port_matches.index(match_num)
                        self.port_matches[index] = list(match)
                    else:
                        self.port_matches.append(list(match))
                    port_text = f"{match[0]}   Activated: {match[2]}"
                    port_name = match[0]
                    for i in range(self.port_combobox.count()):
                        item = self.port_combobox.itemText(i)
                        if port_name in item:
                            self.port_combobox.setItemText(i, port_text)
                            break
                    else:
                        self.port_combobox.addItem(port_text)
                    if 0 <= self.selected_port < len(self.port_matches):
                        if self.port_matches[self.selected_port][2] == str("True"):
                            self.is_activated = True
                        elif self.port_matches[self.selected_port][2] == str("False"):
                            self.is_activated = False
                    # 更新各控件状态
                    self.update_ui_states()
            else :
                self.is_activated = False
                self.update_ui_states()
            for row in self.port_matches:
                if len(row) > 0:
                    self.piper_interface_flag[row[0]] = False
            port_num = len(self.port_matches)
            self.text_edit.append(f"Found {port_num} ports\n")
        self.process.readyReadStandardOutput.connect(updateprint)
        self.is_found = True
        self.button_activatecan.setEnabled(self.is_found)

    # 激活端口
    def run_activatecan(self):
        self.first_activatecan = True
        if not self.port_matches:
            self.text_edit.append("[Error]: No ports found. Please run 'Find CAN Port' first.")
            return
        script_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir, 'can_activate.sh')
        port_speed = 1000000
        if 0 <= self.selected_port < len(self.port_matches):
            name_text = self.name_edit.toPlainText()
            if name_text != self.port_matches[self.selected_port][0]:
                port_match = list(self.port_matches[self.selected_port])
                port_match[0] = str(name_text)
                self.port_matches[self.selected_port] = tuple(port_match)
                port_text_local = f"{name_text}   Activated: {self.port_matches[self.selected_port][2]}"
                self.port_combobox.setItemText(self.selected_port, port_text_local)
            command = f"echo {self.password} | sudo -S bash {script_path} {name_text} {port_speed} {self.port_matches[self.selected_port][1]}"
        else:
            self.text_edit.append("[Error]: Please select a port again.")
            return
        self.process = QProcess(self)
        self.process.start('bash', ['-c', command])
        self.create_piper_interface(self.port_matches[self.selected_port][0], False)
        self.piper.ConnectPort(True)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.readhardware()
        # 重新查找端口以更新状态
        script_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir, 'find_all_can_port.sh')
        self.process_find = QProcess(self)
        command_find = f"echo {self.password} | sudo -S bash {script_path}"
        self.process_find.start('bash', ['-c', command_find])
        def updateprint():
            data = self.process_find.readAllStandardOutput().data().decode('utf-8')
            self.text_edit.append(data)
            matches = re.findall(r'接口名称:\s*(\w+)\s*端口号:\s*([\w.-]+:\d+\.\d+)\s*是否已激活:\s*(\S+)', data)
            if matches:
                for match in matches:
                    self.text_edit.append(f"Port Name: {match[0]}  Port: {match[1]}  Activated: {match[2]}\n")
                    match_num = next((row for row in self.port_matches if row[1] == match[1]), None)
                    if match_num:
                        index = self.port_matches.index(match_num)
                        self.port_matches[index] = list(match)
                    else:
                        self.port_matches.append(list(match))
                    port_text = f"{match[0]}   Activated: {match[2]}"
                    port_name = match[0]
                    for i in range(self.port_combobox.count()):
                        item = self.port_combobox.itemText(i)
                        if port_name in item:
                            self.port_combobox.setItemText(i, port_text)
                            break
                    else:
                        self.port_combobox.addItem(port_text)
                    if 0 <= self.selected_port < len(self.port_matches):
                        if self.port_matches[self.selected_port][2] == str("True"):
                            self.is_activated = True
                        elif self.port_matches[self.selected_port][2] == str("False"):
                            self.is_activated = False
                    # 更新各控件状态
                    self.update_ui_states()
        self.process_find.readyReadStandardOutput.connect(updateprint)
        self.run_findcan()

    # 创建 piper 接口
    def create_piper_interface(self, port: str, is_virtual: bool) -> Optional[C_PiperInterface_V2]:
        if self.piper_interface_flag.get(port) is False:
            self.piper = C_PiperInterface_V2(port, is_virtual)
            self.piper.ConnectPort(True)
            self.piper_interface_flag[port] = True

    # 线程中用于更新关节使能状态的函数
    def display_enable_fun(self):
        enable_list = []
        enable_list.append(int(self.piper.GetArmLowSpdInfoMsgs().motor_1.foc_status.driver_enable_status))
        enable_list.append(int(self.piper.GetArmLowSpdInfoMsgs().motor_2.foc_status.driver_enable_status))
        enable_list.append(int(self.piper.GetArmLowSpdInfoMsgs().motor_3.foc_status.driver_enable_status))
        enable_list.append(int(self.piper.GetArmLowSpdInfoMsgs().motor_4.foc_status.driver_enable_status))
        enable_list.append(int(self.piper.GetArmLowSpdInfoMsgs().motor_5.foc_status.driver_enable_status))
        enable_list.append(int(self.piper.GetArmLowSpdInfoMsgs().motor_6.foc_status.driver_enable_status))
        if all(x == 1 for x in enable_list):
            self.is_enable = True
            self.gripper_slider.setEnabled(self.is_enable)
        else:
            self.is_enable = False
            self.gripper_slider.setEnabled(self.is_enable)
        data = "".join(map(str, enable_list))
        can_fps = round(self.piper.GetCanFps())
        return data, can_fps

    def run_enable(self):
        self.piper.EnableArm(7)
        self.piper.GripperCtrl(0, 1000, 0x01, 0)
        self.text_edit.append("[Info]: Arm enable.")

    def run_disable(self):
        self.piper.DisableArm(7)
        self.piper.GripperCtrl(0, 1000, 0x02, 0)
        self.text_edit.append("[Info]: Arm disable.")

    def run_reset(self):
        self.piper.MotionCtrl_1(0x02, 0, 0)
        self.text_edit.append("[Info]: Arm reset.")
    
    def run_piper_stop(self):
        self.piper.MotionCtrl_1(0x01, 0, 0)
        self.text_edit.append("[Info]: Arm stop.")

    def run_go_zero(self):
        self.piper.MotionCtrl_2(0x01, 0x01, 100, 0x00)
        self.piper.JointCtrl(0, 0, 0, 0, 0, 0)
        time.sleep(0.01)
        self.text_edit.append("[Info]: Arm go zero.")

    def run_gripper_zero(self):
        self.piper.GripperCtrl(0, 1000, 0x00, 0)
        time.sleep(1.5)
        self.piper.GripperCtrl(0, 1000, 0x00, 0xAE)
        self.text_edit.append("[Info]: Gripper zero set.")

    def run_config_init(self):
        self.piper.ArmParamEnquiryAndConfig(0x01, 0x02, 0, 0, 0x02)
        self.piper.SearchAllMotorMaxAngleSpd()
        self.text_edit.append(str(self.piper.GetAllMotorAngleLimitMaxSpd()))
        self.text_edit.append("[Info]: Config init.")
        time.sleep(0.01)

    def update_stroke(self):
        self.Teach_pendant_stroke = self.slider.value()
        self.slider_text_edit.clear()
        self.slider_text_edit.append(f"{self.Teach_pendant_stroke}")
        print(f"Current Teach pendant stroke: {self.Teach_pendant_stroke}")

    def confirm_gripper_teaching_pendant_param_config(self):
        if self.gripper_combobox.currentIndex() == 0:
            self.gripper_pendant = 70
            self.gripper_slider.setRange(0, 70)
        elif self.gripper_combobox.currentIndex() == 1:
            self.gripper_pendant = 0
            self.gripper_slider.setRange(0, 0)
        elif self.gripper_combobox.currentIndex() == 2:
            self.gripper_pendant = 100
            self.gripper_slider.setRange(0, 100)
        self.piper.GripperTeachingPendantParamConfig(self.Teach_pendant_stroke, self.gripper_pendant)
        self.text_edit.append(f"Teaching pendant stroke: {self.Teach_pendant_stroke}\nGripper stroke: {self.gripper_pendant}")

    def update_text(self, edit):
        cursor = edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        edit.setTextCursor(cursor)
        edit.ensureCursorVisible()
    
    def read_max_acc_limit(self):
        self.piper.SearchAllMotorMaxAccLimit()
        self.message_edit.append(f"{self.piper.GetAllMotorMaxAccLimit()}")

    def read_max_angle_speed(self):
        self.piper.SearchAllMotorMaxAngleSpd()
        return f"{self.piper.GetAllMotorAngleLimitMaxSpd()}"

    def read_joint_status(self):
        return f"{self.piper.GetArmJointMsgs()}"

    def read_gripper_status(self):
        return f"{self.piper.GetArmGripperMsgs()}"

    def read_piper_status(self):
        return f"{self.piper.GetArmStatus()}"
    
    def getfk(self):
        feedback = self.piper.GetFK('feedback')
        control = self.piper.GetFK('control')
        joint_data = {
            "Feedback": {f"Joint {i + 1}": feedback[i] for i in range(len(feedback))},
            "Control": {f"Joint {i + 1}": control[i] for i in range(len(control))}
        }
        return (f"Feedback:\n" + 
                "\n".join([f"  {joint}: {value}" for joint, value in joint_data["Feedback"].items()]) + 
                f"\nControl:\n" + 
                "\n".join([f"  {joint}: {value}" for joint, value in joint_data["Control"].items()]))
    
    def update_label(self, data):
        max_chars = 50000  # 设置最大字符数
        new_text = " ".join(map(str, data)) + "\n"

        # 在文本末尾追加新内容
        self.message_edit.moveCursor(QTextCursor.End)
        self.message_edit.insertPlainText(new_text)

        # 获取当前文本
        current_text = self.message_edit.toPlainText()

        # 如果字符数超过 max_chars，删除最早的部分
        if len(current_text) > max_chars:
            self.message_edit.setPlainText(current_text[-max_chars:])

        self.update_text(self.message_edit)
        time.sleep(0.01)

    def update_enable_status(self, data):
        current_time = time.time()
        if current_time - self.last_update_enable_status_time >= 0.1:
            self.last_update_enable_status_time = current_time  # 更新触发时间
            self.enable_status_edit.clear()
            self.enable_status_edit.append(data[0])
            self.can_fps_edit.clear()
            self.can_fps = data[1]
            self.can_fps_edit.append(str(data[1]))
            if self.can_fps == 0:
                self.can_warning()
                self.piper.DisconnectPort(True)
                self.is_activated = False
            elif self.can_fps >= 2000:
                self.piper.ConnectPort(True)
                self.is_activated = True
            else: 
                self.piper.ConnectPort(True)

    def Confirmation_of_message_reading_type_options(self):
        selected_index = self.read_combobox.currentIndex() if self.read_combobox.currentIndex() >= 0 else 0
        self.start_button_pressed = True
        self.start_button_pressed_select = False
        self.button_start_print.setEnabled(self.is_found and self.is_activated and not self.start_button_pressed)
        self.button_stop_print.setEnabled(self.is_found and self.is_activated and self.start_button_pressed)
        self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)
        if selected_index == 0:
            self.text_edit.append("[Info]: Reading angle speed limit.")
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.read_max_angle_speed)
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 1:
            self.text_edit.append("[Info]: Reading joint status.")
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.read_joint_status)
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 2:
            self.text_edit.append("[Info]: Reading gripper status.")
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.read_gripper_status)
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 3:
            self.text_edit.append("[Info]: Reading piper status.")
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.read_piper_status)
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 4:
            self.text_edit.append("[Info]: Reading FK.")
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.getfk)
            self.message_thread.worker.update_signal.connect(self.update_label)
        else:
            self.text_edit.append("[Error]: Please select a type to read.")
    
    def stop_print(self):
        self.text_edit.append("[Info]: Stop print.")
        self.message_thread.stop_reading_thread()
        self.start_button_pressed = False
        self.start_button_pressed_select = True
        self.button_start_print.setEnabled(self.is_found and self.is_activated and not self.start_button_pressed)
        self.button_stop_print.setEnabled(self.is_found and self.is_activated and self.start_button_pressed)
        self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)

    def gripper_ctrl(self):
        self.piper.GripperCtrl(abs(self.gripper * 1000), 1000, 0x01, 0)

    def gripper_clear_err(self):
        self.piper.GripperCtrl(abs(self.gripper * 1000), 1000, 0x02, 0)
        self.text_edit.append("[Info]: Gripper clear err.")

    def readhardware(self):
        """
        读取硬件版本信息，并显示在 hardware_edit 控件中。
        """
        time.sleep(0.1)
        if self.piper:
            version = self.piper.GetPiperFirmwareVersion()
            self.hardware_edit.setText(f"Hardware version\n{version}")

    def update_gripper(self):
        self.gripper = self.gripper_slider.value()
        self.gripper_slider_edit.clear()
        self.gripper_slider_edit.append(f"{self.gripper}")
        self.gripper_ctrl()

    def installation_position_config(self):
        if self.installpos_combobox.currentIndex() == 0:
            self.piper.MotionCtrl_2(0x01, 0x01, 0, 0, 0, 0x01)
            mode = "Parallel"
        elif self.installpos_combobox.currentIndex() == 1:
            self.piper.MotionCtrl_2(0x01, 0x01, 0, 0, 0, 0x02)
            mode = "Left"
        elif self.installpos_combobox.currentIndex() == 2:
            self.piper.MotionCtrl_2(0x01, 0x01, 0, 0, 0, 0x03)
            mode = "Right"
        self.text_edit.append(f"Arm installation position set: {mode}")

    def on_arm_mode_combobox_select(self):
        self.selected_arm = "slave" if self.arm_combobox.currentIndex() == 0 else "master"
        self.text_edit.append(f"Selected Arm: {self.selected_arm}")
        self.master_slave_config()

    def update_ui_states_master(self):
        self.base_state = self.is_found and self.is_activated
        self.button_enable.setEnabled(self.base_state and not self.master_flag)
        self.button_disable.setEnabled(self.base_state and not self.master_flag)
        self.button_go_zero.setEnabled(self.base_state and not self.master_flag)
        self.button_gripper_zero.setEnabled(self.base_state and not self.master_flag)
        self.button_config_init.setEnabled(self.base_state and not self.master_flag)
        self.button_piper_stop.setEnabled(self.base_state and not self.master_flag)
        self.slider.setEnabled(self.base_state and not self.master_flag)
        self.gripper_combobox.setEnabled(self.base_state and not self.master_flag)
        self.button_confirm.setEnabled(self.base_state and not self.master_flag)
        self.installpos_combobox.setEnabled(self.base_state and not self.master_flag)
        self.button_installpos_confirm.setEnabled(self.base_state and not self.master_flag)
        self.button_confirm.setEnabled(self.base_state and not self.master_flag)
        self.button_gripper_clear_err.setEnabled(self.base_state and not self.master_flag)

    def master_slave_config(self):
        if self.selected_arm == "master":
            self.piper.MasterSlaveConfig(0xFA, 0, 0, 0)
            self.master_flag = True
            self.update_ui_states_master()
        elif self.selected_arm == "slave":
            toslave = self.prompt_for_master_slave_config()
            if toslave == 1:
                self.master_flag = False
                self.update_ui_states_master()
                self.piper.MasterSlaveConfig(0xFC, 0, 0, 0)
                self.piper.MotionCtrl_2(0x01, 0x01, 100, 0x00)#位置速度模式
                self.text_edit.append(f"Master-Slave config set to: Slave")
            else:
                self.text_edit.append(f"Master-Slave config still set to: Master")

    def on_port_combobox_select(self):
        if not self.selected_port:
            self.selected_port = 0
        current_index = self.port_combobox.currentIndex()
        self.piper_interface_flag[f"{self.port_matches[self.selected_port][0]}"] = False
        if current_index >= 0:
            self.selected_port = current_index  # 更新为有效的选择
            self.create_piper_interface(f"{self.port_matches[self.selected_port][0]}", False)
            self.text_edit.append(f"Selected Port: can{self.selected_port}")
        else:
            self.text_edit.append("No valid port selected. Please select again.")
            return
        if 0 <= self.selected_port < len(self.port_matches):
            self.name_edit.clear()
            self.name_edit.append(self.port_matches[self.selected_port][0])
            if self.port_matches[self.selected_port][2] == str(True):
                self.is_activated = True
                self.readhardware()
            if self.enable_status_thread is None:
                self.enable_status_thread = MyClass() # 线程初始化
                self.enable_status_thread.start_reading_thread(self.display_enable_fun)  # 启动线程
                self.enable_status_thread.worker.update_signal.connect(self.update_enable_status)
            elif self.port_matches[self.selected_port][2] == str(False): 
                self.is_activated = False
        else :
            self.show_warning()
        self.update_ui_states()

    def cancel_process(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()
            self.text_edit.append("[Info]: Process terminated.")
        else:
            self.text_edit.append("[Error]: No running process to terminate.")

    def close(self):
        return super().close()
# 运行程序的入口函数
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
