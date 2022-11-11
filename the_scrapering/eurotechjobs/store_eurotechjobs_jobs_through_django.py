import pathlib
import sys

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(f"{project_root}")
django_root = f"{pathlib.Path(__file__).parent.parent.parent.resolve()}/promote_me_not"
sys.path.append(f"{django_root}")

import threading
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from common.common import get_browser
from eurotechjobs.site_info import SEARCH_URLS, WEBSITE_ALIAS
import os
from django import setup
from queue import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()
from display_jobs.models import JobPosting


def lang_detection_thread():
    global UNSAVED_JOBS
    while True:
        time.sleep(5)
        while not UNSAVED_JOBS.empty():
            job = UNSAVED_JOBS.get()
            job.detect_description_language()
            job.save()


def get_urls_on_a_search(br: Chrome, search_link: str) -> list:
    br.get(search_link)
    job_url_elements = br.find_element(By.CLASS_NAME, "searchList").find_elements(By.XPATH,
                                                                                  f"//*[contains(@href, 'job_display')]")
    job_urls = list()

    for webelement in job_url_elements:
        link = webelement.get_attribute('href')
        if link not in job_urls:
            job_urls.append(link)
    return job_urls


def main(br: Chrome):
    all_search_url = list()
    for search_url in SEARCH_URLS:
        for job_url in get_urls_on_a_search(br, search_url):
            all_search_url.append(job_url)
    all_search_url = set(all_search_url)

    for search_url in all_search_url:
        br.get(search_url)
        contentbox = br.find_element(By.CLASS_NAME, 'contentbox')
        job_contents = contentbox.find_elements(By.XPATH, "*")
        title, company, location = [item.text.strip() for item in job_contents[0:3]]
        job_description = str()
        for item in job_contents[3:]:
            if f"Don't forget to mention " in item.text or "Apply Now" in item.text:
                break
            item_html = item.get_attribute('innerHTML')
            job_description += item_html
        job_id = search_url.split("/")[-2]
        job = JobPosting(
            job_id=job_id,
            title=title,
            company_name=company,
            description=job_description,
            site_scraped_from=WEBSITE_ALIAS,
            location=location,
        )
        UNSAVED_JOBS.put(job)


if __name__ == "__main__":
    UNSAVED_JOBS = Queue()
    lang_detect_t = threading.Thread(target=lang_detection_thread, daemon=True)
    lang_detect_t.start()
    browser = get_browser()
    browser.implicitly_wait(0.5)
    browser.set_window_size(1920, 2048)
    try:
        main(browser)
    finally:
        print(f"Closed at: {browser.current_url}")
        browser.close()
