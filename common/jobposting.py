class JobPosting:
    def __init__(self, posted_date, applicants, workplace_type, company_size, job_description):
        self.posted_date = posted_date
        self.applicants = applicants
        self.workplace_type = workplace_type
        self.company_size = company_size
        self.job_description = job_description

    def __str__(self):
        return self.posted_date