from PyQt5.QtWidgets import QPushButton, QTextEdit, QComboBox, QSlider, QLabel, QFrame, QGridLayout
from PyQt5.QtCore import Qt

class WidgetCreator:
    '''
    PyQt5 UI控件创建辅助类，可根据参数创建不同类型的控件。

    A helper class for creating PyQt5 UI widgets with customizable parameters.
    '''

    def __init__(self):
        pass

    def create_button(self, text: str, size=(150, 40), enabled=True) -> QPushButton:
        '''
        创建一个 QPushButton（按钮），可设置文本、大小和启用状态。
        :param text: 按钮上的文本
        :param size: 按钮大小（宽, 高）
        :param enabled: 按钮是否可用
        :return: 返回 QPushButton 对象
    
        Creates a QPushButton with the given text, size, and enabled state.
        :param text: The text displayed on the button.
        :param size: A tuple (width, height) specifying the button size.
        :param enabled: A boolean indicating whether the button is enabled.
        :return: A QPushButton object.
        '''
        button = QPushButton(text)
        button.setFixedSize(*size)
        button.setEnabled(enabled)
        return button

    def create_text_edit(self, size=(100, 40), enabled=True, read_only=False) -> QTextEdit:
        '''
        创建一个 QTextEdit（文本框），可设置大小、启用状态和只读模式。
        :param size: 文本框大小（宽, 高）
        :param enabled: 文本框是否可用
        :param read_only: 是否只读
        :return: 返回 QTextEdit 对象

        Creates a QTextEdit widget with specified size, enabled state, and read-only mode.
        :param size: A tuple (width, height) specifying the text box size.
        :param enabled: A boolean indicating whether the text box is enabled.
        :param read_only: A boolean indicating whether the text box is read-only.
        :return: A QTextEdit object.
        '''
        text_edit = QTextEdit()
        text_edit.setFixedSize(*size)
        text_edit.setEnabled(enabled)
        text_edit.setReadOnly(read_only)
        return text_edit

    def create_combo_box(self, items=None, size=(200, 40), enabled=True) -> QComboBox:
        '''
        创建一个 QComboBox（下拉框），可设置选项、大小和启用状态。
        :param items: 下拉框的选项列表
        :param size: 下拉框大小（宽, 高）
        :param enabled: 是否可用
        :return: 返回 QComboBox 对象

        Creates a QComboBox (drop-down menu) with given items, size, and enabled state.
        :param items: A list of strings representing the options in the combo box.
        :param size: A tuple (width, height) specifying the combo box size.
        :param enabled: A boolean indicating whether the combo box is enabled.
        :return: A QComboBox object.
        '''
        combo_box = QComboBox()
        combo_box.setFixedSize(*size)
        if items:
            combo_box.addItems(items)
        combo_box.setEnabled(enabled)
        return combo_box

    def create_slider(self, min_value=0, max_value=100, value=0, orientation='horizontal', enabled=True, size=(300,0)) -> QSlider:
        '''
        创建一个 QSlider（滑动条），可设置最小值、最大值、初始值、方向、启用状态和大小。
        :param min_value: 滑动条最小值
        :param max_value: 滑动条最大值
        :param value: 初始值
        :param orientation: 'horizontal'（水平）或 'vertical'（垂直）
        :param enabled: 是否可用
        :param size: 滑动条的大小，传入一个元组 (width, height)，只会设置宽度或高度，具体取决于方向
        :return: 返回 QSlider 对象

        Creates a QSlider with given range, initial value, orientation, enabled state, and size.
        :param min_value: The minimum value of the slider.
        :param max_value: The maximum value of the slider.
        :param value: The initial value of the slider.
        :param orientation: 'horizontal' or 'vertical' to set the slider's direction.
        :param enabled: A boolean indicating whether the slider is enabled.
        :param size: A tuple (width, height) to set the size of the slider.
        :return: A QSlider object.
        '''
        slider = QSlider()
        if orientation == 'horizontal':
            slider.setOrientation(Qt.Horizontal)
        else:
            slider.setOrientation(Qt.Vertical)
        
        slider.setRange(min_value, max_value)
        slider.setValue(value)
        slider.setEnabled(enabled)
        
        if size:
            if orientation == 'horizontal':
                slider.setFixedWidth(size[0])  # 设置宽度
            else:
                slider.setFixedHeight(size[1])  # 设置高度
        
        return slider


    def create_label(self, text: str, size=(100, 40)) -> QLabel:
        '''
        创建一个 QLabel（标签），可设置文本和大小。
        :param text: 标签上的文本
        :param size: 标签大小（宽, 高）
        :return: 返回 QLabel 对象

        Creates a QLabel with specified text and size.
        :param text: The text displayed in the label.
        :param size: A tuple (width, height) specifying the label size.
        :return: A QLabel object.
        '''
        label = QLabel(text)
        label.setFixedSize(*size)
        return label

    def create_frame(self, frame_shape=QFrame.Box, line_width=1) -> QFrame:
        '''
        创建一个 QFrame（框架），可设置形状和线条宽度。
        :param frame_shape: 框架形状（默认 QFrame.Box）
        :param line_width: 框架边框宽度
        :return: 返回 QFrame 对象

        Creates a QFrame with a specified shape and line width.
        :param frame_shape: The shape of the frame (default is QFrame.Box).
        :param line_width: The width of the frame's border.
        :return: A QFrame object.
        '''
        frame = QFrame()
        frame.setFrameShape(frame_shape)
        frame.setLineWidth(line_width)
        return frame
    def add_layout_to_frame(self, frame: QFrame, widgets: list) -> None:
        '''
        将一系列小部件添加到指定的 QFrame 中，并根据需要自动处理多行或多列的布局。
        :param frame: 目标 QFrame 对象
        :param widgets: 要添加的小部件列表，每个元素为 (widget, row, col, row_span, col_span)
        '''
        layout = QGridLayout()  # 使用网格布局
        
        for widget_data in widgets:
            if len(widget_data) == 3:  # 标准小部件：widget, row, col
                widget, row, col = widget_data
                layout.addWidget(widget, row, col)
            elif len(widget_data) == 5:  # 处理跨行和跨列的小部件：widget, row, col, row_span, col_span
                widget, row, col, row_span, col_span = widget_data
                layout.addWidget(widget, row, col, row_span, col_span)
            else:
                raise ValueError("Invalid widget data format, expected 3 or 5 elements.")

        frame.setLayout(layout)

