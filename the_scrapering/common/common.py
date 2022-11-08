from selenium.webdriver.chrome.options import Options
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import platform


def get_browser(option_arguments=("--headless", "--no-sandbox",)) -> webdriver.Chrome:
    # manager = ChromeDriverManager() if platform.system() == 'Windows' else ChromeDriverManager(version='105.0.5195.19')
    chrome_options = Options()
    for argument in option_arguments:
        chrome_options.add_argument(argument)
    br = webdriver.Chrome(executable_path='the_scrapering/common/chromedriver', options=chrome_options)
    return br
