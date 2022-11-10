import django_filters
from .models import JobPosting
from django.utils import timezone
from django.forms import widgets
from django.db.models import Q


class JobPostingFilter(django_filters.FilterSet):
    title_contains = django_filters.CharFilter(field_name='title',
                                               lookup_expr='contains')
    title_not_contains = django_filters.CharFilter(
        method='title_not_contains_method',
        label='Title not contains',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains = django_filters.CharFilter(
        method='description_does_contain',
        label='Description contains',
        widget=widgets.TextInput(attrs={'placeholder': 'Does contain'})
    )
    description_contains1 = django_filters.CharFilter(
        method='description_does_contain',
        label='Description contains',

        widget=widgets.TextInput(attrs={'placeholder': 'Does contain'})
    )
    description_contains2 = django_filters.CharFilter(
        method='description_does_contain',
        label='Description contains',

        widget=widgets.TextInput(attrs={'placeholder': 'Does contain'})
    )
    description_contains_not = django_filters.CharFilter(
        method='description_does_not_contain',
        label='Description does not contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not1 = django_filters.CharFilter(
        method='description_does_not_contain',
        label='Description does not contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not2 = django_filters.CharFilter(
        method='description_does_not_contain',
        label='Description does not contain',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    posted_date = django_filters.DateFilter(field_name='posted_date', lookup_expr='gt')

    language = django_filters.CharFilter(field_name='language_detected',
                                         lookup_expr='contains',
                                         initial='en')

    workplace_type_contains = django_filters.CharFilter(
        method='workplace_type_contains_method',
        initial='Remote,',
        label='Workplace contains',
        widget=widgets.TextInput(attrs={'placeholder': 'Does not contain'})
    )
    linkedin_id = django_filters.NumberFilter(
        field_name='job_id',
        lookup_expr='iexact'
    )

    applicants = django_filters.NumberFilter(
        field_name='applicants',
        lookup_expr='lte'
    )

    include_marked = django_filters.BooleanFilter(
        method='include_marked_method',
        initial='No',
        label='Include marked items')

    scraped_minutes_ago = django_filters.NumberFilter(
        method='scraped_minutes_ago_method',
        widget=widgets.TextInput(attrs={'placeholder': 'Minutes back known'})
    )

    def include_marked_method(self, qs, name, value):
        print(value)
        return qs.exclude(Q(marked=True) if not value else Q())

    def title_not_contains_method(self, qs, name, value):
        queryset_condition = Q()
        for item in value.split(","):
            queryset_condition = queryset_condition | Q(title__icontains=item)
        return qs.exclude(queryset_condition)

    def workplace_type_contains_method(self, qs, name, value):
        queryset_condition = Q()
        for item in value.split(","):
            queryset_condition = queryset_condition | Q(workplace_type__icontains=item)
        return qs.filter(queryset_condition)

    def description_does_contain(self, qs, name, value):
        queryset_condition = Q()
        for item in value.split(","):
            queryset_condition = queryset_condition | Q(description__icontains=item)
        return qs.filter(queryset_condition)

    def description_does_not_contain(self, qs, name, value):
        queryset_condition = Q()
        for item in value.split(","):
            queryset_condition = queryset_condition | Q(description__icontains=item)
        return qs.exclude(queryset_condition)

    def scraped_minutes_ago_method(self, qs, name, value):
        value = int(round(value))
        return qs.filter(retrieval_date__range=(timezone.now() - timezone.timedelta(minutes=value), timezone.now()))

    class Meta:
        model = JobPosting
        fields = tuple()
