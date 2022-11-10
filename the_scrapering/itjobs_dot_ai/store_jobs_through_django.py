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
from itjobs_dot_ai.site_info import SEARCH_LINKS, WEBSITE_ALIAS
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()

from display_jobs.models import JobPosting


def main(br: Chrome):
    global UNSAVED_JOBS
    seen_job_card_texts = [f"{item.title}-{item.company}-{item.location}" for item in
                           JobPosting.objects.filter(site_scraped_from=WEBSITE_ALIAS)]

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
                            job_card_element = articles[i].find_elements(By.XPATH, "*")[0]
                            job_title = job_card_element.find_element(By.CLASS_NAME, "job-header").text
                            job_locat = job_card_element.find_element(By.CLASS_NAME, 'company-location').text
                            job_comp = job_card_element.find_element(By.CLASS_NAME, 'common-link').text
                            seen_job_card_text = f"{job_title}-{job_comp}-{job_locat}"
                            if seen_job_card_text in seen_job_card_texts:
                                print(f"Skipping {seen_job_card_text}")
                                break
                            seen_job_card_texts.append(seen_job_card_text)
                            job_card_element.click()
                            clicked = True
                        job_details_element = br.find_element(By.CLASS_NAME, "job-details")
                        title = ""
                        tstart = datetime.datetime.now()
                        while title != job_title:
                            if datetime.datetime.now() - tstart > datetime.timedelta(
                                    seconds=15) or "Bad gateway" in br.page_source:
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

                if not clicked:
                    continue
                job_features_element = job_details_element.find_element(By.CLASS_NAME, 'job-features')
                job_features_children_elements = job_features_element.find_elements(By.XPATH, "*")
                if len(job_features_children_elements) < 5:
                    offset = -1
                else:
                    offset = 0
                company = job_features_children_elements[0].text if offset == 0 else "Not listed"
                location = job_features_children_elements[1 + offset].text
                date_listed = job_features_children_elements[2 + offset].find_elements(By.XPATH, "*")[1].get_attribute(
                    'datetime')
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
                    first_seen=date_listed,
                    description=full_description,
                    job_id=job_id

                )
                UNSAVED_JOBS.put(job)
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
