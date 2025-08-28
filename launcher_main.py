import os

from PIL.ImageFont import load_path
from PySide6 import QtWidgets
import sys

from PySide6.QtGui import Qt
from config import load_config
from config import save_config
from record_util import start, stop, toggle_pause


class MyWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("量子录屏")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint )

        self.dialog = QtWidgets.QFileDialog(self)
        self.setup_dialog()
        self.setup_ui()

    def start_record(self):
        # self.showMinimized()
        if not load_config():
            self.record_env.setText("您还未配置FFmpeg路径")
            self.record_env.setStyleSheet("color: red;")
            self.message_box.open()
            return
        print('开始录屏')
        try:
            start()
        except ValueError as e:
            print(f"捕捉到异常{e}")
            self.record_env = QtWidgets.QLabel(str(e), self)
            self.record_env.setStyleSheet("color: red;")

    def pause_record(self):
        if not load_config():
            self.record_env.setText("您还未配置FFmpeg路径")
            self.record_env.setStyleSheet("color: red;")
            self.message_box.open()
            return
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

    def setup_dialog(self) -> None:
        """配置对话框属性功能"""
        self.dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptOpen)  # 打开模式
        self.dialog.setNameFilter("可执行文件(*.exe)")
        self.dialog.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFiles)  # 选择现有文件
        self.dialog.setLabelText(
            QtWidgets.QFileDialog.DialogLabel.Accept, "选择"
        )  # 为「接受」按键指定文本
        self.dialog.setLabelText(
            QtWidgets.QFileDialog.DialogLabel.Reject, "取消"
        )  # 为「拒绝」按键指定文本

    def open_dir(self):
        os.startfile(os.path.join('records'))
    def setup_ui(self) -> None:
        """设置界面"""
        self.resize(300, 80)

        self.message_box = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Icon.Warning,
            "温馨提示",
            "请先下载FFmpeg并配置，注意配置到.../bin/ffmpeg.exe",
            QtWidgets.QMessageBox.StandardButton.Ok,
            self,
        )

        self.record_env = QtWidgets.QLabel("环境正常" if load_config() else "您还未配置FFmpeg路径", self)
        self.record_env.setStyleSheet("color: green;" if load_config() else "color: red;")

        self.record_status = QtWidgets.QLabel("", self)

        browse_btn = QtWidgets.QPushButton("选择文件", self)
        browse_btn.clicked.connect(self.dialog.open)  # type: ignore

        self.dialog.fileSelected.connect(lambda path: [save_config(path), self.record_env.setText("环境正常"), self.record_env.setStyleSheet("color: green;")])  # type: ignore

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

        layout0.addWidget(self.record_env)
        layout0.addWidget(self.record_status)
        layout1.addWidget(browse_btn)
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

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())
