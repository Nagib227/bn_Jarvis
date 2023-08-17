import os
import ctypes
import pyautogui


this_folder = os.getcwd()

def file_find(name, path=r'C://'):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None


def start_gaming_mode():
    close_all_windows()
    path_steam = file_find("steam.exe")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, rf"{this_folder}\img\test_desktop.jpg" , 0)
    if path_steam:
        os.startfile(path_steam)


def close_all_windows():
    pyautogui.hotkey('win', 'd')

        
def stop_gaming_mode():
    os.system("TASKKILL /F /IM steam.exe")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, rf"{this_folder}\img\defolt_desktop.png" , 0)

