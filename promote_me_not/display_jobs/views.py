from django.shortcuts import render
from django.views.generic import ListView
from .models import JobPosting
from .tables import JobPostingTable
from django_tables2 import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
from .filters import JobPostingFilter


class JobPostingListView(ListView):
    model = JobPosting
    template_name = 'display_jobs/job_posting_list.html'


class JobPostingTableView(SingleTableView):
    model = JobPosting
    template_name = 'display_jobs/job_posting_table.html'
    table_class = JobPostingTable


class JobPostingFilterView(SingleTableMixin, FilterView):
    table_class = JobPostingTable
    model = JobPosting
    template_name = 'display_jobs/job_posting_table_filter.html'

    filterset_class = JobPostingFilter


# Create your views here.
def main(request):
    return render(request, 'display_jobs/empty.html', {})


def manual_jobposting_view(request):
    f = JobPostingFilter(request.GET, queryset=JobPosting.objects.all())
    context = {
        'column_names' : [name for name in JobPosting()],
        'filter': f,
    }

    return render(request, 'display_jobs/job_posting_handmade.html', context)
