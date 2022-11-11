import pathlib
import sys

project_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.append(f"{project_root}")
django_root = f"{pathlib.Path(__file__).parent.parent.parent.resolve()}/promote_me_not"
sys.path.append(f"{django_root}")

import threading
import time
from typing import Any
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import JavascriptException, NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver.remote.webelement import WebElement
from common.common import get_browser, UNIT_VALUES
from linked_in.lk_secret import PASSWORD, USERNAME
from linked_in.site_info import LOGIN, SEARCH_LINKS, WEBSITE_ALIAS, JOB_TABS_CONTAINER_CLASSNAME, \
    MINIMUM_TIME_PER_PAGE_SECONDS, DESCRIPTION_CLASSNAME
from common.cookies_store import cookies_get, cookies_load
import datetime
import re
import os
from django import setup
from queue import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()
from display_jobs.models import JobPosting
from django.utils import timezone


def verified_human(br: Chrome) -> bool:
    for _ in range(0, 4):
        try:
            br.find_element(By.ID, 'captchaInternalPath')
            return False
        except NoSuchElementException:
            time.sleep(0.5)
    return True


def is_logged_in(br: Chrome, max_tries=4) -> bool:
    for attempt in range(0, max_tries + 1):
        try:
            br.find_element(By.CLASS_NAME, 'ember-application')
            print("User logged in, grabbing cookies.")
            cookies_get(br, f"{WEBSITE_ALIAS}_cookies.pkl")
            return True
        except:
            if attempt == max_tries:
                return False
            sleep_time = 0.1
            print(f"Rechecking user is logged-in; in {sleep_time} seconds")
            time.sleep(sleep_time)


def lk_login(br: Chrome, u=USERNAME, p=PASSWORD) -> bool:
    br.get(LOGIN)
    br.find_element(By.ID, 'username').send_keys(u)
    pbox = br.find_element(By.ID, 'password')
    pbox.send_keys(p)
    pbox.send_keys(Keys.ENTER)
    if not is_logged_in(br):
        if not verified_human(br):
            print(f"User is not verified as human, will continue once that's done.")
        while not verified_human(br):
            pass
        time.sleep(4)
    cookies_get(br, f"{WEBSITE_ALIAS}_cookies.pkl")

    return True


class LinkedInInsightsNotLoaded(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def next_page(pagination_box: WebElement) -> bool:
    buttons = pagination_box.find_elements(By.XPATH, "*")
    selected_button = pagination_box.find_element(By.CLASS_NAME, 'selected')
    click_next = False
    last_page_name = "Undefined/no page in paginator."
    for item in buttons:
        if item == selected_button:
            last_page_name = item.text
            click_next = True
            continue

        if click_next:
            while True:
                item.click()
                return True
    print(f"There is no next page, last page was: {last_page_name}")
    return False


def get_job_posting(job_id: Any, site_name: str, job_details: WebElement) -> JobPosting:
    title = job_details.find_element(By.CLASS_NAME, "jobs-unified-top-card__job-title").text
    posted_date = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__posted-date').text

    magnitude, unit, _ = posted_date.split(" ")
    unit_seconds = UNIT_VALUES[unit]
    posted_date = timezone.now() - datetime.timedelta(seconds=unit_seconds * int(magnitude))

    company_name = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__company-name').text

    try:
        workplace_type = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__workplace-type').text
    except NoSuchElementException:
        workplace_type = "Unspecified"
    insights = job_details.find_elements(By.CLASS_NAME, 'jobs-unified-top-card__job-insight')
    if len(insights) == 0:
        raise LinkedInInsightsNotLoaded(f"Browser has not loaded insights yet.")
    full_time_or_other = insights[0].text
    if "·" in full_time_or_other:
        full_time_or_other, entry_level = full_time_or_other.split("·")[0].strip(), full_time_or_other.split("·")[
            1].strip()
    else:
        entry_level = "Unspecified"

    company_size = insights[1].text
    if "·" in company_size:
        company_size, company_type = company_size.split("·")[0].strip(), company_size.split("·")[1].strip()
    else:
        company_type = "Unspecified"

    applicants = 0
    for i in range(0, 3):
        try:
            applicants = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__applicant-count').text
            applicants = int(applicants.split(" ")[0])
            break
        except NoSuchElementException:
            time.sleep(0.1)

    job_description = job_details.find_element(By.CLASS_NAME, DESCRIPTION_CLASSNAME).get_attribute('innerHTML')
    location = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__bullet').text

    job = JobPosting(
        job_id=job_id,
        title=title,
        posted_date=posted_date,
        company_name=company_name,
        applicants=applicants,
        workplace_type=workplace_type,
        company_size=company_size,
        company_type=company_type,
        full_time_or_other=full_time_or_other,
        description=job_description,
        site_scraped_from=site_name,
        location=location,
        entry_level=entry_level)
    return job


def main(br) -> None:
    global UNSAVED_JOBS

    br.get(LOGIN)
    # https://www.linkedin.com/jobs/search/?currentJobId=3341349350&f_E=2&geoId=102890719&keywords=python&start=750git
    cookies_load(br, f"{WEBSITE_ALIAS}_cookies.pkl")
    br.get(LOGIN)
    # Used while looking at the element text before clicking on it, thus skipping already-seen-jobs.
    print("Loading known jobs..")
    seen_job_card_texts = [f"{item.title}-{item.company_name}" for item in JobPosting.objects.filter(site_scraped_from=WEBSITE_ALIAS)]
    print(f"Loaded {len(seen_job_card_texts)} job titles to be skipped.")
    # If we're trying to acquire elements that have not loaded yet, we increase this.
    # We time.sleep this number as well as set it as the browser implicit wait time
    insights_time_offset = 0
    element_intercept_click_offset = 0.3
    prev_ignored = 0

    if not is_logged_in(br):
        lk_login(br)
    for link in SEARCH_LINKS:
        br.get(link)
        print(f"Scraping {link}, previously ignored {prev_ignored} posts.")
        prev_ignored = 0
        if 'No matching jobs found' in br.page_source:
            print(f"Linkedin shadowbanned search feature. exit.")
            exit()
        time.sleep(2)

        while True:
            start_time_on_page = datetime.datetime.now()
            zoom_to_elements_by_class_name(br, 'scaffold-layout__list-container', 0, print_failure=False)

            try:
                container = br.find_element(By.CLASS_NAME, 'scaffold-layout__list-container')
            except NoSuchElementException:
                if 'No matching jobs found' in br.page_source:
                    break
                if 'premium/products' in br.current_url:
                    print("Premium products page encountered, reloadling currently search link and continuing."
                          "(Suggestions on where to stuff premium ads not volunteered)")
                    br.get(link)
                    continue
                raise RuntimeError("Unexpected website state.")

            visible_cards = container.find_elements(By.XPATH, "*")
            for n, item in enumerate(visible_cards):
                zoomed_to_card = False
                stale_item_text = False
                for i in range(0, 2):
                    try:
                        card_text = item.text
                        break
                    except StaleElementReferenceException:
                        zoom_to_elements_by_class_name(br, 'job-card-list__title', n - 1, print_failure=False)
                        print("Oh, the staleness.")
                        if 'No matching jobs found' in br.page_source:
                            break
                        time.sleep(0.5)
                        if i == 1:
                            stale_item_text = True
                if stale_item_text:
                    continue

                while card_text == "":
                    if zoom_to_elements_by_class_name(br, 'job-card-list__title', n - 1, print_failure=False):
                        zoomed_to_card = True
                    card_text = item.text
                    time.sleep(insights_time_offset)
                if 'Refine by title' in card_text:
                    continue
                card_text = "-".join(card_text.split("\n")[0:2])
                if card_text not in seen_job_card_texts:
                    seen_job_card_texts.append(card_text)
                else:
                    prev_ignored += 1
                    continue

                # We need to be able to click on it, the text may have been seen before zooming to it.
                if not zoomed_to_card:
                    zoom_to_elements_by_class_name(br, 'job-card-list__title', n - 1, print_failure=False)

                attempts = 5
                while attempts:
                    try:
                        item.find_element(By.CLASS_NAME, 'job-card-list__title').click()
                        break
                    except (NoSuchElementException, StaleElementReferenceException):
                        print(f"Failed on item{item.text} due to nosuch or stale element. Retrying in {6 - attempts}")
                        time.sleep(6 - attempts)
                        attempts -= 1
                    except ElementClickInterceptedException:
                        print("Other element would receive click exception, retrying.")
                        time.sleep(element_intercept_click_offset)
                        element_intercept_click_offset += 0.15
                if not attempts:
                    print(f"Failed to acquire element by class {'job-card-list__title'} {5} times. Reloading link")
                    br.get(link)
                    raise RuntimeError("Mistakes were made.")

                attempts = 4
                while True:
                    time.sleep(insights_time_offset)
                    details = br.find_element(By.CLASS_NAME, JOB_TABS_CONTAINER_CLASSNAME)

                    try:
                        job_id = re.search(r"currentJobId=(.+?)&", br.current_url)[1]
                        job = get_job_posting(job_id, WEBSITE_ALIAS, details)
                        may_exist = JobPosting.objects.filter(job_id=job_id,site_scraped_from=WEBSITE_ALIAS)
                        if not may_exist:
                            UNSAVED_JOBS.put(job)
                        else:
                            may_exist[0].update(job)
                        break
                    except LinkedInInsightsNotLoaded:
                        print("Insights not loaded, retrying.")
                        insights_time_offset += 0.025
                        br.implicitly_wait(0.5 + insights_time_offset)
                        time.sleep(insights_time_offset)
                    except StaleElementReferenceException:
                        print("Stale element exception, retrying.")
                        time.sleep(2)
                    except NoSuchElementException as e:
                        if 'No longer accepting applications' in details.text:
                            print("Skipping, job offer is closed")
                            # TODO: Expand the model to flag closed job positions
                            break
                        print(str(e))
                    except Exception as e:
                        print(f"Mishandled exception, continuing to next post, exception was: {str(e)}")
                        attempts -= 1
                        time.sleep(4 - attempts)

            wait_for_insights_to_load(br)

            while datetime.datetime.now() - start_time_on_page < datetime.timedelta(
                    seconds=MINIMUM_TIME_PER_PAGE_SECONDS):
                pass

            if not zoom_to_elements_by_class_name(br, 'artdeco-pagination__pages', 0):
                print(
                    f"JavascriptException when scrolling element into view for {3} consecutive attempts.-> Assuming this page has no more entries")
                print("Reached last page on this search (Couldn't zoom to paginator)")
                break

            pagination_box = br.find_element(By.CLASS_NAME, 'artdeco-pagination__pages')

            if not next_page(pagination_box):
                print("Reached last page on this search")
                break
            wait_for_insights_to_load(br)


def wait_for_insights_to_load(br: Chrome, max_attempts=10):
    while True:
        try:
            # Before paginating, we ensure the currenet pge has finished loading.
            # linkedin doesnt like it when you blaze through the paginator
            if len(br.find_element(By.CLASS_NAME, JOB_TABS_CONTAINER_CLASSNAME).find_elements(By.CLASS_NAME,
                                                                                              'jobs-unified-top-card__job-insight')) > 0:
                break
        except Exception as e:
            time.sleep(0.5)
            max_attempts -= 1
            if not max_attempts:
                raise e


def zoom_to_elements_by_class_name(br, class_name, index, max_attempts=4, print_failure=True):
    rv = False
    for i in range(0, max_attempts + 1):
        try:
            script = f"document.getElementsByClassName('{class_name}')[{index}].scrollIntoView(true)"
            br.execute_script(script)
            rv = True
            break
        except JavascriptException:
            if print_failure:
                print(f"Couldn't zoom to {class_name}. Retrying.")
            time.sleep(0.1)
            continue
    return rv


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
    browser = get_browser()
    browser.implicitly_wait(0.5)
    browser.set_window_size(1920, 2048)
    try:
        main(browser)
    finally:
        print(f"Closed at: {browser.current_url}")
        browser.close()
