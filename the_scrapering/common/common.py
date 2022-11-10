from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import platform


def get_browser(option_arguments=("--headless", "--no-sandbox",)) -> webdriver.Chrome:
    manager = ChromeDriverManager() if platform.system() == 'Windows' else ChromeDriverManager(version='105.0.5195.19')
    chrome_options = Options()
    for argument in option_arguments:
        chrome_options.add_argument(argument)
    br = webdriver.Chrome(executable_path=manager.install(), options=chrome_options)
    return br

UNIT_VALUES = {
    'seconds': 1,
    'second': 1,
    'minutes': 60,
    'minute': 60,
    'hour': 60 * 60,
    'hours': 60 * 60,
    'day': 60 * 24 * 60,
    'days': 60 * 24 * 60,
    'week': 60 * 24 * 60 * 7,
    'weeks': 60 * 24 * 60 * 7,
    'month': 60 * 24 * 60 * 30,
    'months': 60 * 24 * 60 * 30,
    'years': 60 * 24 * 60 * 30 * 12,
    'year': 60 * 24 * 60 * 30 * 12,
}