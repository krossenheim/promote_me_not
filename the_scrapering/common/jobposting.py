import pickle
import datetime
from the_scrapering.common.common import create_destination_folders
from the_scrapering.linked_in.site_info import WEBSITE_ALIAS as LINKED_IN_WEBSITE_ALIAS
from langdetect import detect
from os.path import isfile


class JobPosting:
    def __init__(self, job_id,
                 title,
                 posted_date,
                 company_name,
                 applicants,
                 workplace_type,
                 company_size,
                 company_type,
                 full_time_or_other,
                 job_description,
                 site_name,
                 location,
                 entry_level):
        self.job_id = job_id
        self.retrieval_date = datetime.datetime.now()

        self.posted_date = posted_date

        self.title = title
        self.company_name = company_name
        self.applicants = applicants
        self.workplace_type = workplace_type
        self.company_size = company_size
        self.company_type = company_type
        self.full_time_or_other = full_time_or_other
        self.description = job_description
        self.location = location
        assert isinstance(site_name, str)
        self.site_name = site_name
        self.entry_level = entry_level
        # Consider assigning the job posting's language here instead of checking it elsewhere
        self.__language_posted = None

    def __str__(self):
        return f"{self.title} - {self.job_id}"

    def __lt__(self, other):
        return self.posted_date < other.posted_date

    @property
    def language_posted(self):
        if self.__language_posted is None and self.description != '':
            self.__language_posted = detect(self.description)
            print(f"Language: {self.__language_posted} -- Now saving {self.job_id}.")
            self.save(verbose=False, overwrite=True)
        return self.__language_posted

    @property
    def url(self):
        if self.site_name == LINKED_IN_WEBSITE_ALIAS:
            return f'https://www.linkedin.com/jobs/view/{self.job_id}'
        raise RuntimeError(f"Site {self.site_name} not implemented. on this model")

    @property
    def __save_to_path(self) -> str:
        return f'../jobs/{self.site_name}/{self.job_id}'

    def save(self, verbose=True, overwrite=False) -> None:
        if not overwrite and isfile(self.__save_to_path):
            print(f"Not saving {self.job_id} as it already exists.")
            return
        if verbose:
            print(f"saving {self}")
        try:
            with open(self.__save_to_path, "wb") as f:
                pickle.dump(self, f)
        except FileNotFoundError:
            create_destination_folders(self.site_name)
