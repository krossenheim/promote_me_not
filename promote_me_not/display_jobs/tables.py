import django_tables2 as tables
from .models import JobPosting


class JobPostingTable(tables.Table):
    class Meta:
        model = JobPosting
        template_name = "django_tables2/bootstrap.html"
