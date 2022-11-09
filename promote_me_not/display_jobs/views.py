import json

from django.shortcuts import render
from django.views.generic import ListView
from django_tables2 import SingleTableView, SingleTableMixin
from django_filters.views import FilterView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt

from .filters import JobPostingFilter
from .models import JobPosting
from .tables import JobPostingTable
import time


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


def standardJsonResponse(status: str = "", message: str = "", payload: dict = None):
    rv = {
        'Status': status,
        'Message': message,
        'Payload': dict() if payload is None else payload
    }
    return JsonResponse(rv)


@csrf_exempt
def toggle_marked_attribute(request):
    if request.method != "POST":
        return standardJsonResponse(status="Failure", message="Bad request.")
    data = json.loads(request.body)
    job = JobPosting.objects.filter(pk=data['pk'])
    if not job:
        return standardJsonResponse(status="Failure", message="No such job id")
    job[0].marked = not job[0].marked
    job[0].save()
    return standardJsonResponse(status='Success',
                                message='Toggle attiribute marked.',
                                payload={'marked_value_now': job[0].marked})

@csrf_exempt
def toggle_favourited_attribute(request):
    if request.method != "POST":
        return standardJsonResponse(status="Failure", message="Bad request.")
    data = json.loads(request.body)
    job = JobPosting.objects.filter(pk=data['pk'])
    if not job:
        return standardJsonResponse(status="Failure", message="No such job id")
    job[0].favourited = not job[0].favourited
    job[0].save()
    return standardJsonResponse(status='Success',
                                message='Toggle attiribute favourited.',
                                payload={'favourited_value_now': job[0].favourited})


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
