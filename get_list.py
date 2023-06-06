import asyncio
import msvcrt
from bilibili_api import Credential
from bilibili_api.user import get_self_info
from bilibili_api import login, settings
from bilibili_api import sync


def pwd_input():
    chars = []
    while True:
        try:
            new_char = msvcrt.getch().decode(encoding="utf-8")
        except:
            return input("你很可能不是在cmd命令行下运行，密码输入将不能隐藏:")
        if new_char in '\r\n':  # 如果是换行，则输入结束
            print()
            break
        elif new_char == '\b':  # 如果是退格，则删除密码末尾一位并且删除一个星号
            if chars:
                del chars[-1]
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格
                msvcrt.putch(' '.encode(encoding='utf-8'))  # 输出一个空格覆盖原来的星号
                msvcrt.putch('\b'.encode(encoding='utf-8'))  # 光标回退一格准备接受新的输入
        else:
            chars.append(new_char)
            msvcrt.putch('*'.encode(encoding='utf-8'))  # 显示为星号
    return ''.join(chars)
# https://www.cnblogs.com/botoo/p/7272824.html


mode = 0
mode_invalid_flag = False
try:
    mode = int(input("请选择登录方式：\n"
                     "1. 密码登录\n"
                     "2. 验证码登录\n"
                     "3. 二维码登录\n"
                     "请输入 1/2/3\n"
                     "退出程序请按Ctrl+C\n"))
    if mode < 1 or mode > 3:
        mode_invalid_flag = True
except KeyboardInterrupt:
    exit()
except:
    mode_invalid_flag = True

while mode_invalid_flag:
    mode_invalid_flag = False
    try:
        mode = int(input("非法输入！请输入 1/2/3 ！"))
        if mode < 1 or mode > 3:
            mode_invalid_flag = True
    except KeyboardInterrupt:
        exit()
    except:
        mode_invalid_flag = True

credential = None

# 关闭自动打开 geetest 验证窗口
settings.geetest_auto_open = False

if mode == 3:
    # 二维码登录
    print("请登录：")
    credential = login.login_with_qrcode()
    try:
        credential.raise_for_no_bili_jct()  # 判断是否成功
        credential.raise_for_no_sessdata()  # 判断是否成功
    except:
        print("登录失败...")
        exit(1)
    print("登录成功")

print(credential.get_cookies())
if credential != None:
    name = sync(get_self_info(credential))['name']
    print(f"欢迎，{name}!")

# async def main() -> None:
#     # 初始化相簿类
#     al = album.Album(123348276)
#     # 获取图片
#     pictures = await al.get_pictures()
#     # 下载所有图片
#     cnt = 0
#     for pic in pictures:
#         await pic.download(f"{cnt}.png")
#         cnt += 1
