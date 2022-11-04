import django_filters
from .models import JobPosting
from django.utils import timezone
from django.forms import widgets
from django.db.models import Q


class JobPostingFilter(django_filters.FilterSet):
    title_contains = django_filters.CharFilter(field_name='title',
                                               lookup_expr='contains')
    description_contains = django_filters.CharFilter(field_name='description',
                                                     lookup_expr='contains')
    description_contains1 = django_filters.CharFilter(field_name='description',
                                                      lookup_expr='contains')
    description_contains2 = django_filters.CharFilter(field_name='description',
                                                      lookup_expr='contains')
    description_contains4 = django_filters.CharFilter(field_name='description',
                                                      lookup_expr='contains')
    description_contains_not = django_filters.CharFilter(
        method='description_does_not_contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not1 = django_filters.CharFilter(
        method='description_does_not_contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not2 = django_filters.CharFilter(
        method='description_does_not_contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not3 = django_filters.CharFilter(
        method='description_does_not_contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )

    posted_date = django_filters.DateFilter(field_name='posted_date', lookup_expr='gt')

    language = django_filters.CharFilter(field_name='language_detected',
                                         lookup_expr='contains',
                                         initial='en')

    worplace_type = django_filters.CharFilter(field_name='workplace_type',
                                              lookup_expr='iexact',
                                              initial='Remote')
    linkedin_id = django_filters.NumberFilter(
        field_name='job_id',
        lookup_expr='iexact'
    )

    scraped_minutes_ago = django_filters.NumberFilter(
        method='scraped_minutes_ago_method',
        widget=widgets.TextInput(attrs={'placeholder': 'Minutes back known'})
    )

    def description_does_not_contain(self, qs, name, value):
        return qs.exclude(description__contains=value)

    def scraped_minutes_ago_method(self, qs, name, value):
        value = int(round(value))
        return qs.filter(retrieval_date__range=(timezone.now() - timezone.timedelta(minutes=value), timezone.now()))

    class Meta:
        model = JobPosting
        fields = tuple()
