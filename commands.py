from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from subprocess import CREATE_NO_WINDOW
import os


service = Service(executable_path='./Chrom/chromedriver-win64/chromedriver.exe')
service.creation_flags = CREATE_NO_WINDOW
options = webdriver.ChromeOptions()
options.page_load_strategy = 'eager'
options.add_argument("--start-maximized")
options.binary_location = ".\\Chrom\\chrome-win64\\chrome.exe"

chrome_driver = None


def checking_browser(func):
    def _(*args, **kwargs):
        global chrome_driver
    
        try:
            return func(*args, **kwargs)
        except WebDriverException:
            chrome_driver = None
            return func(*args, **kwargs)
    return _

def get_all_page():
    global chrome_driver
    
    pages = []
    for i in chrome_driver.window_handles:
        chrome_driver.switch_to.window(i)
        pages.append(chrome_driver.current_url)
    return pages


def go_to_url(url):
    global chrome_driver

    pages = []
    for i in chrome_driver.window_handles:
        chrome_driver.switch_to.window(i)
        if chrome_driver.current_url == url:
            return None

# @checking_browser
def open_browser():
    global chrome_driver
    
    if chrome_driver:
        if get_all_page():
            go_to_url(get_all_page()[0])
            return None
        chrome_driver.get("https://bread-network.ru/")
        return None
    
    chrome_driver = webdriver.Chrome(service=service, options=options)
    chrome_driver.get("https://bread-network.ru/")

# @checking_browser
def open_page(page="https://bread-network.ru/"):
    global chrome_driver
    
    if chrome_driver:
        if page in get_all_page():
            go_to_url(page)
            return None
        chrome_driver.execute_script(f'''window.open("{page}","_blank");''')
        return None
    
    chrome_driver = webdriver.Chrome(service=service, options=options)
    chrome_driver.get(page)
    

def close_browser():
    global chrome_driver

    chrome_driver = None
    os.system("Taskkill /IM chrome.exe /F")

