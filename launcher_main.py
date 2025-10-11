import os
from pathlib import Path

import sys

from PySide6 import QtWidgets
from PySide6.QtGui import Qt
from record_util import start, stop, toggle_pause

# 录屏工具
class MyWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("量子录屏")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint )

        self.setup_ui()

    def start_record(self):
        print('开始录屏')
        try:
            start()
        except ValueError as e:
            print(f"捕捉到异常{e}")
            self.record_env = QtWidgets.QLabel(str(e), self)
            self.record_env.setStyleSheet("color: red;")

    def pause_record(self):

        if '开始' in self.pause_btn.text():
            self.record_status.setText('录屏中...')
            self.record_status.setStyleSheet("color: red;")
            self.pause_btn.setText('暂停')
            print('开始录屏')
            start()
        elif '暂停' in self.pause_btn.text():
            self.record_status.setText('已暂停')
            self.record_status.setStyleSheet("color: red;")
            self.pause_btn.setText('继续')
            toggle_pause()
        else:
            # self.showMinimized()
            self.record_status.setText('录屏中...')
            self.record_status.setStyleSheet("color: red;")
            self.pause_btn.setText('暂停')
            toggle_pause()

    def stop_record(self):
        print('停止录制')
        self.record_status.setText('文件已保存')
        self.record_status.setStyleSheet("color: green;")
        self.pause_btn.setText('开始')
        stop()

    def open_dir(self):
        os.startfile(os.path.join('records'))
    def setup_ui(self) -> None:
        """设置界面"""
        # self.resize(300, 80)
        self.setFixedSize(220, 96)
        self.record_status = QtWidgets.QLabel("", self)

        self.pause_btn = QtWidgets.QPushButton("开始", self)
        self.pause_btn.clicked.connect(self.pause_record)

        stop_btn = QtWidgets.QPushButton("停止", self)
        stop_btn.clicked.connect(self.stop_record)

        open_btn = QtWidgets.QPushButton("打开文件", self)
        open_btn.clicked.connect(self.open_dir)

        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
        layout0 = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        layout1 = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        layout2 = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)

        layout0.addWidget(self.record_status)
        layout1.addWidget(open_btn)
        layout2.addWidget(self.pause_btn)
        layout2.addWidget(stop_btn)

        layout.addLayout(layout0)
        layout.addLayout(layout1)
        layout.addLayout(layout2)


        self.setLayout(layout)

    def closeEvent(self, event):
        stop()
        event.accept()


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容开发环境和打包环境"""
    try:
        # 打包后的环境
        if getattr(sys, 'frozen', False):
            base_dir = Path(sys.executable).parent
        else:
            # 开发环境：假设这个代码文件在项目根目录或子目录中
            base_dir = Path(__file__).parent

        # 构建完整路径
        full_path = base_dir / relative_path
        return full_path

    except Exception as e:
        print(f"获取资源路径错误: {e}")
        return Path(relative_path)  # 返回相对路径作为后备

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())
