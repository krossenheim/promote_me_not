from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
import platform
job_saving_folder_path = '../jobs'


def get_browser(option_arguments=("--headless","--no-sandbox",)) -> webdriver.Chrome:
    executable_path = ChromeDriverManager().install() if platform.system() == 'Windows' else ChromeDriverManager(version='105.0.5195.19').install()
    chrome_options = Options()
    for argument in option_arguments:
        chrome_options.add_argument(argument)
    br = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
    return br


def create_destination_folders(website_alias):
    website_jobs_save_path = f'{job_saving_folder_path}/{website_alias}'
    if not os.path.isdir(f'{job_saving_folder_path}'):
        os.mkdir(job_saving_folder_path)
        os.mkdir(website_jobs_save_path)
    elif not os.path.isdir(website_jobs_save_path):
        os.mkdir(website_jobs_save_path)
