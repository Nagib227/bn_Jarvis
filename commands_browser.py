import webbrowser
import os


def open_browser():
    webbrowser.open("https://")
    

def open_page(page="https://bread-network.ru/"):
    webbrowser.open(page)
    

def close_browser():
    os.system("Taskkill /IM browser.exe /F")


def browser_search(req):
    req = "+".join(req.split())
    webbrowser.open(f"https://yandex.ru/search/?text={req}")
