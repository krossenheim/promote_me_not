class JobPosting:
    def __init__(self, job_id, title, posted_date, company_name, applicants, workplace_type, company_size,
                 job_description):
        self.job_id = job_id
        self.title = title
        self.posted_date = posted_date
        self.company_name = company_name
        self.applicants = applicants
        self.workplace_type = workplace_type
        self.company_size = company_size
        self.job_description = job_description

    def __str__(self):
        return f"{self.title} - {self.posted_date}"
