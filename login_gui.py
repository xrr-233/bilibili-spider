import asyncio
import json
import uuid
import httpx
import requests
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, Slot, QObject, Signal, QTimer
from PySide6.QtGui import QPixmap
from bilibili_api import login, LoginError, Picture, Credential
from bilibili_api.utils.utils import get_api

from widgetgallery import WidgetGallery


class LoginWidget(QWidget):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.setWindowTitle("凭证登录")

        self.menu_widget = QTabWidget()
        self.init_tab1()
        self.init_tab2()
        self.init_tab3()
        self.tabs = []
        self.tabs.append(self.tab1)
        self.tabs.append(self.tab2)
        self.tabs.append(self.tab3)
        self.current_tab = 0
        self.hide_widgets(1)
        self.hide_widgets(2)
        self.menu_widget.tabBarClicked.connect(self.change_tab)

        layout = QHBoxLayout()
        layout.addWidget(self.menu_widget)
        # layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)
        self.setFixedWidth(self.sizeHint().width())
        self.show()

        adjust_timer = QTimer(self)
        adjust_timer.timeout.connect(self.adjustSize)
        adjust_timer.start(10)

        self.qr_code_status_timer = None
        self.credential = None

    def init_tab1(self):
        self.tab1 = QWidget()
        tab1_layout = QGridLayout()
        tab1_phone_email_input = QLineEdit()
        tab1_phone_email_input.setObjectName('tab1_phone_email_input')
        tab1_phone_email_label = QLabel("手机号/邮箱：")
        tab1_phone_email_label.setBuddy(tab1_phone_email_input)
        tab1_layout.addWidget(tab1_phone_email_label, 0, 0)
        tab1_layout.addWidget(tab1_phone_email_input, 0, 1)
        tab1_password_input = QLineEdit()
        tab1_password_input.setObjectName('tab1_password_input')
        tab1_password_input.setClearButtonEnabled(True)
        tab1_password_input.setEchoMode(QLineEdit.Password)
        tab1_password_label = QLabel("密码：")
        tab1_password_label.setBuddy(tab1_password_input)
        tab1_layout.addWidget(tab1_password_label, 1, 0)
        tab1_layout.addWidget(tab1_password_input, 1, 1)
        tab1_hint = QLabel()
        tab1_hint.setObjectName('tab1_hint')
        tab1_layout.addWidget(tab1_hint, 2, 0, 1, 2)
        tab1_hint.hide()
        tab1_login_button = QPushButton("登录")
        tab1_login_button.setShortcut(Qt.Key_Return)
        tab1_login_button.clicked.connect(self.login_with_password)
        tab1_layout.addWidget(tab1_login_button, 3, 0, 1, 2)
        self.tab1.setLayout(tab1_layout)
        self.menu_widget.addTab(self.tab1, "密码登录")

    def init_tab2(self):
        self.tab2 = QWidget()
        tab2_layout = QGridLayout()
        tab2_phone_input = QLineEdit()
        tab2_phone_input.setObjectName('tab2_phone_input')
        tab2_phone_label = QLabel("手机号：")
        tab2_phone_label.setBuddy(tab2_phone_input)
        tab2_layout.addWidget(tab2_phone_label, 0, 0)
        tab2_layout.addWidget(tab2_phone_input, 0, 1)
        tab2_send_sms_button = QPushButton("发送验证码")
        tab2_send_sms_button.clicked.connect(self.get_sms_code)
        tab2_layout.addWidget(tab2_send_sms_button, 0, 2)
        tab2_auth_code_input = QLineEdit()
        tab2_auth_code_input.setObjectName('tab2_auth_code_input')
        tab2_auth_code_label = QLabel("验证码：")
        tab2_auth_code_label.setBuddy(tab2_auth_code_input)
        tab2_layout.addWidget(tab2_auth_code_label, 1, 0)
        tab2_layout.addWidget(tab2_auth_code_input, 1, 1, 1, 2)
        tab2_hint = QLabel()
        tab2_hint.setObjectName('tab2_hint')
        tab2_layout.addWidget(tab2_hint, 2, 0, 1, 3)
        tab2_hint.hide()
        tab2_login_button = QPushButton("登录")
        tab2_login_button.clicked.connect(self.login_with_sms)
        tab2_layout.addWidget(tab2_login_button, 3, 0, 1, 3)
        self.tab2.setLayout(tab2_layout)
        self.menu_widget.addTab(self.tab2, "验证码登录")

    def init_tab3(self):
        self.tab3 = QWidget()
        tab3_layout = QVBoxLayout()
        tab3_qr_code_label = QLabel()
        tab3_qr_code_label.setObjectName('tab3_qr_code_label')
        self.qr_code_pixmap = QPixmap()
        self.tab3.setLayout(tab3_layout)
        tab3_qr_code_scaled = self.qr_code_pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        tab3_qr_code_label.setScaledContents(True)
        tab3_qr_code_label.setPixmap(tab3_qr_code_scaled)
        tab3_layout.addWidget(tab3_qr_code_label)
        tab3_hint = QLabel()
        tab3_hint.setObjectName('tab3_hint')
        tab3_layout.addWidget(tab3_hint)
        tab3_hint.hide()
        self.menu_widget.addTab(self.tab3, "二维码登录")

    @Slot(int)
    def change_tab(self, index):
        if not index == self.current_tab:
            if index == 2:
                if self.qr_code_status_timer is None:
                    qr_code_refresh_timer = QTimer(self.tab3)
                    qr_code_refresh_timer.timeout.connect(self.update_qr_code)
                    qr_code_refresh_timer.start(120000)
                    self.qr_code_status_timer = QTimer(self.tab3)
                    self.qr_code_status_timer.timeout.connect(self.login_with_qr_code)
                    self.qr_code_status_timer.start(500)
                    self.update_qr_code()
            self.hide_widgets(self.current_tab)
            self.current_tab = index
            self.show_widgets(self.current_tab)

    def show_widgets(self, index):
        for widget in self.tabs[index].findChildren(QObject):
            if isinstance(widget, QWidget) and 'hint' not in widget.objectName():
                widget.show()

    def hide_widgets(self, index):
        for widget in self.tabs[index].findChildren(QObject):
            if isinstance(widget, QWidget):
                widget.hide()

    def login_with_password(self):
        """
        目前使用bilibili-api的密码登录会显示"本次登录环境存在风险, 需使用手机号进行验证或绑定"
        :return:
        """
        widget = self.tab1
        phone_email = widget.findChild(QLineEdit, 'tab1_phone_email_input').text()
        password = widget.findChild(QLineEdit, 'tab1_password_input').text()
        hint: QLabel = widget.findChild(QLabel, 'tab1_hint')
        try:
            self.credential = login.login_with_password(phone_email, password)
        except LoginError:
            hint.setText('<font color=red>用户名或密码错误</font>')
            hint.show()
            return
        except Exception as e:
            print(e)
        if isinstance(self.credential, login.Check):
            hint.setText('<font color=red>需要进行验证，请考虑使用二维码登录</font>')
            hint.show()
        else:
            hint.setText('<font color=green>登录成功</font>')
            hint.show()
            self.setDisabled(True)

            destroy_timer = QTimer(self)
            destroy_timer.timeout.connect(self.app.exit)
            destroy_timer.start(1000)

    def get_sms_code(self):
        widget = self.tab2
        phone = widget.findChild(QLineEdit, 'tab2_phone_input').text()
        login.send_sms(login.PhoneNumber(phone, country="+86"))  # 默认设置地区为中国大陆

    def login_with_sms(self):
        """
        目前bilibili-api的sms功能正在修复中，待填坑（懒得整了，直接扫码吧）
        :return:
        """
        widget = self.tab2
        phone = widget.findChild(QLineEdit, 'tab2_phone_input').text()
        auth_code = widget.findChild(QLineEdit, 'tab2_auth_code_input').text()
        hint: QLabel = widget.findChild(QLabel, 'tab2_hint')
        try:
            self.credential = login.login_with_sms(login.PhoneNumber(phone, country="+86"), auth_code)
        except LoginError:
            hint.setText('<font color=red>验证码错误</font>')
            hint.show()
            return
        if isinstance(self.credential, login.Check):
            hint.setText('<font color=red>需要进行验证，请考虑使用二维码登录</font>')
            hint.show()
        else:
            hint.setText('<font color=green>登录成功</font>')
            hint.show()
            self.setDisabled(True)

            destroy_timer = QTimer(self)
            destroy_timer.timeout.connect(self.app.exit)
            destroy_timer.start(1000)

    def update_qr_code(self):
        api = get_api("login")["qrcode"]["get_qrcode_and_token"]
        qr_code_login_data = json.loads(httpx.get(api["url"]).text)["data"]
        self.login_key = qr_code_login_data["qrcode_key"]
        self.qr_code_image = Picture.from_file(login.make_qrcode(qr_code_login_data["url"]))
        self.qr_code_pixmap.loadFromData(self.qr_code_image.content, self.qr_code_image.imageType)
        qr_code_scaled = self.qr_code_pixmap.scaled(200, 200, Qt.KeepAspectRatio)
        qr_code_label: QLabel = self.tab3.findChild(QLabel, 'tab3_qr_code_label')
        qr_code_label.setPixmap(qr_code_scaled)

    def login_with_qr_code(self):
        widget = self.tab3
        hint: QLabel = widget.findChild(QLabel, 'tab3_hint')

        events_api = get_api("login")["qrcode"]["get_events"]
        events = json.loads(
            requests.get(
                events_api["url"],
                params={"qrcode_key": self.login_key},
                cookies={"buvid3": str(uuid.uuid1()), "Domain": ".bilibili.com"},
            ).text
        )
        # {'url': 'https://passport.biligame.com/x/passport-login/web/crossDomain?DedeUserID=x&DedeUserID__ckMd5=x&Expires=x&SESSDATA=x&bili_jct=x&gourl=x', 'refresh_token': 'x', 'timestamp': 1683903305723, 'code': 0, 'message': ''}
        if "code" in events.keys() and events["code"] == -412:
            hint.setText('<font color=red>登录失败，请重试</font>')
            hint.show()
        elif events["data"]["code"] == 0:
            hint.setText('<font color=green>登录成功</font>')
            hint.show()
            self.setDisabled(True)

            url: str = events["data"]["url"]
            cookies_list = url.split("?")[1].split("&")
            sessdata = ""
            bili_jct = ""
            dede = ""
            for cookie in cookies_list:
                if cookie[:8] == "SESSDATA":
                    sessdata = cookie[9:]
                if cookie[:8] == "bili_jct":
                    bili_jct = cookie[9:]
                if cookie[:11].upper() == "DEDEUSERID=":
                    dede = cookie[11:]
            self.credential = Credential(sessdata, bili_jct, dedeuserid=dede)

            destroy_timer = QTimer(self)
            destroy_timer.timeout.connect(self.app.exit)
            destroy_timer.start(1000)


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


async def login_gui():
    app = QApplication()
    # gallery = WidgetGallery()
    # gallery.show()
    login_widget = LoginWidget(app)
    app.exec()

    credential: Credential = login_widget.credential
    try:
        valid = await credential.check_valid()
    except:
        exit(-1)
    if not valid:
        print('Cookie无效！')
        exit(-1)
    return credential


if __name__ == '__main__':
    # asyncio.get_event_loop().run_until_complete(main())
    login_gui()
