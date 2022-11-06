import json

from django.shortcuts import render
from django.views.generic import ListView
from django_tables2 import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect,csrf_exempt

from .filters import JobPostingFilter
from .models import JobPosting
from .tables import JobPostingTable


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


@csrf_exempt
def toggle_marked_attribute(request):
    if request.method != "POST":
        return JsonResponse({'Status': 'Failure', "Message": "Bad request."})
    data = json.loads(request.body)
    job = JobPosting.objects.filter(pk=data['pk'])
    if not job:
        return JsonResponse({'Status': 'Failure', "Message": "No such pk."})
    job[0].marked = not job[0].marked
    job[0].save()
    return JsonResponse({'Status': 'Success', "Message": "Toggled attribute marked.."})


# Create your views here.
def main(request):
    return render(request, 'display_jobs/empty.html', {})


def manual_jobposting_view(request):
    f = JobPostingFilter(request.GET, queryset=JobPosting.objects.all().order_by("-retrieval_date"))
    context = {
        'column_names': [name for name in JobPosting()],
        'filter': f,
    }

    return render(request, 'display_jobs/job_posting_handmade.html', context)
