# thread_module.py
import threading
import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal

class Worker(QObject):
    """执行具体任务的工作者类"""
    finished = pyqtSignal()            # 任务完成信号，用于通知线程结束
    update_signal = pyqtSignal(object) # 更新信号，用于传递数据到主线程

    def __init__(self, stop_event, target, parent=None):
        """
        :param stop_event: 用于停止线程的 threading.Event 对象
        :param target: 需要在线程中运行的可调用目标函数
        """
        super().__init__(parent)
        if not callable(target):
            raise ValueError("提供的 target 必须是可调用的函数")
        self.stop_event = stop_event
        self.target = target

    def run(self):
        """具体的线程任务"""
        if not self.target:
            print("未提供目标函数，无法执行任务")
            self.finished.emit()
            return
        try:
            while not self.stop_event.is_set():
                start_time = time.time()  # 获取当前时间
                result = self.target()  # 执行目标函数并获取返回值
                # 判断返回值是否是元组
                if isinstance(result, tuple):
                    self.update_signal.emit(result)  # 返回多个值的情况，发送元组
                else:
                    self.update_signal.emit((result,))  # 单个值的情况，封装成元组发送
                elapsed_time = time.time() - start_time  # 计算执行时间
                sleep_time = max(0, 0.1 - elapsed_time)    # 计算等待时间（保持大约50Hz）
                time.sleep(sleep_time)
        except Exception as e:
            print(f"线程任务发生异常：{e}")
        finally:
            print("线程任务已停止")
            self.finished.emit()  # 发送完成信号

class MyClass(QObject):
    """线程管理类，用于启动和停止工作线程"""
    def __init__(self):
        super().__init__()
        self.stop_event = threading.Event()  # 创建停止事件
        self.thread = None                   # QThread 对象
        self.worker = None                   # Worker 对象

    def can_start_thread(self):
        """检查线程是否可以启动"""
        return not (self.thread and self.thread.isRunning())

    def start_reading_thread(self, target):
        """
        启动一个线程，并在其中运行目标函数 target
        :param target: 可调用函数，返回需要传递到主线程的数据
        """
        if not callable(target):
            print("提供的 target 不是可调用的函数")
            return

        if not self.can_start_thread():
            print("线程已在运行，无需启动")
            return

        # 创建 QThread 对象
        self.thread = QThread()
        # 创建 Worker 对象，将 stop_event 和目标函数传入
        self.worker = Worker(self.stop_event, target)
        # 将 Worker 对象移动到新线程中
        self.worker.moveToThread(self.thread)
        # 连接信号与槽：线程启动后调用 worker.run
        self.thread.started.connect(self.worker.run)
        # 当 worker 完成时退出线程并清理 worker 对象
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.start()

    def stop_reading_thread(self):
        """停止线程"""
        if self.thread and self.thread.isRunning():
            self.stop_event.set()   # 通知线程停止
            self.thread.quit()      # 请求线程退出
            self.thread.wait()      # 等待线程完成
            print("线程已停止")
        else:
            print("线程未运行，无需停止")
        self.stop_event.clear()     # 清除停止标志
