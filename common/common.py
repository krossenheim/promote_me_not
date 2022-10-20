from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os

job_saving_folder_path = '../jobs'


def get_browser() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    br = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=chrome_options)
    return br


def create_destination_folders(website_alias):
    website_jobs_save_path = f'{job_saving_folder_path}/{website_alias}'
    if not os.path.isdir(f'{job_saving_folder_path}'):
        os.mkdir(job_saving_folder_path)
        os.mkdir(website_jobs_save_path)
    elif not os.path.isdir(website_jobs_save_path):
        os.mkdir(website_jobs_save_path)
