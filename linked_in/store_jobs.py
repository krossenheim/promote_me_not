import time
from typing import Any
from common.jobposting import JobPosting
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import JavascriptException, NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from common.common import get_browser
from common.secret import PASSWORD
from linked_in.site_info import LOGIN, JOBS, WEBSITE_ALIAS
from cookies_store import cookies_get, cookies_load
import datetime
import re

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
            return True
        except:
            if attempt == max_tries:
                return False
            sleep_time = min((5, max_tries + 0.5 - attempt))
            print(f"Retrying in {sleep_time} seconds")
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


def zoom_out(br: Chrome) -> None:
    br.execute_script("document.getElementsByClassName('scaffold-layout__list')[0].style.zoom = 0.5")


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
    posted_date = datetime.datetime.now() - datetime.timedelta(seconds=unit_seconds * int(magnitude))

    company_name = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__company-name').text
    try:
        applicants = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__applicant-count').text
        applicants = int(applicants.split(" ")[0])

    except NoSuchElementException:
        applicants = 0

    try:
        workplace_type = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__workplace-type').text
    except NoSuchElementException:
        workplace_type = "Unspecified"
    company_size = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__job-insight').text
    job_description = job_details.find_element(By.CLASS_NAME, 'jobs-description-content__text').text
    location = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__bullet').text

    job = JobPosting(
        job_id,
        title,
        posted_date,
        company_name,
        applicants,
        workplace_type,
        company_size,
        job_description,
        site_name,
        location)
    return job


def main() -> None:
    br = get_browser()
    br.set_window_size(1920, 2048)
    br.get(LOGIN)
    cookies_load(br)
    br.get(LOGIN)
    if not is_logged_in(br):
        lk_login(br)
    br.get(JOBS)
    time.sleep(2)

    while True:
        container = br.find_element(By.CLASS_NAME, 'scaffold-layout__list-container')
        visible_cards = container.find_elements(By.XPATH, "*")
        for n, item in enumerate(visible_cards):
            if 'Refine by title' in item.text:
                continue
            # Clicking the middle of the element sometimes hits a link instead, this avoids that.

            try:
                br.execute_script(
                    f"document.getElementsByClassName('job-card-list__title')[{n - 1}].scrollIntoView(true)")
            except JavascriptException as e:
                print(f"JavascriptException: IGNORED")

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
                time.sleep(0.5)
                details = br.find_element(By.CLASS_NAME, 'scaffold-layout__detail')
                if not attempts:
                    raise RuntimeError("Mistakes were made 2.")
                try:
                    job_id = re.search(r"currentJobId=(.+?)&", br.current_url)[1]
                    job = get_job_posting(job_id, WEBSITE_ALIAS, details)
                    job.save()
                    break
                except Exception as e:
                    print(str(e))
                    attempts -= 1

        time.sleep(0.5)
        pagination_box = br.find_element(By.CLASS_NAME, 'artdeco-pagination__pages')
        next_page(pagination_box)
        time.sleep(2)
    #     press_next = True


if __name__ == "__main__":
    main()
    print(1)
