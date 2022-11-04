from django.test import TestCase
from display_jobs.models import JobPosting
from display_jobs.filters import JobPostingFilter
from django.utils import timezone


class JobPostingFilterTestCase(TestCase):
    def setUp(self):
        JobPosting.objects.create(title='time filter test older than 60 mins', retrieval_date=timezone.timezone)
        JobPosting.objects.create(title='time filter test older than 30 mins')
        JobPosting.objects.create(title='time filter test younger than 30 mins')

    def test_get_attributenames_ordered_for_table(self) -> None:
        invalid_names = list()
        morethan60 = JobPosting.objects.create(title='time filter test older than 60 mins')
        morethan30 = JobPosting.objects.create(title='time filter test older than 30 mins')
        lessthan30 = JobPosting.objects.create(title='time filter test younger than 30 mins')

        for item in post.wanted_attributes_for_ordered_table:
            if item not in post.__dict__.keys():
                invalid_names.append(item)
        if invalid_names:
            raise AttributeError(f"The list of attributes on JobPosting has invalid attribute names :{invalid_names}")
