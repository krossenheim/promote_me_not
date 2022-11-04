from django.test import TestCase
from display_jobs.models import JobPosting


class JobPostingTestCase(TestCase):
    def setUp(self):
        JobPosting.objects.create(title='Test')

    def test_get_attributenames_ordered_for_table(self) -> None:
        invalid_names = list()
        post = JobPosting.objects.get(title='Test')
        for item in post.wanted_attributes_for_ordered_table:
            if item not in post.__dict__.keys():
                invalid_names.append(item)
        if invalid_names:
            raise AttributeError(f"The list of attributes on JobPosting has invalid attribute names :{invalid_names}")

