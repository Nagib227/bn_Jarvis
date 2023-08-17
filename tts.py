import gtts 
from playsound import playsound 


def va_speak(text: str):
    audio = gtts.gTTS(text=text, lang="ru", slow=False)
    audio.save("example.mp3")
    playsound("example.mp3")
