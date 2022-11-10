import pathlib
import sys

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(f"{project_root}")
django_root = f"{pathlib.Path(__file__).parent.parent.parent.resolve()}/promote_me_not"
sys.path.append(f"{django_root}")

import threading
import time
from selenium.webdriver import Chrome
from common.common import get_browser
import os
from django import setup
from queue import Queue
from itjobs_dot_ai.site_info import SEARCH_LINKS
from selenium.webdriver.common.by import By
from selenium.common.exceptions import JavascriptException, NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()


def main(br: Chrome):
    for link in SEARCH_LINKS:
        br.get(link)
        while True:
            infinite_scroll_component = br.find_element(By.CLASS_NAME, "infinite-scroll-component")
            articles = infinite_scroll_component.find_elements(By.CLASS_NAME, "job-abstract")
            if not articles:
                print(f"Finished search at {link}")
                break
            for i in range(0, len(articles)):
                scroll_to_second_child_of_infinite_scroll_component(br)
                clicked = False
                while True:
                    try:
                        if not clicked:
                            job_title_element = articles[i].find_elements(By.XPATH, "*")[0].find_element(By.CLASS_NAME,
                                                                                                         "job-header")
                            job_title = job_title_element.text
                            job_title_element.click()
                            clicked = True
                        job_details_element = br.find_element(By.CLASS_NAME, "job-details")
                        title = ""
                        tstart = datetime.datetime.now()
                        while title != job_title:
                            if datetime.datetime.now() - tstart > datetime.timedelta(seconds=15) or "Bad gateway" in br.page_source:
                                clicked = False
                                br.back()
                                break
                            try:
                                title = job_details_element.find_elements(By.XPATH, "*")[1].text
                            except StaleElementReferenceException:
                                pass
                        else:
                            break
                    except StaleElementReferenceException:
                        pass

                job_features_element = job_details_element.find_element(By.CLASS_NAME, 'job-features')
                job_features_children_elements = job_features_element.find_elements(By.XPATH, "*")
                if len(job_features_children_elements) < 5:
                    offset = -1
                else:
                    offset = 0
                company = job_features_children_elements[0].text if offset == 0 else "Not listed"
                location = job_features_children_elements[1 + offset].text
                date_listed = job_features_children_elements[2 + offset].text
                external_url = job_features_children_elements[3 + offset].text
                tags_html = job_features_children_elements[4 + offset].get_attribute('innerHTML')
                description_html = job_details_element.find_element(By.CLASS_NAME,
                                                                    'job-description-block').get_attribute('innerHTML')
                full_description = f"{tags_html}<br><br>{description_html}"
                print(title)
                remove_second_child_of_infinite_scroll_component(br)
            scroll_to_get_more_posts(br)


def scroll_to_second_child_of_infinite_scroll_component(br: Chrome) -> bool:
    script = "document.getElementsByClassName('infinite-scroll-component')[0].children[1].scrollIntoView()"
    br.execute_script(script)
    return True


def remove_second_child_of_infinite_scroll_component(br: Chrome) -> bool:
    script = "document.getElementsByClassName('infinite-scroll-component')[0].children[1].remove()"
    br.execute_script(script)
    return True


def scroll_to_get_more_posts(br: Chrome) -> bool:
    script = "document.getElementById('jobList').children[0].children[0].children[document.getElementById('jobList').children[0].children[0].children.length-1].children[document.getElementById('jobList').children[0].children[0].children[document.getElementById('jobList').children[0].children[0].children.length-1].children.length-1].scrollIntoView()"
    br.execute_script(script)
    return True


def lang_detection_thread():
    global UNSAVED_JOBS
    while True:
        time.sleep(5)
        while not UNSAVED_JOBS.empty():
            job = UNSAVED_JOBS.get()
            job.detect_description_language()
            job.save()


if __name__ == "__main__":
    UNSAVED_JOBS = Queue()
    lang_detect_t = threading.Thread(target=lang_detection_thread, daemon=True)
    lang_detect_t.start()
    browser = get_browser(option_arguments=tuple())
    browser.implicitly_wait(0.5)
    browser.set_window_size(1920, 2048)
    try:
        main(browser)
    finally:
        print(f"Closed at: {browser.current_url}")
        browser.close()
