from django.db import models
from django.utils import timezone
from softdelete.models import SoftDeleteObject
from langdetect import detect


# Create your models here.
class JobPosting(SoftDeleteObject, models.Model):
    job_id = models.IntegerField(unique=True, default=0)
    retrieval_date = models.DateTimeField(default=timezone.now)
    first_seen = models.DateTimeField(default=timezone.now)
    posted_date = models.DateTimeField(default=timezone.now)
    applicants = models.IntegerField(null=True)
    title = models.CharField(max_length=255, null=True)
    workplace_type = models.CharField(max_length=255, null=True)
    company_size = models.CharField(max_length=255, null=True)
    company_name = models.CharField(max_length=255, null=True)
    company_type = models.CharField(max_length=255, null=True)
    full_time_or_other = models.TextField(max_length=255, null=True)
    description = models.TextField(null=True)
    location = models.CharField(max_length=255, null=True)
    site_scraped_from = models.CharField(max_length=255, null=True)
    entry_level = models.CharField(max_length=255, null=True)
    language_detected = models.CharField(max_length=2, null=True)

    @property
    def language_posted(self):
        if not self.language_detected:
            self.language_detected = detect(self.description) if self.description else '00'
            self.save()
        return self.language_detected

    def update(self, other):
        if other.applicants != self.applicants:
            print(f"{self} has received {other.applicants - self.applicants} new applicants, saving.")
            applicants_change = JobPostingApplicantChange(
                offer_related=self,
                previous_applicants=self.applicants,
                previous_date=self.retrieval_date,
                current_applicants=other.applicants,
                current_date=other.retrieval_date,

            )
            applicants_change.save()
        self.retrieval_date = timezone.now()

        self.applicants = other.applicants
        self.save()

    def save(self, *args, **kwargs):
        if not self.first_seen:
            print(f"Found new entry: {self}")
            self.first_seen = timezone.now()
            self.retrieval_date = timezone.now()

        super(JobPosting, self).save(*args, **kwargs)

    def __repr__(self):
        return f"{self.title} - {self.job_id}"

    def __str__(self):
        return self.__repr__()


class JobPostingApplicantChange(SoftDeleteObject, models.Model):
    offer_related = models.ForeignKey(JobPosting, on_delete=models.DO_NOTHING)
    previous_applicants = models.IntegerField()
    previous_date = models.DateTimeField()
    current_applicants = models.IntegerField()
    current_date = models.DateTimeField()
