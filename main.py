import datetime
import json
import os
import queue
import random
import struct
import subprocess
import sys
import time

import openai
from openai import error
import pvporcupine
import vosk
import yaml
from fuzzywuzzy import fuzz
from pvrecorder import PvRecorder

import wave
import contextlib
from pygame import mixer

import tts
import config

from commands_browser import *
from commands_gaming import *
from commands_pk import *


mixer.init()

# some consts
CDIR = os.getcwd()
VA_CMD_LIST = yaml.safe_load(
    open('commands.yaml', 'rt', encoding='utf8'),
)

# ChatGPT vars
system_message = {"role": "system", "content": "Ты голосовой ассистент из железного человека."}
message_log = [system_message]

# init openai
openai.api_key = config.OPENAI_TOKEN

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


def gpt_answer():
    global message_log

    model_engine = "gpt-3.5-turbo"
    max_tokens = 256  # default 1024
    try:
        response = openai.ChatCompletion.create(
            model=model_engine,
            messages=message_log,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1,
            stop=None
        )
    except (error.TryAgain, error.ServiceUnavailableError):
        return "чат джипити перегружен!"
    except openai.OpenAIError as ex:
        # если ошибка - это макс длина контекста, то возвращаем ответ с очищенным контекстом
        if ex.code == "context_length_exceeded":
            message_log = [system_message, message_log[-1]]
            return gpt_answer()
        else:
            return "Не удалось подключиться к джипити"

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response.choices[0].message.content


# play(f'{CDIR}\\sound\\ok{random.choice([1, 2, 3, 4])}.wav')
def say(filename):
    with contextlib.closing(wave.open(filename, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
    duration = frames / float(rate)
    
    mixer.music.load(filename)
    mixer.music.play()
    time.sleep(duration)

def play(phrase, wait_done=True):
    global recorder
    filename = f"{CDIR}\\sound\\"

    if phrase == "greet":
        filename += f"greet{random.choice([1, 2, 3])}.wav"
    elif phrase == "ok1":
        filename += f"ok1.wav"
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


def q_callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def va_respond(voice: str):
    global recorder, message_log, first_request
    print(f"Распознано: {voice}")

    cmd = recognize_command(filter_command(voice))

    print(cmd)

    if len(cmd['cmd'].strip()) <= 0:
        return False
    elif cmd['percent'] < 70 or cmd['cmd'] not in VA_CMD_LIST.keys():
        if fuzz.ratio(voice.join(voice.split()[:1]).strip(), "найди") > 75:
            play("ok")
            browser_search(voice.join(voice.split()[1:]).strip())
            return False
        elif fuzz.ratio(voice.join(voice.split()[:1]).strip(), "скажи") > 75:
            play("ok1")
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
    elif cmd == 'open_bn':
        open_page(page="https://bread-network.ru/")
        play("ok")
    elif cmd == 'open_google':
        open_page(page="https://www.google.com/")
        play("ok")
    elif cmd == 'open_youtube':
        open_page(page="https://www.youtube.com/")
        play("ok")
    elif cmd == 'music':
        open_page(page="https://rur.hitmotop.com/")
        open_page(page="https://music.yandex.ru/promo/quiz/?utm_source=direct_network&utm_medium=paid_performance&utm_campaign=90062188%7CMSCAMP-4_[MU-P]_%7BWM:N%7D_RU-225_goal-PL_Tovarnaya-Quiz-Domen&utm_content=cid%7C90062188%7Cgid%7C5230967356%7Caid%7C14777156718&yclid=12164668103123533823/")
        play("ok")

    elif cmd == 'gaming_mode_on':
        play("ok")
        start_gaming_mode()
        play("ready")
    elif cmd == 'gaming_mode_off':
        play("ok")
        stop_gaming_mode()
        play("ready")

    elif cmd == 'stop_all_processes':
        play("ok")
        stop_all_processes()
        play("ready")
    elif cmd == 'completion_work':
        play("ok")
        completion_work()

    elif cmd == 'thanks':
        play("thanks")
    elif cmd == 'stupid':
        play("stupid")
    elif cmd == 'off':
        play("off", True)
        porcupine.delete()
        exit(0)

    elif cmd == 'sound_on':
        sound_on()
        play("ok")
    elif cmd == 'sound_off':
        play("ok", True)
        sound_off()


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
