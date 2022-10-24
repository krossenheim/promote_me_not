from django.db import models
import datetime

# Create your models here.
class JobPosting(models.Model):
    job_id = models.IntegerField(null=True, blank=True, unique=True)
    retrieval_date = models.DateTimeField(null=True, blank=True)
    posted_date = models.DateTimeField(null=True, blank=True)
    applicants = models.IntegerField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    workplace_type = models.TextField(null=True, blank=True)
    company_size = models.TextField(null=True, blank=True)
    company_name = models.TextField(null=True, blank=True)
    company_type = models.TextField(null=True, blank=True)
    full_time_or_other = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    site_scraped_from = models.TextField(null=True, blank=True)
    entry_level = models.TextField(null=True, blank=True)
    language_of_description = models.CharField(max_length=2, null=True, blank=True)


    def update(self,other):
        print(f"Updating {self}")
        self.retrieval_date = datetime.datetime.now()
        self.applicants = other.applicants
        self.save()

    def __repr__(self):
        return f"{self.title} - {self.job_id}"

    def __str__(self):
        return self.__repr__()
