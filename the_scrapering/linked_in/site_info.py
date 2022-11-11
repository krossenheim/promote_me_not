import os
from pathlib import Path

LOGIN = 'https://www.linkedin.com/login'
HOME = 'https://www.linkedin.com'
WEBSITE_ALIAS = "linked_in"
JOB_TABS_CONTAINER_CLASSNAME = 'scaffold-layout__detail'
DESCRIPTION_CLASSNAME = 'jobs-unified-description__content'  # if ('jantequera' in str(Path(__file__).resolve()) or 'autom' in str(Path(__file__).resolve())) else 'jobs-description-content__text'
MINIMUM_TIME_PER_PAGE_SECONDS = 1.9
INSIGHTS_TIME_OFFSET_MAX = 3.5
geo_ids = {
    'netherlands': '102890719',
    'europe': '91000002',
    'finland': '100456013',
    'denmark': '104514075',
    'norway': '103819153',
    'switz': '106693272',
    'spain': '105646813',
    'sweden': '105117694',
    'ger': '101282230',

}
search_terms = "python,software,developer,automation engineer,automation testing,testing,game,api python,coder,flask,django".split(
    ',')
bases = (
    'https://www.linkedin.com/jobs/search/?currentJobId=3328383281&geoId=__GEOID__&keywords=',
)
SEARCH_LINKS = list()
for search_term in search_terms:
    for base in bases:
        for country, code in geo_ids.items():
            search_link = f"{base}{search_term}".replace("__GEOID__", code)
            SEARCH_LINKS.append(search_link)

print("-")
