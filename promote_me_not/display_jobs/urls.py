from . import views
from django.urls import path

urlpatterns = [
    path('list/', views.JobPostingListView.as_view()),
    path('table/', views.JobPostingTableView.as_view()),
    path('filtered/', views.JobPostingFilterView.as_view()),
    path('man/', views.manual_jobposting_view),
    path('toggle_marked/', views.toggle_marked_attribute, name = 'toggle_marked'),
    path('toggle_favourited/', views.toggle_favourited_attribute, name='toggle_favourited'),

]
