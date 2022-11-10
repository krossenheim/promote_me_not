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
from itjobs_dot_ai.site_info import SEARCH_LINK, WEBSITE_ALIAS
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()

from display_jobs.models import JobPosting


def main(br: Chrome):
    global UNSAVED_JOBS
    seen_job_card_texts = [f"{item.title}-{item.company_name}-{item.location}" for item in
                           JobPosting.objects.filter(site_scraped_from=WEBSITE_ALIAS)]

    br.get(SEARCH_LINK)
    last_link = SEARCH_LINK
    while True:
        if 'Bad gateway' in br.page_source:
            print("Loading last known OK link before site crapped on on us.")
            br.get(last_link)
        try:
            infinite_scroll_component = br.find_element(By.CLASS_NAME, "infinite-scroll-component")
            articles = infinite_scroll_component.find_elements(By.CLASS_NAME, "job-abstract")
        except (NoSuchElementException, StaleElementReferenceException):
            continue

        num_articles = len(articles)
        if not num_articles:
            print("Scrolling for more articles")
            scroll_to_get_more_posts(br)
            continue
        scroll_to_second_child_of_infinite_scroll_component(br)
        try:
            job_card_element = infinite_scroll_component.find_elements(By.XPATH, "*")[1]
            classname_seconchild = job_card_element.get_attribute('class')
        except (NoSuchElementException, StaleElementReferenceException):
            continue
        if 'job' not in classname_seconchild:
            scroll_to_get_more_posts(br)
            continue

        try:
            job_title_element = job_card_element.find_element(By.CLASS_NAME, "job-header")
            job_title = job_title_element.text
            job_locat = job_card_element.find_element(By.CLASS_NAME, 'company-location').text
            job_comp = job_card_element.find_element(By.CLASS_NAME, 'common-link').text
        except (NoSuchElementException,StaleElementReferenceException):
            continue
        seen_job_card_text = f"{job_title}-{job_comp}-{job_locat}"
        if seen_job_card_text in seen_job_card_texts:
            print(f"Skipping {seen_job_card_text}")
            remove_second_child_of_infinite_scroll_component(br)
            continue
        seen_job_card_texts.append(seen_job_card_text)
        job_title_element.click()
        last_link = br.current_url
        job_details_element = br.find_element(By.CLASS_NAME, "job-details")


        title = ""
        tstart = datetime.datetime.now()
        while title!= job_title and datetime.datetime.now() - tstart < datetime.timedelta(seconds=20):
            if 'Bad gateway' in br.page_source:
                break
            try:
                title = job_details_element.find_elements(By.XPATH, "*")[1].text
                break
            except StaleElementReferenceException:
                pass

        if title != job_title:
            continue
        job_features_element = job_details_element.find_element(By.CLASS_NAME, 'job-features')
        job_features_children_elements = job_features_element.find_elements(By.XPATH, "*")
        if len(job_features_children_elements) < 5:
            offset = -1
        else:
            offset = 0
        company = job_features_children_elements[0].text if offset == 0 else "Not listed"
        location = job_features_children_elements[1 + offset].text
        date_listed_str = job_features_children_elements[2 + offset].find_elements(By.XPATH, "*")[1].get_attribute(
            'datetime')
        date_listed = datetime.datetime.strptime(date_listed_str,"%Y-%m-%dT%H:%M:%S")
        external_url = job_features_children_elements[3 + offset].text
        tags_html = job_features_children_elements[4 + offset].get_attribute('innerHTML')
        description_html = job_details_element.find_element(By.CLASS_NAME,
                                                            'job-description-block').get_attribute('innerHTML')
        full_description = f"{tags_html}<br><br>{description_html}"
        job_id = br.current_url.split("/")[-1]

        job = JobPosting(
            title=title,
            location=location,
            company_name=company,
            site_scraped_from=WEBSITE_ALIAS,
            posted_date=date_listed,
            description=full_description,
            job_id=job_id

        )
        UNSAVED_JOBS.put(job)
        remove_second_child_of_infinite_scroll_component(br)


def scroll_to_second_child_of_infinite_scroll_component(br: Chrome) -> bool:
    script = "document.getElementsByClassName('infinite-scroll-component')[0].children[1].scrollIntoView()"
    br.execute_script(script)
    return True


def remove_second_child_of_infinite_scroll_component(br: Chrome) -> bool:
    script = "if (document.getElementsByClassName('infinite-scroll-component')[0].children[1].textContent != '') {document.getElementsByClassName('infinite-scroll-component')[0].children[1].remove()}"
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
