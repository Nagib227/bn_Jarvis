import datetime
import json
import os
import queue
import random
import struct
import subprocess
import sys
import time
from ctypes import POINTER, cast

# import openai
# from openai import error
import pvporcupine
import vosk
import yaml
from comtypes import CLSCTX_ALL
from fuzzywuzzy import fuzz
from pvrecorder import PvRecorder
from pycaw.pycaw import (
    AudioUtilities,
    IAudioEndpointVolume
)
from rich import print

import wave
from pygame import mixer

import config
from commands import *


mixer.init()

# some consts
CDIR = os.getcwd()
VA_CMD_LIST = yaml.safe_load(
    open('commands.yaml', 'rt', encoding='utf8'),
)

# ChatGPT vars
# system_message = {"role": "system", "content": "Ты голосовой ассистент из железного человека."}
# message_log = [system_message]

# init openai
# openai.api_key = config.OPENAI_TOKEN

# PORCUPINE
porcupine = pvporcupine.create(
    access_key=config.PICOVOICE_TOKEN,
    keywords=['jarvis'],
    sensitivities=[1]
)
# print(pvporcupine.KEYWORDS)

# VOSK
model = vosk.Model("model_small")
samplerate = 16000
device = config.MICROPHONE_INDEX
kaldi_rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()


# play(f'{CDIR}\\sound\\ok{random.choice([1, 2, 3, 4])}.wav')
def say(filename):
    mixer.music.load(filename)
    mixer.music.play()

def play(phrase, wait_done=True):
    global recorder
    filename = f"{CDIR}\\sound\\"

    if phrase == "greet":  # for py 3.8
        filename += f"greet{random.choice([1, 2, 3])}.wav"
    elif phrase == "ok":
        filename += f"ok{random.choice([1, 2, 3])}.wav"
    elif phrase == "not_found":
        filename += "not_found.wav"
    elif phrase == "thanks":
        filename += "thanks.wav"
    elif phrase == "run":
        filename += "run.wav"
    elif phrase == "stupid":
        filename += "stupid.wav"
    elif phrase == "ready":
        filename += "ready.wav"
    elif phrase == "off":
        filename += "off.wav"

    if wait_done:
        recorder.stop()

    say(filename)

    if wait_done:
        recorder.start()


def va_respond(voice: str):
    global recorder, message_log, first_request
    print(f"Распознано: {voice}")

    cmd = recognize_command(filter_command(voice))

    print(cmd)

    if len(cmd['cmd'].strip()) <= 0:
        return False
    elif cmd['percent'] < 70 or cmd['cmd'] not in VA_CMD_LIST.keys():
        if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:

            message_log.append({"role": "user", "content": voice})
            response = gpt_answer()
            message_log.append({"role": "assistant", "content": response})

            recorder.stop()
            tts.va_speak(response)
            time.sleep(0.5)
            recorder.start()
            return False
        else:
            play("not_found")
            time.sleep(1)

        return False
    else:
        execute_cmd(cmd['cmd'], voice)
        return True


def filter_command(raw_voice: str):
    cmd = raw_voice

    for x in config.VA_ALIAS:
        cmd = cmd.replace(x, "").strip()

    for x in config.VA_TBR:
        cmd = cmd.replace(x, "").strip()

    return cmd


def recognize_command(cmd: str):
    rc = {'cmd': '', 'percent': 0}
    for c, v in VA_CMD_LIST.items():

        for x in v:
            vrt = fuzz.ratio(cmd, x)
            if vrt > rc['percent']:
                rc['cmd'] = c
                rc['percent'] = vrt

    return rc


def execute_cmd(cmd: str, voice: str):
    if cmd == 'open_browser':
        open_browser()
        play("ok")
    elif cmd == 'close_browser':
        close_browser()
        play("ok")

    elif cmd == 'open_google':
        open_page(page="https://www.google.com/")
        play("ok")

    elif cmd == 'open_youtube':
        open_page(page="https://www.youtube.com/")
        play("ok")

    # elif cmd == 'music':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Run music.exe'])
    #     play("ok")
    #
    # elif cmd == 'music_off':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Stop music.exe'])
    #     time.sleep(0.2)
    #     play("ok")
    #
    # elif cmd == 'music_save':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Save music.exe'])
    #     time.sleep(0.2)
    #     play("ok")
    #
    # elif cmd == 'music_next':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Next music.exe'])
    #     time.sleep(0.2)
    #     play("ok")
    #
    # elif cmd == 'music_prev':
    #     subprocess.Popen([f'{CDIR}\\custom-commands\\Prev music.exe'])
    #     time.sleep(0.2)
    #     play("ok")
    #
    # elif cmd == 'sound_off':
    #     play("ok", True)
    #
    #     devices = AudioUtilities.GetSpeakers()
    #     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #     volume = cast(interface, POINTER(IAudioEndpointVolume))
    #     volume.SetMute(1, None)
    #
    # elif cmd == 'sound_on':
    #     devices = AudioUtilities.GetSpeakers()
    #     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #     volume = cast(interface, POINTER(IAudioEndpointVolume))
    #     volume.SetMute(0, None)
    #
    #     play("ok")
    #
    # elif cmd == 'thanks':
    #     play("thanks")
    #
    # elif cmd == 'stupid':
    #     play("stupid")
    #
    # elif cmd == 'gaming_mode_on':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to gaming mode.exe'])
    #     play("ready")
    #
    # elif cmd == 'gaming_mode_off':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch back to workspace.exe'])
    #     play("ready")
    #
    # elif cmd == 'switch_to_headphones':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to headphones.exe'])
    #     time.sleep(0.5)
    #     play("ready")
    #
    # elif cmd == 'switch_to_dynamics':
    #     play("ok")
    #     subprocess.check_call([f'{CDIR}\\custom-commands\\Switch to dynamics.exe'])
    #     time.sleep(0.5)
    #     play("ready")
    #
    # elif cmd == 'off':
    #     play("off", True)
    #
    #     porcupine.delete()
    #     exit(0)


# `-1` is the default input audio device.
recorder = PvRecorder(device_index=config.MICROPHONE_INDEX, frame_length=porcupine.frame_length)
recorder.start()
print('Using device: %s' % recorder.selected_device)

print(f"Jarvis (v3.0) начал свою работу ...")
play("run")
time.sleep(0.5)

ltc = time.time() - 1000

while True:
    try:
        pcm = recorder.read()
        keyword_index = porcupine.process(pcm)

        if keyword_index >= 0:
            recorder.stop()
            play("greet", True)
            print("Yes, sir.")
            recorder.start()  # prevent self recording
            ltc = time.time()

        while time.time() - ltc <= 10:
            pcm = recorder.read()
            sp = struct.pack("h" * len(pcm), *pcm)

            if kaldi_rec.AcceptWaveform(sp):
                if va_respond(json.loads(kaldi_rec.Result())["text"]):
                    ltc = time.time()

                break

    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
        raise
