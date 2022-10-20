from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def get_browser(kill_chrome=False) -> webdriver.Chrome:
    if kill_chrome:
        kill_chromes()
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    br = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
    return br
