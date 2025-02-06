import win32gui, win32com.client, pythoncom
import sys
import keyboard
import time, random
from pynput.keyboard import Controller
import win32con
import win32api
import json

# 关闭游戏窗口
def close_window(hwnd):
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        print("游戏窗口已关闭")
    except Exception as e:
        print(f"关闭窗口失败: {e}")

# 检测窗口是否最小化
def is_window_minimized(hwnd):
    placement = win32gui.GetWindowPlacement(hwnd)
    return placement[1] == win32con.SW_SHOWMINIMIZED

# 后台模式按键输入
def send_key_to_window(key='f', tm=0.2, keyup=True):
    global game_nd
    hwnd = game_nd

    # 取消最小化
    if is_window_minimized(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

    key = 0x41 + ord(key) - ord('a')
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(random.random() * 0.2 + tm)
    if keyup:
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)    

# 枚举所有窗口
def enum_windows_callback(hwnd, hwnds):
    try:
        class_name = win32gui.GetClassName(hwnd).strip()
        window_name = win32gui.GetWindowText(hwnd).strip()
        if (window_name == 'Infinity Nikki' or window_name == 'InfinityNikki' or window_name == '无限暖暖') and class_name == 'UnrealWindow':
            hwnds.append(hwnd)
    except:
        pass
    return True

# 强制游戏窗口处于前台
def set_forground(hwnds):
    """将窗口设置为前台"""
    try:
        pythoncom.CoInitialize()

        # 检查并恢复窗口状态
        if is_window_minimized(hwnds):
            win32gui.ShowWindow(hwnds, win32con.SW_RESTORE)

        # 直接设置为前台
        win32gui.SetForegroundWindow(hwnds)
    except:
        pass

# 检测游戏窗口
def init_window():
    hwnds = []
    win32gui.EnumWindows(lambda a,b:enum_windows_callback(a,b), hwnds)

    if len(hwnds) == 0:
        print('未找到游戏窗口。')
        time.sleep(5)
        return None
    
    game_nd = hwnds[0]
    
    if foreground:
        set_forground(game_nd)

    return game_nd

# 前台模式按键输入
def press_key_pynput(key, tm, keyup):
    global stop, game_nd

    while win32gui.GetForegroundWindow() != game_nd:
        time.sleep(1)
        if stop:
            return

        print("尝试将游戏窗口置于前台...")
        game_nd = init_window()
        if game_nd is None:
            print("未找到游戏窗口，停止运行。")
            stop = 1
            return
        time.sleep(1)
        break

    keyboard = Controller()
    keyboard.press(key)
    time.sleep(random.random() * 0.2 + tm)

    if keyup:
        keyboard.release(key)

# 检测手动暂停
def on_key_press(event):
    if event.name == "f8":
        global stop
        print("F8 已被按下，尝试停止运行")
        stop = True

# 模拟按键输入
def press(key, tm, keyup = True):
    if foreground:
        press_key_pynput(key, tm, keyup)
    else:
        send_key_to_window(key, tm, keyup)

# 读取用户选择数据
def load_info():
    try:
        with open('info.txt', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# 保存用户选择数据
def save_info(info):
    with open('info.txt', 'w') as f:
        json.dump(info, f)

# 询问用户选择
def ask_user_choice():
    global foreground, closure, duration, remember_fg, remember_cls, remember_dur

    # 运行模式选择
    if remember_fg != 1: # 0 or 2
        while True:
            try:
                print("请选择运行模式：0 为后台模式，1 为前台模式。")
                foreground = int(input("输入您的选择："))
                if foreground in [0, 1]:
                    break
            except ValueError:
                pass
            print("无效输入，请输入 0 或 1。")

        if remember_fg == 0:
            while True:
                try:
                    print("是否记住运行模式选择？ 0 为否，1 为记住选择，2 为否且不再询问。")
                    remember_fg = int(input("输入您的选择："))
                    if remember_fg in [0, 1, 2]:
                        break
                except ValueError:
                    pass
                print("无效输入，请输入0、1 或 2。")
        else:
            print("运行模式已不再询问，请删除 info.txt 进行重新设置。")

    # 关闭选择
    if remember_cls != 1: # 0 or 2
        while True:
            try:
                print("\n请选择结束时是否自动关闭游戏：0 为否，1 为是。")
                closure = int(input("输入您的选择："))
                if closure in [0, 1]:
                    break
            except ValueError:
                pass
            print("无效输入，请输入 0 或 1。")

        if remember_cls == 0:
            while True:
                try:
                    print("是否记住自动关闭选择？0 为否，1 为记住选择，2 为否且不再询问。")
                    remember_cls = int(input("输入您的选择："))
                    if remember_cls in [0, 1, 2]:
                        break
                except ValueError:
                    pass
                print("无效输入，请输入 0、1 或 2。")
        else:
            print("关闭选择已不再询问，请删除 info.txt 进行重新设置。")

    # 运行时间选择
    if remember_dur != 1: # 0 or 2
        while True:
            try:
                print("\n请选择运行时间（分钟）：")
                duration = int(input("输入您的选择："))
                if duration > 0:
                    break
            except ValueError:
                pass
            print("无效输入，请输入大于零的时间。")

        if remember_dur == 0:
            while True:
                try:
                    print("是否记住运行时间选择？0 为否，1 为记住选择，2 为否且不再询问。")
                    remember_dur = int(input("输入您的选择："))
                    if remember_dur in [0, 1, 2]:
                        break
                except ValueError:
                    pass
                print("无效输入，请输入 0、1 或 2。")
        else:
            print("运行时间已不再询问，请删除 info.txt 进行重新设置。")

if __name__ == "__main__":
    stop = False

    # 初始化用户信息文件
    info = load_info()
    foreground = info.get("foreground")
    closure = info.get("closure")
    duration = info.get("duration")
    remember_fg = info.get("remember_foreground", 0)
    remember_cls = info.get("remember_closure", 0)
    remember_dur = info.get("remember_duration", 0)

    if remember_fg != 1 or remember_cls != 1:
        ask_user_choice()

        # 更新并保存选择
        info["foreground"] = foreground
        info["closure"] = closure
        info["duration"] = duration
        info["remember_foreground"] = remember_fg
        info["remember_closure"] = remember_cls
        info["remember_duration"] = remember_dur
        save_info(info)

    keyboard.on_press(on_key_press)
    game_nd = init_window()

    if game_nd is not None:
        tm = time.time()
        end_time = tm + 60 * duration
        print("游戏窗口已找到，开始运行。")
        print(f"运行时间：{duration} 分钟，预计结束时刻：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}。")

        time.sleep(1)
        press('f', 0.2)
        recent_a = 0
        notif_tm = time.time()

        while not stop and time.time() < end_time:
            # 剩余时间提醒
            if time.time() - notif_tm > (60 * 30): # 30 分钟提醒一次
                print(f"已运行 {int((time.time() - tm) // 60)} 分钟，剩余 {duration - int((time.time() - tm) // 60)} 分钟。")
                notif_tm = time.time()

            time.sleep(random.random() * 1 + 2)
            press('f', 0.2)

            if time.time() - recent_a > 10:
                recent_a = time.time()
                press('a', 0.2, False)

        if stop:
            print("运行已停止。")
        else:
            print(f"运行时间已达 {duration} 分钟，运行自动停止。")
            if closure == 1:
                print("准备自动关闭游戏窗口...")
                close_window(game_nd)

        time.sleep(1)
