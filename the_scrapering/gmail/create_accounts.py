import sys
import pathlib

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(f"{project_root}\promote_me_not")

from common.common import get_browser
from selenium.webdriver.common.by import By
from unique_names_generator import get_random_name
from django import setup
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()

URL = "http://accounts.google.com/signupmobile"


class FillIn:
    def __init__(self):
        self.firstname = get_random_name(separator='')
        self.lastname = get_random_name(separator='')
        self.username = get_random_name(separator='')
        self.password = f"123A${get_random_name(separator='')}"

    def __iter__(self):
        return [self.firstname, self.lastname, self.username, self.password, self.password]

    def __getitem__(self, item):
        return self.__iter__()[item]


def main():
    agent = "Mozilla/5.0 (Linux; U; Android 4.0.2; en-us; Galaxy Nexus Build/ICL53F) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
    persons = [FillIn()]
    browser = get_browser()
    for person in persons:
        browser.get(URL)
        fieldnames = "firstName,lastName,username,password,ConfirmPasswd".split(",")
        fieldTypes = [By.ID, By.ID, By.ID, By.ID, By.NAME]
        for n, item in enumerate(fieldnames):
            browser.find_element(by=fieldTypes[n]).send_keys(person[n])
        browser.find_element(By.XPATH,
                             '/html/body/div[1]/div[1]/div[2]/div[1]/div[2]/div/div/div[2]/div/div[2]/div/div[1]/div/div/button/div[3]').click()


if __name__ == "__main__":
    main()
