from . import views
from django.urls import path

urlpatterns = [
    path('list/', views.JobPostingListView.as_view()),
    path('table/', views.JobPostingTableView.as_view()),
    path('filtered/', views.JobPostingFilterView.as_view()),
    path('man/', views.manual_jobposting_view)

]
