import os
from comtypes import CLSCTX_ALL
from ctypes import POINTER, cast
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)


NOT_STOP_PROCESS = ["python.exe", "pythonw.exe"]


def stop_all_processes():
    for v in os.popen("tasklist"):
        try:
            if not v.split()[0] in NOT_STOP_PROCESS:
                os.system(f"TASKKILL /F /IM {v.split()[0]}")
        except Exception:
            continue


def completion_work():
    os.system("shutdown /s")


def sound_off():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)


def sound_on():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(0, None)
