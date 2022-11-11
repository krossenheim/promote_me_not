base_url = "https://www.eurotechjobs.com/job_search/keyword/"

keywords = 'python,django,software,developer,backend'.split(',')

SEARCH_URLS = [f"{base_url}{item}" for item in keywords]