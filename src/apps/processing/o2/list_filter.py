# coding=utf-8
# implement it for phenomenon time
# https://docs.djangoproject.com/en/2.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter


from django.contrib import admin
from psycopg2.extras import NumericRange


class AgeRangeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'phenomenon time'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'age'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('8--19', '8–18 years'),
            ('19--26', '19–25 years'),
            ('26--36', '26–35 years'),
            ('36--56', '36–55 years'),
            ('56--', '56+ years'),
            ('0--', 'Any'),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        v = self.value()
        if v == None:
            return queryset
        age_from, age_to = list(map(
            lambda p: None if p=='' else int(p),
            v.split('--')
        ))
        age_range = NumericRange(age_from, age_to)

        return queryset.filter(
            age__contained_by=age_range
        )
