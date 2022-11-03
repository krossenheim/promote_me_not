import django_filters
from .models import JobPosting
from django.forms.widgets import TextInput


class JobPostingFilter(django_filters.FilterSet):
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
        widget=TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not1 = django_filters.CharFilter(
        method='description_does_not_contain',
        widget=TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not2 = django_filters.CharFilter(
        method='description_does_not_contain',
        widget=TextInput(attrs={'placeholder': 'Does not contain'})
    )
    description_contains_not3 = django_filters.CharFilter(
        field_name='Not contains',
        widget=TextInput(attrs={'placeholder': 'Does not contain'})
    )

    def description_does_not_contain(self, qs, name, value):
        return qs.exclude(description__contains=value)

    class Meta:
        model = JobPosting
        fields = tuple()
