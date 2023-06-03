import sys
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Slot, QObject, Signal, QRect, QSize
from PySide6.QtGui import QPixmap
from bilibili_api import login_func

from widgetgallery import WidgetGallery


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("嘴臭孙笑川")

        self.hello = ["你吼那么大声干什么", "那我凭什么关窗嘛", "那你去物管啊", "你再骂", "我操你妈"]

        self.button = QPushButton("SB，有本事你就来点点看")
        self.text = QLabel("<font color=red size=40>Hello World!</font>",
                                     alignment=Qt.AlignCenter)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @Slot()
    def magic(self):
        self.text.setText(f"<font color=red size=40>{random.choice(self.hello)}</font>")


class LoginWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("凭证登录")

        menu_widget = QTabWidget()

        item1 = QWidget()
        item1_layout = QGridLayout(item1)
        item1_phone_email_input = QLineEdit()
        item1_phone_email_label = QLabel("手机号/邮箱：")
        item1_phone_email_label.setBuddy(item1_phone_email_input)
        item1_layout.addWidget(item1_phone_email_label, 0, 0)
        item1_layout.addWidget(item1_phone_email_input, 0, 1)
        item1_password_input = QLineEdit()
        item1_password_input.setClearButtonEnabled(True)
        item1_password_input.setEchoMode(QLineEdit.Password)
        item1_password_label = QLabel("密码：")
        item1_password_label.setBuddy(item1_password_input)
        item1_layout.addWidget(item1_password_label, 1, 0)
        item1_layout.addWidget(item1_password_input, 1, 1)
        item1_login_button = QPushButton("登录")
        item1_layout.addWidget(item1_login_button, 2, 0, 1, 2)
        item1_widgets = []
        item1_widgets.append(item1_phone_email_label)
        item1_widgets.append(item1_phone_email_input)
        item1_widgets.append(item1_password_label)
        item1_widgets.append(item1_password_input)
        item1_widgets.append(item1_login_button)
        menu_widget.addTab(item1, "密码登录")

        item2 = QWidget()
        item2_layout = QGridLayout(item2)
        item2_phone_input = QLineEdit()
        item2_phone_label = QLabel("手机号：")
        item2_phone_label.setBuddy(item2_phone_input)
        item2_layout.addWidget(item2_phone_label, 0, 0)
        item2_layout.addWidget(item2_phone_input, 0, 1)
        item2_send_sms_button = QPushButton("发送验证码")
        item2_layout.addWidget(item2_send_sms_button, 0, 2)
        item2_auth_code_input = QLineEdit()
        item2_auth_code_label = QLabel("验证码：")
        item2_auth_code_label.setBuddy(item2_auth_code_input)
        item2_layout.addWidget(item2_auth_code_label, 1, 0)
        item2_layout.addWidget(item2_auth_code_input, 1, 1, 1, 2)
        item2_login_button = QPushButton("登录")
        item2_layout.addWidget(item2_login_button, 2, 0, 1, 3)
        item2_widgets = []
        item2_widgets.append(item2_phone_label)
        item2_widgets.append(item2_phone_input)
        item2_widgets.append(item2_send_sms_button)
        item2_widgets.append(item2_auth_code_label)
        item2_widgets.append(item2_auth_code_input)
        item2_widgets.append(item2_login_button)
        menu_widget.addTab(item2, "验证码登录")

        item3 = QWidget()
        item3_layout = QVBoxLayout(item3)
        item3_qr_code_label = QLabel()
        qrcode_data = login_func.get_qrcode()
        item3_qr_code = QPixmap()
        item3_qr_code.loadFromData(qrcode_data[0].content, qrcode_data[0].imageType)
        item3_qr_code_scaled = item3_qr_code.scaled(item3_qr_code.size() / 2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        print(qrcode_data[1])

        item3_qr_code_label.setScaledContents(True)
        item3_qr_code_label.setPixmap(item3_qr_code_scaled)
        # self.qrcode_sec = qrcode_data[1]
        item3_layout.addWidget(item3_qr_code_label)
        item3_widgets = []
        item3_widgets.append(item3_qr_code_label)
        menu_widget.addTab(item3, "二维码登录")

        menu_widget.tabBarClicked.connect(self.change_tab)

        self.tabs = []
        self.tabs.append(item1_widgets)
        self.tabs.append(item2_widgets)
        self.tabs.append(item3_widgets)

        self.current_tab = 0
        self.hide_widgets(1)
        self.hide_widgets(2)

        layout = QHBoxLayout()
        layout.addWidget(menu_widget)
        self.setLayout(layout)

    @Slot(int)
    def change_tab(self, index):
        if not index == self.current_tab:
            self.hide_widgets(self.current_tab)
            self.current_tab = index
            self.show_widgets(self.current_tab)

    def show_widgets(self, index):
        for widget in self.tabs[index]:
            widget.show()

    def hide_widgets(self, index):
        for widget in self.tabs[index]:
            widget.hide()

class Communicate(QObject):
    # create two new signals on the fly: one will handle
    # int type, the other will handle strings
    speak = Signal((int,), (str,))

    def __init__(self, parent=None):
        super().__init__(parent)

        self.speak[int].connect(self.say_something)
        self.speak[str].connect(self.say_something)

    # define a new slot that receives a C 'int' or a 'str'
    # and has 'say_something' as its name
    @Slot(int)
    @Slot(str)
    def say_something(self, arg):
        if isinstance(arg, int):
            print("This is a number:", arg)
        elif isinstance(arg, str):
            print("This is a string:", arg)


if __name__ == '__main__':
    # app = QApplication([])
    # widget = MyWidget()
    # widget.resize(800, 600)
    # widget.show()
    # sys.exit(app.exec())

    # app = QApplication([])
    # someone = Communicate()
    # # emit 'speak' signal with different arguments.
    # # we have to specify the str as int is the default
    # someone.speak.emit(10)
    # someone.speak[str].emit("Hello everybody!")

    app = QApplication()
    # gallery = WidgetGallery()
    # gallery.show()
    login_widget = LoginWidget()
    login_widget.show()
    sys.exit(app.exec())
