import time
from common.jobposting import JobPosting
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

url_li = "https://www.linkedin.com/jobs/search/?geoId=91000000&keywords=python&start=0"


def get_browser():
    br = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    br.set_window_size(1600, 12000)
    return br


def lk_login(br: webdriver.Chrome, u='jleonardola@gmail.com', p='lkverysecure123') -> bool:
    br.get('https://www.linkedin.com/login')
    br.find_element(By.ID, 'username').send_keys(u)
    pbox = br.find_element(By.ID, 'password')
    pbox.send_keys(p)
    pbox.send_keys(Keys.ENTER)
    return True


def zoom_out(br: webdriver.Chrome):
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


def get_job_posting(job_details: WebElement):
    posted_date = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__posted-date')
    applicants = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__applicant-count')
    workplace_type = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__workplace-type')
    company_size = job_details.find_element(By.CLASS_NAME, 'jobs-unified-top-card__job-insight')
    job_description = job_details.find_element(By.CLASS_NAME, 'jobs-description-content__text')
    job = JobPosting(posted_date, applicants, workplace_type, company_size, job_description)
    return job


def main():
    br = get_browser()
    lk_login(br)
    br.get(url_li)

    # zoom_out(br)
    # time.sleep(1)

    listings = list()

    # jobs_search_results = br.find_element(By.CLASS_NAME, 'jobs-search-results-list')

    while True:
        container = br.find_element(By.CLASS_NAME, 'scaffold-layout__list-container')
        visible_cards = container.find_elements(By.XPATH, "*")
        for n,item in enumerate(visible_cards):
            if 'Refine by title' in item.text:
                continue
            # Clicking the middle of the element sometimes hits a link instead, this avoids that.
            attempts = 5
            while True:
                try:
                    br.execute_script(f"document.getElementsByClassName('job-card-list__title')[{n}].scrollIntoView(true)")
                    item.find_element(By.CLASS_NAME, 'job-card-list__title').click()
                    break
                except Exception as e:
                    print(f"Failed on item{item.text}. Retrying in {6-attempts}")
                    time.sleep(6-attempts)
                    attempts -=1
            time.sleep(1)
            details = br.find_element(By.CLASS_NAME, 'scaffold-layout__detail')
            max_try = 4
            while True:
                if not max_try:
                    break
                try:
                    job = get_job_posting(details)
                    listings.append(job)
                    break
                except:
                    max_try -= 1

        pagination_box = br.find_element(By.CLASS_NAME, 'artdeco-pagination__pages')
        next_page(pagination_box)
        time.sleep(2)
    #     press_next = True


if __name__ == "__main__":
    main()
    print(1)
