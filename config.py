from dotenv import load_dotenv
import os

# Find .env file with os variables
load_dotenv("dev.env")

# Конфигурация
VA_NAME = 'Jarvis'
VA_VER = "3.0"
VA_ALIAS = ('джарвис',)
VA_TBR = ('скажи', 'покажи', 'ответь', 'произнеси', 'расскажи', 'сколько', 'слушай')

# ID микрофона (можете просто менять ID пока при запуске не отобразится нужный)
# -1 это стандартное записывающее устройство
MICROPHONE_INDEX = -1

# Путь к браузеру Google Chrome
CHROME_PATH = 'C:/Users/Admin/Chrom/chrome-win64/chrome.exe'

# Токен Picovoice
PICOVOICE_TOKEN = 'S7d97CcqxxN7ZLITu2H7g1mD2tYlAgJHmfWnSMbIctsMTms5WQzC2A=='

# Токен OpenAI
OPENAI_TOKEN = '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'
