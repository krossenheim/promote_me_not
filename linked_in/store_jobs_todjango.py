import time
from typing import Any
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import JavascriptException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from common.common import get_browser
from common.secret import PASSWORD
from linked_in.site_info import LOGIN, SEARCH_LINKS, WEBSITE_ALIAS
from cookies_store import cookies_get, cookies_load
import datetime
import re
import os
import sys
from django import setup

sys.path.append(r"C:\Users\jantequera\PycharmProjects\lkscrape\promote_me_not")
sys.path.append(r"C:\Users\VKPC\PycharmProjects\scrapejobs\promote_me_not")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'promote_me_not.settings')
setup()
from display_jobs.models import JobPosting
from django.utils import timezone

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
    'month': 60 * 24 * 60 * 7 * 30,
    'months': 60 * 24 * 60 * 7 * 30,
    'years': 60 * 24 * 60 * 7 * 30 * 12,
    'year': 60 * 24 * 60 * 7 * 30 * 12,
}


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
            cookies_get(br)
            return True
        except:
            if attempt == max_tries:
                return False
            sleep_time = min((5, max_tries + 0.5 - attempt))
            print(f"Rechecking user is logged-in; in {sleep_time} seconds")
            time.sleep(sleep_time)


def lk_login(br: Chrome, u='jleonardola@gmail.com', p=PASSWORD) -> bool:
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
    cookies_get(br)

    return True


class LinkedInInsightsNotLoaded(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def next_page(pagination_box: WebElement) -> bool:
    buttons = pagination_box.find_elements(By.XPATH, "*")
    selected_button = pagination_box.find_element(By.CLASS_NAME, 'selected')
    click_next = False
    for item in buttons:
        if item == selected_button:
            click_next = True
            continue
        if click_next:
            item.click()
            return True
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

    job_description = job_details.find_element(By.CLASS_NAME, 'jobs-description-content__text').text
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
    br.set_window_size(1920, 2048)
    br.get(LOGIN)
    cookies_load(br)
    br.get(LOGIN)
    # If we're trying to acquire elements that have not loaded yet, we increase this
    insights_time_offset = 0
    if not is_logged_in(br):
        lk_login(br)
    for link in SEARCH_LINKS:
        br.get(link)
        time.sleep(2)

        while True:
            zoom_to_elements_by_class_name(br, 'scaffold-layout__list-container', 0)

            try:
                container = br.find_element(By.CLASS_NAME, 'scaffold-layout__list-container')
            except NoSuchElementException:
                if 'No matching jobs found' in br.page_source:
                    break
                raise RuntimeError("Unexpected website state.")

            visible_cards = container.find_elements(By.XPATH, "*")
            for n, item in enumerate(visible_cards):
                if 'Refine by title' in item.text:
                    continue
                # Clicking the middle of the element sometimes hits a link instead, this avoids that.
                zoom_to_elements_by_class_name(br, 'job-card-list__title', n - 1)

                attempts = 5
                while attempts:
                    try:
                        item.find_element(By.CLASS_NAME, 'job-card-list__title').click()
                        break
                    except Exception as e:
                        print(f"Failed on item{item.text}. Retrying in {6 - attempts}")
                        time.sleep(6 - attempts)
                        attempts -= 1
                if not attempts:
                    raise RuntimeError("Mistakes were made.")

                attempts = 4

                while True:
                    time.sleep(0.1 + insights_time_offset)
                    details = br.find_element(By.CLASS_NAME, 'scaffold-layout__detail')
                    try:
                        job_id = re.search(r"currentJobId=(.+?)&", br.current_url)[1]
                        job = get_job_posting(job_id, WEBSITE_ALIAS, details)
                        may_exist = JobPosting.objects.filter(job_id=job_id)
                        if not may_exist:
                            job.save()
                        else:
                            may_exist[0].update(job)
                        break
                    except LinkedInInsightsNotLoaded:
                        print("Insights not loaded, retrying.")
                        insights_time_offset += 0.05
                        time.sleep(0.1)
                    except StaleElementReferenceException:
                        print("Stale element exception, retrying.")
                        time.sleep(2)
                    except NoSuchElementException:
                        if 'No longer accepting applications' in details.text:
                            print("Skipping, job offer is closed")
                            # TODO: Expand the model to flag closed job positions
                            break
                    except Exception as e:
                        print(f"Mishandled exception, continuing to next post, exception was: {str(e)}")
                        attempts -= 1
                        time.sleep(4 - attempts)

            time.sleep(0.5)

            if not zoom_to_elements_by_class_name(br, 'artdeco-pagination__pages', 0):
                print(f"JavascriptException when scrolling element into view-> Assuming this page has no more entries")
                print("Reached last page on this search")
                break

            pagination_box = br.find_element(By.CLASS_NAME, 'artdeco-pagination__pages')
            if not next_page(pagination_box):
                print("Reached last page on this search")
                break
            time.sleep(2)
        #     press_next = True


def zoom_to_elements_by_class_name(br, class_name, index):
    try:
        br.execute_script(
            f"document.getElementsByClassName('{class_name}')[{index}].scrollIntoView(true)")
        return True
    except JavascriptException:
        return False


if __name__ == "__main__":
    browser = get_browser()
    try:
        main(browser)
    except Exception as e:
        print(f"Crashed at page: {browser.current_url}\n{str(e)}")
    finally:
        print(f"Closed at: {browser.current_url}")
        browser.close()
