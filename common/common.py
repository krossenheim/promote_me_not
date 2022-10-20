from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import psutil


def kill_chromes():
    for proc in psutil.process_iter():
        if 'chrome' in proc.name():
            print("killing ",proc.name())
            proc.kill()


def get_browser(kill_chrome=False) -> webdriver.Chrome:
    if kill_chrome:
        kill_chromes()
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chromedata")
    br = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
    return br
