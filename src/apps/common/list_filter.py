# implement it for phenomenon time
# https://docs.djangoproject.com/en/2.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter


from datetime import date

from django.contrib import admin
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from psycopg2.extras import DateTimeTZRange

from apps.utils.time import UTC_P0100


class DateRangeRangeFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'phenomenon time'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'phenomenon_time'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        today = date.today()
        this_monday = today - timedelta(days=today.weekday())
        next_monday = this_monday + timedelta(weeks=1)
        prev_monday = this_monday - timedelta(weeks=1)
        this_monday = this_monday.strftime('%Y-%m-%d')
        next_monday = next_monday.strftime('%Y-%m-%d')
        prev_monday = prev_monday.strftime('%Y-%m-%d')
        this_week = this_monday + '--' + next_monday
        last_week = prev_monday + '--' + this_monday
        return (
            (this_week, 'this week'),
            (last_week, 'last week'),
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
        dt_from, dt_to = list(map(
            lambda p: datetime.combine(
                parse(p),
                datetime.min.time()
            ).replace(tzinfo=UTC_P0100),
            v.split('--')
        ))
        dt_range = DateTimeTZRange(dt_from, dt_to)

        return queryset.filter(
            phenomenon_time_range__contained_by=dt_range
        )
