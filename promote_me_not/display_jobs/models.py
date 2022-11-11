from typing import Any, Generator

from django.db import models
from django.utils import timezone
from softdelete.models import SoftDeleteObject
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


# Create your models here.
class JobPosting(SoftDeleteObject, models.Model):
    job_id = models.IntegerField(default=0)
    retrieval_date = models.DateTimeField(default=timezone.now)
    first_seen = models.DateTimeField(default=None)
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
    marked = models.BooleanField(default=False)
    favourited = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self.wanted_attributes_for_ordered_table = "entry_level,marked,favourited,title,applicants,location,first_seen,workplace_type,full_time_or_other,retrieval_date".split(
            ",")
        super().__init__(*args, **kwargs)

    def __iter__(self):
        for item in self.get_pretty_names_for_wanted_attributes_ordered_table:
            yield item

    @property
    def joburl(self):
        if self.site_scraped_from == 'itijobsai':
            return f"https://itjobs.ai/Finland/job/{self.job_id}"
        if self.site_scraped_from == 'linked_in':
            return f"https://www.linkedin.com/jobs/view/{self.job_id}"
        if self.site_scraped_from == 'eurotechjobs':
            return f"https://www.eurotechjobs.com/job_display/{self.job_id}/doesntmatterweirdsite"



    @property
    def get_pretty_names_for_wanted_attributes_ordered_table(self) -> list:
        rv = list()
        for item in self.wanted_attributes_for_ordered_table:
            temp = item.split("_")
            rv_append = " ".join([item.capitalize() for item in temp])
            rv.append(rv_append)
        return rv

    @property
    def get_attributes_ordered_for_table(self) -> list:
        rv = [self.__getattribute__(item) for item in self.wanted_attributes_for_ordered_table]
        return rv

    def detect_description_language(self):
        try:
            self.language_detected = detect(self.description) if self.description else '00'
        except LangDetectException:
            self.language_detected = '00'

    @property
    def language_posted(self):
        if not self.language_detected or self.language_detected is None:
            self.detect_description_language()
            self.save()
        return self.language_detected

    def update(self, other):
        print(f"{self} has received {other.applicants - self.applicants} new applicants, saving.")
        applicants_change = JobPostingApplicantChange(
            previous_title=self.title,
            current_title=other.title,
            offer_related=self,
            previous_applicants=self.applicants,
            previous_date=self.retrieval_date,
            current_applicants=other.applicants,
            current_date=other.retrieval_date,
            previous_location=self.location,
            current_location=other.location

        )
        applicants_change.save()
        self.retrieval_date = timezone.now()
        self.applicants = other.applicants
        self.location = other.location
        self.description = other.description

        self.save()

    def save(self, *args, **kwargs):
        if not self.first_seen:
            print(f"New entry: {self}, posted {timezone.now() - self.posted_date} ago")
            self.first_seen = timezone.now()
            self.retrieval_date = timezone.now()

        super(JobPosting, self).save(*args, **kwargs)

    def __repr__(self):
        return f"{self.title} - {self.job_id}"

    def __str__(self):
        return self.__repr__()


class JobPostingApplicantChange(SoftDeleteObject, models.Model):
    previous_title = models.CharField(max_length=255, blank=True)
    current_title = models.CharField(max_length=255, blank=True)
    offer_related = models.ForeignKey(JobPosting, on_delete=models.DO_NOTHING)
    previous_applicants = models.IntegerField()
    previous_date = models.DateTimeField()
    current_applicants = models.IntegerField()
    current_date = models.DateTimeField()
    previous_location = models.CharField(max_length=255, blank=True)
    current_location = models.CharField(max_length=255, blank=True)


class GeneratedUsername():
    firstname = models.CharField(max_length=255, blank=True)
    lastname = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
