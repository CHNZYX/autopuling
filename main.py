import win32gui, win32com.client, pythoncom
import sys
import keyboard
import time, random
from pynput.keyboard import Controller
import win32con
import win32api
import json

def send_key_to_window(hwnd, key=0x46):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(random.random()*0.2+0.2)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)    

def set_forground(game_nd):
    try:
        pythoncom.CoInitialize()
        shell = win32com.client.Dispatch("WScript.Shell")
        if getattr(sys, 'frozen', False):
            shell.SendKeys(" ")
        else:
            shell.SendKeys("")
        win32gui.SetForegroundWindow(game_nd)
    except:
        pass

def enum_windows_callback(hwnd, hwnds):
    try:
        class_name = win32gui.GetClassName(hwnd)
        window_name = win32gui.GetWindowText(hwnd)
        if (window_name == 'InfinityNikki' or window_name == '无限暖暖') and class_name == 'UnrealWindow':
            hwnds.append(hwnd)
    except:
        pass
    return True

def init_window():
    hwnds = []
    win32gui.EnumWindows(lambda a,b:enum_windows_callback(a,b), hwnds)
    if len(hwnds) == 0:
        print('未找到游戏窗口')
        time.sleep(5)
        return None
    game_nd = hwnds[0]
    send_key_to_window(game_nd, win32con.VK_SPACE)
    if foreground:
        set_forground(game_nd)
    return game_nd

def press_key_pynput(key):
    global stop, game_nd
    cnt = 0
    while win32gui.GetForegroundWindow() != game_nd:
        time.sleep(1)
        if stop:
            return
        cnt += 1
        if cnt > 600:
            print("尝试将游戏窗口置于前台...")
            game_nd = init_window()
            if game_nd is None:
                print("未找到游戏窗口，停止运行")
                stop = 1
                return
            time.sleep(1)
            break
    keyboard = Controller()
    keyboard.press(key)
    time.sleep(random.random()*0.2+0.2)
    keyboard.release(key)

stop = False
def on_key_press(event):
    if event.name == "f8":
        global stop
        print("F8 已被按下，尝试停止运行")
        stop = True
        
def press():
    if foreground:
        press_key_pynput('f')
    else:
        send_key_to_window(game_nd)

def load_info():
    try:
        with open('info.txt', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_info(info):
    with open('info.txt', 'w') as f:
        json.dump(info, f)

def ask_user_choice():
    print("请选择运行模式：0为前台模式，1为后台模式(测试功能，请保证游戏窗口状态为被覆盖而不是最小化)")
    while True:
        try:
            foreground = int(input("输入您的选择："))
            if foreground in [0, 1]:
                break
        except ValueError:
            pass
        print("无效输入，请输入0或1。")

    print("是否记住您的选择？0为否，1为记住选择，2为否且不再询问")
    while True:
        try:
            remember = int(input("输入您的选择："))
            if remember in [0, 1, 2]:
                break
        except ValueError:
            pass
        print("无效输入，请输入0、1或2。")

        # 获取用户输入的循环次数
    while True:
        try:
            loop_count = int(input("请输入循环次数："))
            if loop_count > 0:
                break
        except ValueError:
            print("无效输入，请输入一个正整数。")

    return foreground, remember,loop_count

info = load_info()
foreground = info.get("foreground")
remember_choice = info.get("remember_choice", 0)
loop_count = info.get("loop_count", 130)
if remember_choice == 0 or remember_choice == 2:
    foreground, remember_choice,loop_count = ask_user_choice()

    # 更新并保存选择
    info["foreground"] = foreground
    info["remember_choice"] = remember_choice
    info["loop_count"] = loop_count
    save_info(info)

if remember_choice == 2:
    print("已选择不再询问，请注意需手动删除info.txt以重新设置。")

keyboard.on_press(on_key_press)
game_nd = init_window()
if game_nd is not None:
    print("游戏窗口已找到，开始运行")

    for _ in range(loop_count):
        if stop:
            print("运行已停止")
            break
        press()
        time.sleep(random.random() * 1 + 2)
    
    if not stop:
        print(f"已完成 {loop_count} 次循环。")

    time.sleep(1)
