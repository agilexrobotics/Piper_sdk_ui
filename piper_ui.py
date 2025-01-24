import sys
import os
import re
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QGridLayout, QPushButton, QTextEdit, QInputDialog, QLineEdit, QSlider, QLabel, QFrame
from PyQt5.QtCore import QProcess, Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QComboBox 
from typing import (
    Optional,
)
# from sip import registerMetaType
from PyQt5.QtGui import QTextCursor, QPixmap
# registerMetaType(QTextCursor)

import time
from piper_sdk import *
from PyQt5.QtWidgets import QMessageBox
import threading

class Worker(QObject):
    """执行具体任务的工作者类"""
    finished = pyqtSignal()  # 任务完成信号，用于通知线程结束
    update_signal = pyqtSignal(object)  # 更新信号，用于传递数据到主线程

    def __init__(self, stop_event, target, parent=None):
        super().__init__(parent)
        if not callable(target):
            raise ValueError("提供的 target 必须是可调用的函数")
        self.stop_event = stop_event
        self.target = target  # 需要在线程中运行的函数

    def run(self):
        """具体的线程任务"""
        if not self.target:
            print("未提供目标函数，无法执行任务")
            self.finished.emit()
            return
        try:
            while not self.stop_event.is_set():
                start_time = time.time()  # 获取当前时间
                data = self.target()  # 执行目标函数并获取返回值
                self.update_signal.emit(data)  # 将数据发送到主线程
                elapsed_time = time.time() - start_time  # 计算执行时间
                sleep_time = max(0, 0.1 - elapsed_time)  # 计算需要等待的时间，以保持50Hz
                time.sleep(sleep_time)  # 控制循环频率
        except Exception as e:
            print(f"线程任务发生异常：{e}")
        finally:
            print("线程任务已停止")
            self.finished.emit()  # 发送完成信号

class MyClass(QObject):
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()  # 创建停止事件
        self.thread = None  # 线程对象

    def can_start_thread(self):
        """检查线程是否可以启动"""
        return not (self.thread and self.thread.isRunning())

    def start_reading_thread(self, target):
        """启动线程"""
        if not callable(target):
            print("提供的 target 不是可调用的函数")
            return

        if not self.can_start_thread():
            print("线程已在运行，无需启动")
            return

        # 创建线程
        self.thread = QThread()
        self.worker = Worker(self.stop_event, target)  # 创建工作者对象
        self.worker.moveToThread(self.thread)  # 将工作者移动到线程

        # 连接信号与槽
        self.thread.started.connect(self.worker.run)  # 线程启动时执行 run 方法
        self.worker.finished.connect(self.thread.quit)  # 任务完成时退出线程
        self.worker.finished.connect(self.worker.deleteLater)  # 删除工作者对象
        self.thread.finished.connect(self.thread.deleteLater)  # 删除线程对象

        # 将子线程数据更新信号连接到主线程槽
        self.worker.update_signal.connect(self.update_gui)

        # 启动线程
        self.stop_event.clear()  # 清除停止标志
        self.thread.start()

    def update_gui(self, data):
        """更新 GUI 的槽函数"""
        time.sleep(0.01)
        # print(f"更新 GUI：{data}")
        # 这里可以添加具体的 GUI 更新逻辑，例如更新 QLabel、QTextEdit 等。

    def stop_reading_thread(self):
        """停止线程"""
        if self.thread and self.thread.isRunning():
            self.stop_event.set()  # 通知线程停止
            self.thread.quit()  # 请求线程退出
            self.thread.wait()  # 等待线程完成
            print("线程已停止")
        else:
            print("线程未运行，无需停止")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Piper SDK Tools')  # 设置窗口标题
        self.resize(800, 600)  # 设置窗口大小
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        # 将窗口居中显示在屏幕上
        screen_geometry = QApplication.primaryScreen().geometry()
        self.move((screen_geometry.width() - self.width()) // 2,
                  (screen_geometry.height() - self.height()) // 2)
        self.layout = QGridLayout()  # 创建一个网格布局

        # 信息打印窗口
        self.text_edit = QTextEdit()  # 创建一个文本编辑控件
        # self.text_edit.setFixedSize(800, 300)  # 设置文本编辑控件的固定大小    

        # 已经查找标志
        self.is_found = False
        # 已经激活标志
        self.is_activated = False
        # 夹爪行程已经设置
        self.is_enable = False

        # 查找端口
        self.button_findcan = QPushButton('Find CAN Port')  # 创建一个按钮
        self.button_findcan.clicked.connect(self.run_findcan)  # 连接按钮点击事件到 run_findcan 方法
        self.button_findcan.setFixedSize(150, 40)  # 设置按钮的固定大小

        # 端口选择
        self.port_combobox = QComboBox(self)  
        self.port_combobox.setFixedSize(200, 40)
        self.selected_port = None
         
        # 主从臂选择
        self.arm_combobox = QComboBox(self)
        self.arm_combobox.setFixedSize(200, 40)
        self.selected_arm = None
        self.arm_combobox.addItem("Slave")
        self.arm_combobox.addItem("Master")

        # 是否切换到从臂标志
        self.flag = None
        self.arm_combobox.setEnabled(self.is_found and self.is_activated)
        self.master_flag = False

        # 更改端口名字
        self.name_edit = QTextEdit()
        self.name_edit.setFixedSize(100, 40)
        self.name_edit.setEnabled(self.is_activated)

        # 激活端口
        self.button_activatecan = QPushButton('Activate CAN Port')
        self.button_activatecan.clicked.connect(self.run_activatecan)
        self.button_activatecan.setFixedSize(150, 40)
        self.button_activatecan.setEnabled(self.is_found)


        # 机械臂使能
        self.button_enable = QPushButton('Enable')
        self.button_enable.clicked.connect(self.run_enable)
        self.button_enable.setFixedSize(150, 40)
        self.button_enable.setEnabled(self.is_found and self.is_activated)


        # 机械臂失能
        self.button_disable = QPushButton('Disable')
        self.button_disable.clicked.connect(self.run_disable)
        self.button_disable.setFixedSize(150, 40)
        self.button_disable.setEnabled(self.is_found and self.is_activated)

        # 重置机械臂
        self.button_reset = QPushButton('Reset')
        self.button_reset.clicked.connect(self.run_reset)
        self.button_reset.setFixedSize(150, 40)
        self.button_reset.setEnabled(self.is_found and self.is_activated)

        # 机械臂到达零点
        self.button_go_zero = QPushButton('Go Zero')
        self.button_go_zero.clicked.connect(self.run_go_zero)
        self.button_go_zero.setFixedSize(150, 40)
        self.button_go_zero.setEnabled(self.is_found and self.is_activated)

        # 夹爪零点设置
        self.button_gripper_zero = QPushButton('Gripper Zero')
        self.button_gripper_zero.clicked.connect(self.run_gripper_zero)
        self.button_gripper_zero.setFixedSize(150, 40)
        self.button_gripper_zero.setEnabled(self.is_found and self.is_activated)

        # 参数初始化
        self.button_config_init = QPushButton('Config Init')
        self.button_config_init.clicked.connect(self.run_config_init)
        self.button_config_init.setFixedSize(150, 40)
        self.button_config_init.setEnabled(self.is_found and self.is_activated)

        # 示教器行程滑块
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)  # 设置为水平滑块
        self.slider.setRange(100, 200)  # 设置滑块范围为100到200
        self.slider.setValue(100)  # 初始值为100
        self.slider.valueChanged.connect(self.update_stroke)  # 当滑块值变化时更新信息
        self.slider_label = QLabel('Teach pendant stroke')
        self.slider.setEnabled(self.is_found and self.is_activated)
        self.slider_text_edit = QTextEdit()
        self.slider_text_edit.setReadOnly(True)
        self.slider_text_edit.setFixedSize(60, 30)

        # 夹爪行程选择
        self.gripper_combobox = QComboBox(self)
        self.gripper_combobox.setFixedSize(200, 40)
        self.gripper_combobox.addItem("70")
        self.gripper_combobox.addItem("0")
        self.gripper_combobox.addItem("100")
        self.gripper_combobox_label = QLabel('Gripper stroke')
        self.gripper_combobox.setEnabled(self.is_found and self.is_activated)

        # 夹爪和示教器参数设置确认
        self.button_confirm = QPushButton('Confirm')
        self.button_confirm.clicked.connect(self.confirm_gripper_teaching_pendant_param_config)
        self.button_confirm.setFixedSize(80, 40)
        self.button_confirm.setEnabled(self.is_found and self.is_activated)

        # 夹爪清错
        self.button_gripper_clear_err = QPushButton('Gripper\ndisable\nand\nclear err')
        self.button_gripper_clear_err.clicked.connect(self.gripper_clear_err)
        self.button_gripper_clear_err.setFixedSize(60, 80)
        self.button_gripper_clear_err.setEnabled(self.is_found and self.is_activated)

        # 夹爪示教器参数设置确认框
        frame = QFrame()
        frame.setFrameShape(QFrame.Box)  # 设置为方框
        # frame.setFrameShadow(QFrame.Raised)  # 设置方框的阴影效果
        frame.setLineWidth(1)  # 设置边框宽度

        self.gripper_teaching_layout = QGridLayout(frame)
        self.gripper_teaching_layout.addWidget(self.slider_label, 0, 0)
        self.gripper_teaching_layout.addWidget(self.slider, 1, 0)
        self.gripper_teaching_layout.addWidget(self.slider_text_edit, 1, 1)
        self.gripper_teaching_layout.addWidget(self.gripper_combobox_label, 2, 0)
        self.gripper_teaching_layout.addWidget(self.gripper_combobox, 3, 0)
        self.gripper_teaching_layout.addWidget(self.button_confirm, 3, 1)
        self.gripper_teaching_layout.addWidget(self.button_gripper_clear_err, 1, 2, 5, 2)

        # 硬件信息
        self.button_hardware = QPushButton("hardware version")
        self.button_hardware.clicked.connect(self.readhardware)
        self.button_hardware.setFixedSize(150, 40)
        self.button_hardware.setEnabled(self.is_found and self.is_activated)

        self.hardware_edit = QTextEdit()
        self.hardware_edit.setReadOnly(True)
        self.hardware_edit.setFixedSize(150, 40)

        # logo
        self.label = QLabel(self)
        main_dir = os.path.dirname(os.path.abspath(__file__))
        # 构建图像文件的完整路径
        image_path = os.path.join(main_dir, 'logo-white.png')
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(150, 40, Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.label.resize(150, 40)
        self.label.setStyleSheet("background-color: black;")

        # 信息读取框
        read_frame = QFrame()
        read_frame.setFrameShape(QFrame.Box)  # 设置为方框
        # frame.setFrameShadow(QFrame.Raised)  # 设置方框的阴影效果
        read_frame.setLineWidth(1)  # 设置边框宽度
        self.read_layout = QGridLayout(read_frame)
        self.Status_information_reading_label = QLabel('Status information reading')

        self.button_read_acc_limit = QPushButton('Max Acc Limit')
        self.button_read_acc_limit.clicked.connect(self.read_max_acc_limit)
        self.button_read_acc_limit.setFixedSize(120, 40)
        self.button_read_acc_limit.setEnabled(self.is_found and self.is_activated)
        
        # 开始停止标志
        self.start_button_pressed = False
        self.start_button_pressed_select = True
        self.stop_button_pressed = False
        
        # 信息读取类型选项
        self.read_combobox = QComboBox(self)
        self.read_combobox.setFixedSize(200, 40)
        self.read_combobox.addItem("Angle Speed Limit")
        self.read_combobox.addItem("joint Status")
        self.read_combobox.addItem("Gripper Status")
        self.read_combobox.addItem("Piper Status")
        self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)

        # 信息读取类型选项确认
        self.button_read_confirm = QPushButton('Start')
        self.button_read_confirm.clicked.connect(self.Confirmation_of_message_reading_type_options)
        self.button_read_confirm.setFixedSize(80, 40)
        self.button_read_confirm.setEnabled(self.is_found and self.is_activated)

        # 停止打印信息
        self.button_stop_print = QPushButton('Stop')
        self.button_stop_print.setEnabled(self.is_found and self.is_activated and self.start_button_pressed)
        self.button_stop_print.clicked.connect(self.stop_print)
        self.button_stop_print.setFixedSize(80, 40)

        # 信息读取框网格布局
        self.read_layout.addWidget(self.Status_information_reading_label, 0, 0)
        self.read_layout.addWidget(self.button_read_acc_limit, 0, 1)
        self.read_layout.addWidget(self.read_combobox, 1, 0)
        self.read_layout.addWidget(self.button_read_confirm, 1, 1)
        self.read_layout.addWidget(self.button_stop_print, 1, 2)

        # 信息打印窗口
        self.message_edit = QTextEdit()  # 创建一个文本编辑控件
        self.message_edit.setReadOnly(True)
        # self.message_edit.setFixedSize(800, 300)

        # 夹爪控制滑块
        self.gripper_slider = QSlider()
        self.gripper_slider.setOrientation(Qt.Horizontal)  # 设置为水平滑块
        self.gripper_slider.setRange(0, 70)  # 设置滑块范围为100到200
        self.gripper_slider.setValue(0)  # 初始值为100
        self.gripper_slider.valueChanged.connect(self.update_gripper)  # 当滑块值变化时更新信息
        self.gripper_slider_lable = QLabel('Gripper control')
        self.gripper_slider.setEnabled(self.is_enable)
        self.gripper_slider_edit = QTextEdit()
        self.gripper_slider_edit.setReadOnly(True)
        self.gripper_slider_edit.setFixedSize(60, 30)

        self.gripper_teaching_layout.addWidget(self.gripper_slider_lable, 4, 0)
        self.gripper_teaching_layout.addWidget(self.gripper_slider, 5, 0)
        self.gripper_teaching_layout.addWidget(self.gripper_slider_edit, 5, 1)

        # 机械臂安装位置
        self.installpos_combobox = QComboBox(self)
        self.installpos_combobox.setFixedSize(200, 40)
        self.installpos_combobox_lable = QLabel('Installation position')
        self.installpos_combobox.addItem("Parallel")
        self.installpos_combobox.addItem("Left")
        self.installpos_combobox.addItem("Right")
        self.installpos_combobox.setEnabled(self.is_found and self.is_activated)

        # 安装位置确认
        self.button_installpos_confirm = QPushButton('Confirm')
        self.button_installpos_confirm.setFixedSize(80, 40)
        self.button_installpos_confirm.clicked.connect(self.installation_position_config)
        self.button_installpos_confirm.setEnabled(self.is_found and self.is_activated)

        self.read_layout.addWidget(self.installpos_combobox_lable, 2, 0)
        self.read_layout.addWidget(self.installpos_combobox, 3, 0)
        self.read_layout.addWidget(self.button_installpos_confirm, 3, 1)

        # 机械臂零点设置
        # self.button_joint_zero = QPushButton('Joint Zero')
        # self.button_joint_zero.clicked.connect(self.run_joint_zero)
        # self.button_joint_zero.setFixedSize(150, 40)
        # self.button_joint_zero.setEnabled(self.is_found and self.is_activated)

        # 关节使能状态显示
        self.enable_status_edit = QTextEdit()
        self.enable_status_edit.setReadOnly(True)
        self.enable_status_edit.setFixedSize(70, 30)
        self.enable_status_edit_lable = QLabel('Joint enable status(0->disable, 1->enable)')

        # 取消按钮
        self.button_cancel = QPushButton('Cancel')
        self.button_cancel.clicked.connect(self.cancel_process)
        self.button_cancel.setFixedSize(150, 40)

        # 关闭窗口
        self.button_close = QPushButton('Exit')
        self.button_close.clicked.connect(self.close)
        self.button_close.setFixedSize(150, 40)

        # 布局
        self.layout.addWidget(self.button_findcan, 0, 0)  # 第0行，第0列
        self.layout.addWidget(self.port_combobox, 0, 1)
        self.layout.addWidget(self.name_edit, 0, 2)
        self.layout.addWidget(self.button_activatecan, 0, 3)
        self.layout.addWidget(self.button_enable, 0, 4)
        self.layout.addWidget(self.button_disable, 0, 5)

        self.layout.addWidget(self.button_reset, 1, 0)
        self.layout.addWidget(self.button_gripper_zero, 1, 1)
        self.layout.addWidget(self.button_go_zero, 1, 2)
        self.layout.addWidget(self.arm_combobox, 1, 3)
        self.layout.addWidget(self.button_config_init, 1, 4)
        self.layout.addWidget(frame, 2, 0, 3, 3)
        self.layout.addWidget(read_frame, 2, 3, 3, 4)
        self.layout.addWidget(self.label, 0, self.layout.columnCount())
        self.layout.addWidget(self.hardware_edit, 1, self.layout.columnCount()-1)
        self.layout.addWidget(self.button_hardware,2,self.layout.columnCount()-1)
        self.layout.addWidget(self.button_cancel, self.layout.rowCount()-1, self.layout.columnCount()-1)
        self.layout.addWidget(self.enable_status_edit_lable,self.layout.rowCount(), 0)
        self.layout.addWidget(self.enable_status_edit, self.layout.rowCount()-1, 1)
        self.layout.addWidget(self.button_close, self.layout.rowCount()-1, self.layout.columnCount()-1)
        self.layout.addWidget(self.text_edit, self.layout.rowCount(), 0, self.layout.rowCount(), round(self.layout.columnCount()/2)-1)  # 第1行，从第0列跨2列
        self.layout.addWidget(self.message_edit, self.layout.rowCount()-6, round(self.layout.columnCount()/2)-1, self.layout.rowCount()-6, self.layout.columnCount())  # 第1行，从第2列跨2列
        self.setLayout(self.layout)  # 设置主窗口的布局

        self.port_matches = []  # 初始化 port_matches 属性
        self.port_combobox.currentIndexChanged.connect(self.on_port_combobox_select)
        self.arm_combobox.currentIndexChanged.connect(self.on_arm_mode_combobox_select)

        self.password = None
        self.enable_status_thread = None
        self.Teach_pendant_stroke = 100

        self.piper = None
        self.already_warn = False

    def can_warning(self):
            # 创建警告消息框
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)  # 设置消息框图标为警告
        msg.setWindowTitle("Warnning")  # 设置消息框标题
        msg.setText("No information for the CAN port.")  # 设置提示框的内容
        msg.setStandardButtons(QMessageBox.Ok)  # 设置标准按钮（“确定”按钮）
        msg.exec_()  # 显示消息框
     
    # 读取硬件信息
    def readhardware(self):
        time.sleep(1)
        self.hardware_edit.setText(f"Hardware version\n{self.piper.GetPiperFirmwareVersion()}")

    def show_warning(self):
            # 创建警告消息框
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)  # 设置消息框图标为警告
        msg.setWindowTitle("Warnning")  # 设置消息框标题
        msg.setText("Invalid port selected, please re-find the CAN port.")  # 设置提示框的内容
        msg.setStandardButtons(QMessageBox.Ok)  # 设置标准按钮（“确定”按钮）
        msg.exec_()  # 显示消息框

    # 端口选择后的处理
    def on_port_combobox_select(self):
        if not hasattr(self, 'selected_port'):  # Check if 'selected_port' is already set
            self.selected_port = 0  # Set default value to the first item (index 0)

        current_index = self.port_combobox.currentIndex()
    
        # 检查是否有有效的选择（索引 >= 0）
        if current_index >= 0:
            self.selected_port = current_index  # 更新为有效的选择
            self.text_edit.append(f"Selected Port: can{self.selected_port}")
        else:
            # 如果没有有效选择，可以处理该情况
            self.text_edit.append("没有选择有效的端口。")
            self.text_edit.append(f"Selected Port: can{self.selected_port}")

        if 0 <= self.selected_port < len(self.port_matches):
            self.name_edit.clear()
            self.name_edit.append(self.port_matches[self.selected_port][0])
            # print(self.port_matches[0][2])
            if self.port_matches[self.selected_port][2] == str(True):
                self.is_activated = True
                self.create_piper_interface(f"{self.port_matches[self.selected_port][0]}", False)
                self.readhardware()
            if self.enable_status_thread is None:
                self.enable_status_thread = MyClass() # 线程初始化
                self.enable_status_thread.start_reading_thread(self.display_enable_fun)  # 启动线程
                self.enable_status_thread.worker.update_signal.connect(self.update_enable_status)
            elif self.port_matches[self.selected_port][2] == str(False): 
                self.is_activated = False
        else :
            self.show_warning()
        self.arm_combobox.setEnabled(self.is_found and self.is_activated)
        self.button_enable.setEnabled(self.is_found and self.is_activated)
        self.button_disable.setEnabled(self.is_found and self.is_activated)
        self.button_reset.setEnabled(self.is_found and self.is_activated)
        self.button_go_zero.setEnabled(self.is_found and self.is_activated)
        self.button_gripper_zero.setEnabled(self.is_found and self.is_activated)
        self.button_config_init.setEnabled(self.is_found and self.is_activated)
        self.slider.setEnabled(self.is_found and self.is_activated)
        self.gripper_combobox.setEnabled(self.is_found and self.is_activated)
        self.button_confirm.setEnabled(self.is_found and self.is_activated)
        self.button_read_confirm.setEnabled(self.is_found and self.is_activated)
        self.installpos_combobox.setEnabled(self.is_found and self.is_activated)
        self.button_installpos_confirm.setEnabled(self.is_found and self.is_activated)
        self.button_read_acc_limit.setEnabled(self.is_found and self.is_activated)
        self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)
        self.button_hardware.setEnabled(self.is_found and self.is_activated)
        self.button_gripper_clear_err.setEnabled(self.is_found and self.is_activated)
        self.name_edit.setEnabled(self.is_activated)

    # 主从臂选择后的处理
    def on_arm_mode_combobox_select(self):
        self.selected_arm = "slave" if self.arm_combobox.currentIndex() == 0 else "master"
        self.text_edit.append(f"Selected Arm: {self.selected_arm}")
        self.master_slave_config()

    # 主从臂配置切换
    def master_slave_config(self):
        if self.selected_arm == "master":
            self.piper.MasterSlaveConfig(0xFA, 0, 0, 0)
            self.master_flag = True
            self.button_enable.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_disable.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_go_zero.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_gripper_zero.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_config_init.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.slider.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.gripper_combobox.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_confirm.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.installpos_combobox.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_installpos_confirm.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_confirm.setEnabled(self.is_found and self.is_activated and not self.master_flag)
            self.button_gripper_clear_err.setEnabled(self.is_found and self.is_activated)

        elif self.selected_arm == "slave":
            toslave = self.prompt_for_master_slave_config()
            if toslave == 1:
                self.master_flag = False
                self.button_enable.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_disable.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_go_zero.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_gripper_zero.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_config_init.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.slider.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.gripper_combobox.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_confirm.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.installpos_combobox.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_installpos_confirm.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_confirm.setEnabled(self.is_found and self.is_activated and not self.master_flag)
                self.button_gripper_clear_err.setEnabled(self.is_found and self.is_activated)
                
                self.piper.MasterSlaveConfig(0xFC, 0, 0, 0)
                self.piper.MotionCtrl_2(0x01, 0x01, 100, 0x00)#位置速度模式
                self.text_edit.append(f"Master-Slave config set to: Slave")
            else:
                self.text_edit.append(f"Master-Slave config still set to: Master")

    # 弹出主从臂切换确认框
    def prompt_for_master_slave_config(self):       
        reply = QMessageBox.question(self, "Attention!!!", 
            "Please confirm if you want to switch to Slave mode.\nBefore switching to slave, make sure the robot arm has been manually returned to a position near the origin.\nOnce confirmed, the robotic arm will reset automatically.\nBe cautious of any potential drops!!!",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.flag = 1  # 确认后设置标志为1
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

    # 输出终端信息
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.text_edit.append(data)

    # 查找端口
    def run_findcan(self):
        # 检查密码是否已经设置
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
            # if not any(match[0] == matches[0] for match in self.port_matches):
            #     self.port_matches.extend(list(matches))

            if matches:
                for match in matches:
                    # 显示端口信息
                    self.text_edit.append(f"Port Name: {match[0]}  Port: {match[1]}  Activated: {match[2]}\n")
                    match_num = next((row for row in self.port_matches if row[1] == match[1]), None)
            
                    if match_num:
                        # 如果找到匹配的行，更新这一行
                        index = self.port_matches.index(match_num)
                        self.port_matches[index] = list(match)
                    else:
                        # 如果没有找到匹配的行，添加 matches 作为新的一行
                        self.port_matches.append(list(match))

                    # 创建要添加到下拉框的文本
                    port_text = f"{match[0]}   Activated: {match[2]}"
                    port_name = f"{match[0]}"
                    # 检查下拉框中是否已存在该端口
                    for i in range(self.port_combobox.count()):
                        item = self.port_combobox.itemText(i)
                        if port_name in item:  # 如果 port_name 部分匹配
                            self.port_combobox.setItemText(i, port_text)  # 更新已存在的项
                            break
                    else:
                        # 如果没有找到匹配项，才添加新项
                        self.port_combobox.addItem(port_text)
                    if 0 <= self.selected_port < len(self.port_matches):
                        if self.port_matches[self.selected_port][2] == str("True") :
                            self.is_activated = True
                        elif self.port_matches[self.selected_port][2] == str("False"): 
                            self.is_activated = False
                    self.arm_combobox.setEnabled(self.is_found and self.is_activated)
                    self.button_enable.setEnabled(self.is_found and self.is_activated)
                    self.button_disable.setEnabled(self.is_found and self.is_activated)
                    self.button_reset.setEnabled(self.is_found and self.is_activated)
                    self.button_go_zero.setEnabled(self.is_found and self.is_activated)
                    self.button_gripper_zero.setEnabled(self.is_found and self.is_activated)
                    self.button_config_init.setEnabled(self.is_found and self.is_activated)
                    self.slider.setEnabled(self.is_found and self.is_activated)
                    self.gripper_combobox.setEnabled(self.is_found and self.is_activated)
                    self.button_confirm.setEnabled(self.is_found and self.is_activated)
                    self.button_read_confirm.setEnabled(self.is_found and self.is_activated)
                    self.installpos_combobox.setEnabled(self.is_found and self.is_activated)
                    self.button_installpos_confirm.setEnabled(self.is_found and self.is_activated)
                    self.button_read_acc_limit.setEnabled(self.is_found and self.is_activated)
                    self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)
                    self.button_hardware.setEnabled(self.is_found and self.is_activated)
                    self.button_gripper_clear_err.setEnabled(self.is_found and self.is_activated)
                    self.name_edit.setEnabled(self.is_activated)


            port_num = len(self.port_matches)
            self.text_edit.append(f"Found {port_num} ports\n")

        self.process.readyReadStandardOutput.connect(updateprint)
        self.is_found = True
        time.sleep(0.05)

        self.button_activatecan.setEnabled(self.is_found)

        if not self.process.waitForStarted():
            self.text_edit.append("[Error]: Unable to start script.")
            return
        
    # 激活端口
    def run_activatecan(self):
        # 弹出密码输入框

        if not self.port_matches:
            self.text_edit.append("[Error]: No ports found. Please run 'Find CAN Port' first.")
            return 

        script_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir, 'can_activate.sh')
        port_speed = 1000000

        if 0 <= self.selected_port < len(self.port_matches):
            name_text = self.name_edit.toPlainText()
            # print (port_name)
            if name_text != self.port_matches[self.selected_port][0]:
                port_match = list(self.port_matches[self.selected_port])  # 转为 list
                port_match[0] = str(name_text) # 修改第一个元素
                self.port_matches[self.selected_port] = tuple(port_match)  # 转回 tuple
                port_text_local = f"{name_text}   Activated: {self.port_matches[self.selected_port][2]}"
                self.port_combobox.setItemText(self.selected_port, port_text_local)
            command = f"echo {self.password} | sudo -S bash {script_path} {name_text} {port_speed} {self.port_matches[self.selected_port][1]}"     
        else: 
            self.text_edit.append("[Error]: Please select a port again.")
            return
        # command = f"echo {password} | sudo -S bash {script_path} {'can1'} {1000000} {'3-1.4.4.1:1.0'}"
        # self.text_edit.append(f"Running command: {command}")
        self.process = QProcess(self)
        self.process.start('bash', ['-c', command])
        time.sleep(0.1)
        self.create_piper_interface(f"{self.port_matches[self.selected_port][0]}", False)
        # self.text_edit.append(f"Command has been run")

        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.readhardware()
        self.already_warn = False
        # 刷新关节使能状态
        if self.enable_status_thread is None:
            self.enable_status_thread = MyClass() # 线程初始化
            self.enable_status_thread.start_reading_thread(self.display_enable_fun)  # 启动线程
            self.enable_status_thread.worker.update_signal.connect(self.update_enable_status)
        script_dir = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir, 'find_all_can_port.sh')
        self.process_find = QProcess(self)
        command_find = f"echo {self.password} | sudo -S bash {script_path}"
        self.process_find.start('bash', ['-c', command_find])   
        self.process_find.finished.connect(self.on_process_find_finished)
        def updateprint():
            data = self.process_find.readAllStandardOutput().data().decode('utf-8')
            self.text_edit.append(data)

            # 正则表达式提取端口信息
            matches = re.findall(r'接口名称:\s*(\w+)\s*端口号:\s*([\w.-]+:\d+\.\d+)\s*是否已激活:\s*(\S+)', data)
            # if not matches in self.port_matches:
            #     self.port_matches.extend(list(matches))

            if matches:
                for match in matches:
                    # 显示端口信息
                    self.text_edit.append(f"Port Name: {match[0]}  Port: {match[1]}  Activated: {match[2]}\n")

                    match_num = next((row for row in self.port_matches if row[1] == match[1]), None)
            
                    if match_num:
                        # 如果找到匹配的行，更新这一行
                        index = self.port_matches.index(match_num)
                        self.port_matches[index] = list(match)
                    else:
                        # 如果没有找到匹配的行，添加 matches 作为新的一行
                        self.port_matches.append(list(match))

                    # 创建要添加到下拉框的文本
                    port_text = f"{match[0]}   Activated: {match[2]}"
                    port_name = f"{match[0]}"
                    # 检查下拉框中是否已存在该端口
                    for i in range(self.port_combobox.count()):
                        item = self.port_combobox.itemText(i)
                        if port_name in item:  # 如果 port_name 部分匹配
                            self.port_combobox.setItemText(i, port_text)  # 更新已存在的项
                            break
                    else:
                        # 如果没有找到匹配项，才添加新项
                        self.port_combobox.addItem(port_text)

                    if 0 <= self.selected_port < len(self.port_matches):
                        if self.port_matches[self.selected_port][2] == str("True") :
                            self.is_activated = True
                        elif self.port_matches[self.selected_port][2] == str("False"): 
                            self.is_activated = False
                    self.arm_combobox.setEnabled(self.is_found and self.is_activated)
                    self.button_enable.setEnabled(self.is_found and self.is_activated)
                    self.button_disable.setEnabled(self.is_found and self.is_activated)
                    self.button_reset.setEnabled(self.is_found and self.is_activated)
                    self.button_go_zero.setEnabled(self.is_found and self.is_activated)
                    self.button_gripper_zero.setEnabled(self.is_found and self.is_activated)
                    self.button_config_init.setEnabled(self.is_found and self.is_activated)
                    self.slider.setEnabled(self.is_found and self.is_activated)
                    self.gripper_combobox.setEnabled(self.is_found and self.is_activated)
                    self.button_confirm.setEnabled(self.is_found and self.is_activated)
                    self.button_read_confirm.setEnabled(self.is_found and self.is_activated)
                    self.installpos_combobox.setEnabled(self.is_found and self.is_activated)
                    self.button_installpos_confirm.setEnabled(self.is_found and self.is_activated)
                    self.button_read_acc_limit.setEnabled(self.is_found and self.is_activated)
                    self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)
                    self.button_hardware.setEnabled(self.is_found and self.is_activated)
                    self.button_gripper_clear_err.setEnabled(self.is_found and self.is_activated)
                    self.name_edit.setEnabled(self.is_activated)


        self.process_find.readyReadStandardOutput.connect(updateprint)
        time.sleep(0.05)

    # 创建piper接口
    def create_piper_interface(self, port: str, is_virtual: bool) -> Optional[C_PiperInterface_V2]:
        if self.piper is None:
            self.piper = C_PiperInterface_V2(port,is_virtual)
            self.piper.ConnectPort()
        
    
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

        if not self.piper.isOk():
            if self.already_warn == False:
                self.can_warning()
                self.already_warn = True
        else :
            time.sleep(1)

        return data
 
    # 机械臂使能
    def run_enable(self):
        self.piper.EnableArm(7)
        self.piper.GripperCtrl(0,1000,0x01, 0)
        self.text_edit.append("[Info]: Arm enable.")

    # 机械臂失能
    def run_disable(self):
        self.piper.DisableArm(7)
        self.piper.GripperCtrl(0,1000,0x02, 0)
        self.text_edit.append("[Info]: Arm disable.")

    # 重置机械臂
    def run_reset(self):
        self.piper.MotionCtrl_1(0x02,0,0)#恢复
        # self.piper.MotionCtrl_2(0, 0, 0, 0x00)#位置速度模式
        self.text_edit.append("[Info]: Arm reset.")

    # 机械臂到达零点
    def run_go_zero(self):  
        # for i in range(0, 6):        
            self.piper.MotionCtrl_2(0x01, 0x01, 100, 0x00)
            self.piper.JointCtrl(0, 0, 0, 0, 0, 0)
            time.sleep(0.01)
            self.text_edit.append("[Info]: Arm go zero.")
            pass   

    # 夹爪零点设置
    def run_gripper_zero(self):
        self.piper.GripperCtrl(0,1000,0x00, 0)
        time.sleep(1.5)
        self.piper.GripperCtrl(0,1000,0x00, 0xAE)
        self.text_edit.append("[Info]: Gripper zero set.")
    
    # 参数初始化
    def run_config_init(self):
        self.piper.ArmParamEnquiryAndConfig(0x01,0x02,0,0,0x02)
        self.piper.SearchAllMotorMaxAngleSpd()
        self.text_edit.append(str(self.piper.GetAllMotorAngleLimitMaxSpd()))
        self.text_edit.append("[Info]: Config init.")
        time.sleep(0.01)
    
    # 更新滑块值
    def update_stroke(self):
        # 更新记录的值，当滑块值变化时调用此方法
        self.Teach_pendant_stroke = self.slider.value()
        self.slider_text_edit.clear()
        self.slider_text_edit.append(f"{self.Teach_pendant_stroke}")
        print(f"Current Teach pendant stroke: {self.Teach_pendant_stroke}")  # 打印当前值
    
    # 夹爪和示教器参数设置确认
    def confirm_gripper_teaching_pendant_param_config(self):
        if self.gripper_combobox.currentIndex() == 0 :
            self.gripper_pendant = 70
            self.gripper_slider.setRange(0, 70)
        elif self.gripper_combobox.currentIndex() == 1 :
            self.gripper_pendant = 0
            self.gripper_slider.setRange(0, 0)
        elif self.gripper_combobox.currentIndex() == 2 :
            self.gripper_pendant = 100
            self.gripper_slider.setRange(0, 100)
        self.piper.GripperTeachingPendantParamConfig(self.Teach_pendant_stroke, self.gripper_pendant)
        self.text_edit.append(f"Teaching pendant stroke: {self.Teach_pendant_stroke}\nGripper stroke: {self.gripper_pendant}")

    def update_text(self,edit):
        cursor = QTextCursor()
        cursor = edit.textCursor()  # 获取 edit 的光标
        cursor.movePosition(cursor.End)  # 将光标移动到文本末尾
        edit.setTextCursor(cursor)  # 更新 edit 的光标位置
        edit.ensureCursorVisible()  # 确保光标可见

    # 读取最大加速度限制
    def read_max_acc_limit(self):
        self.piper.SearchAllMotorMaxAccLimit()
        self.message_edit.append(f"{self.piper.GetAllMotorMaxAccLimit()}") 
    
    # 读取最大角度和速度限制
    def read_max_angle_speed(self):
        self.piper.SearchAllMotorMaxAngleSpd()
        return(f"{self.piper.GetAllMotorAngleLimitMaxSpd()}")

    # 读取关节状态
    def read_joint_status(self):
        return(f"{self.piper.GetArmJointMsgs()}")

    def read_gripper_status(self):
        return(f"{self.piper.GetArmGripperMsgs()}")
    
    def read_piper_status(self):
        return(f"{self.piper.GetArmStatus()}")

    def update_label(self, data):
        self.message_edit.append(data)
        self.update_text(self.message_edit)
        time.sleep(0.01)

    def update_enable_status(self,data):
        self.enable_status_edit.clear()
        self.enable_status_edit.append(data)

    # 信息读取类型选择确认
    def Confirmation_of_message_reading_type_options(self):
        selected_index = 0
        self.start_button_pressed = True
        self.start_button_pressed_select = False
        self.button_stop_print.setEnabled(self.is_found and self.is_activated and self.start_button_pressed)
        self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)
        # 检查 currentIndex 是否有效
        if self.read_combobox.currentIndex() >= 0:
            selected_index = self.read_combobox.currentIndex()
        if selected_index == 0:
            self.text_edit.append("[Info]: Reading angle speed limit.")
            self.stop_button_pressed = False
            self.message_thread = MyClass() # 线程初始化
            self.message_thread.start_reading_thread(self.read_max_angle_speed)  # 启动线程
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 1:
            self.text_edit.append("[Info]: Reading joint status.")
            self.stop_button_pressed = False
            self.message_thread = MyClass() # 线程初始化
            self.message_thread.start_reading_thread(self.read_joint_status)  # 启动线程
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 2:
            self.text_edit.append("[Info]: Reading gripper status.")
            self.stop_button_pressed = False
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.read_gripper_status)
            self.message_thread.worker.update_signal.connect(self.update_label)
        elif selected_index == 3:
            self.text_edit.append("[Info]: Reading piper status.")
            self.stop_button_pressed = False
            self.message_thread = MyClass()
            self.message_thread.start_reading_thread(self.read_piper_status)
            self.message_thread.worker.update_signal.connect(self.update_label)
        else:
            self.text_edit.append("[Error]: Please select a type to read.")

    # 停止打印信息
    def stop_print(self):
        self.text_edit.append("[Info]: Stop print.")
        self.stop_button_pressed = True
        self.message_thread.stop_reading_thread()
        self.start_button_pressed = False
        self.start_button_pressed_select = True
        self.button_stop_print.setEnabled(self.is_found and self.is_activated and self.start_button_pressed)
        self.read_combobox.setEnabled(self.is_found and self.is_activated and self.start_button_pressed_select)
    # 夹爪控制
    def gripper_ctrl(self):
        self.piper.GripperCtrl(abs(self.gripper*1000), 1000, 0x01, 0)
    
    def gripper_clear_err(self):
        self.piper.GripperCtrl(abs(self.gripper*1000), 1000, 0x02, 0)

    # 更新夹爪控制滑块值
    def update_gripper(self):
        # 更新记录的值，当滑块值变化时调用此方法
        self.gripper = self.gripper_slider.value()
        self.gripper_slider_edit.clear()
        self.gripper_slider_edit.append(f"{self.gripper}")
        self.gripper_ctrl()
    
    def installation_position_config(self):
        if self.installpos_combobox.currentIndex() == 0 :
            self.piper.MotionCtrl_2(0x01,0x01,0,0,0,0x01)
            mode = "Parallel"  
        elif self.installpos_combobox.currentIndex() == 1 :
            self.piper.MotionCtrl_2(0x01,0x01,0,0,0,0x02)  
            mode = "Left"
        elif self.installpos_combobox.currentIndex() == 2 :
            self.piper.MotionCtrl_2(0x01,0x01,0,0,0,0x03)  
            mode = "Right"
        self.text_edit.append(f"Arm installation position set: {mode}")

    # 夹爪零点设置
    # def run_joint_zero(self):
    #     self.piper.JointConfig(7,0xAE)
    #     self.text_edit.append("[Info]: Joint zero set.")

    # 取消进程
    def cancel_process(self):
        if self.process and self.process.state() == QProcess.Running:
            self.process.terminate()  # 终止当前进程
            self.text_edit.append("[Info]: Process terminated.")
        else:
            self.text_edit.append("[Error]: No running process to terminate.")
    
    def close(self):
        return super().close()
    
    def on_process_find_finished(self):
        exit_code = self.process_find.exitCode()  # 获取进程的退出码
        if exit_code == 0:
            self.text_edit.append("[Info]: Process executed successfully.")
        else:
            self.text_edit.append(f"[Error]: Process failed with exit code {exit_code}.")


def main():
    app = QApplication(sys.argv)  # 创建应用程序对象
    window = MainWindow()  # 创建主窗口对象
    window.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入应用程序的主循环


if __name__ == '__main__':
    main()  # 如果是主模块，则运行 main 函数
