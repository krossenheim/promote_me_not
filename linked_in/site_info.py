import os
from pathlib import Path

LOGIN = 'https://www.linkedin.com/login'
JOBS = "https://www.linkedin.com/jobs/search/?geoId=91000000&keywords=django&start=0"
HOME = 'https://www.linkedin.com'
WEBSITE_ALIAS = "linked_in"

geo_ids = {
    'denmark': '104514075',
    'norway': '103819153',
    'spain': '105646813',
    'netherlands': '102890719',
    'sweden': '105117694',


}
search_terms = "django,python,software,developer,automation,testing,game,api,flask".split(',')
bases = (
    'https://www.linkedin.com/jobs/search/?currentJobId=3328383281&f_E=2&geoId=__GEOID__&keywords=',
    'https://www.linkedin.com/jobs/search/?currentJobId=3328383281&geoId=__GEOID__&keywords='
)
SEARCH_LINKS = list()
for search_term in search_terms:
    for base in bases:
        for country, code in geo_ids.items():
            search_link = f"{base}{search_term}".replace("__GEOID__", code)
            SEARCH_LINKS.append(search_link)

print("-")