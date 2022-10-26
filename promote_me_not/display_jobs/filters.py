import django_filters
from .models import JobPosting


class JobPostingFilter(django_filters.FilterSet):
    description_contains = django_filters.CharFilter(field_name='description',
                                                     lookup_expr='contains')
    description_contains1 = django_filters.CharFilter(field_name='description',
                                                      lookup_expr='contains')
    description_contains2 = django_filters.CharFilter(field_name='description',
                                                      lookup_expr='contains')
    description_contains4 = django_filters.CharFilter(field_name='description',
                                                      lookup_expr='contains')
    description_contains_not = django_filters.CharFilter(field_name='description',
                                                         lookup_expr='contains')
    description_contains_not1 = django_filters.CharFilter(field_name='description',
                                                          lookup_expr='contains')
    description_contains_not2 = django_filters.CharFilter(field_name='description',
                                                          lookup_expr='contains')
    description_contains_not4 = django_filters.CharFilter(field_name='description',
                                                          lookup_expr='contains')

    class Meta:
        model = JobPosting
        exclude = ('pk',)
