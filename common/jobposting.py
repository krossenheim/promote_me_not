import pickle
import datetime
from common.common import create_destination_folders
from linked_in.site_info import WEBSITE_ALIAS as LINKED_IN_WEBSITE_ALIAS


class JobPosting:
    def __init__(self, job_id, title, posted_date, company_name, applicants, workplace_type, company_size,
                 job_description, site_name, location):
        self.job_id = job_id
        self.retrieval_date = datetime.datetime.now()

        self.posted_date = posted_date

        self.title = title
        self.company_name = company_name
        self.applicants = applicants
        self.workplace_type = workplace_type
        self.company_size = company_size
        self.description = job_description
        self.location = location
        assert isinstance(site_name, str)
        self.site_name = site_name
        # Consider assigning the job posting's language here instead of checking it elsewhere

    def __str__(self):
        return f"{self.title} - {self.job_id}"

    @property
    def url(self):
        if self.site_name == LINKED_IN_WEBSITE_ALIAS:
            return f'https://www.linkedin.com/jobs/view/{self.job_id}'
        raise RuntimeError(f"Site {self.site_name} not implemented. on this model")

    @property
    def __save_to_path(self) -> str:
        return f'../jobs/{self.site_name}/{self.job_id}'

    def save(self) -> None:
        print(f"saving {self}")
        try:
            with open(self.__save_to_path, "wb") as f:
                pickle.dump(self, f)
        except FileNotFoundError:
            create_destination_folders(self.site_name)
