import unicodecsv
from django.http import HttpResponse, StreamingHttpResponse


class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def stream_as_csv_action(description="Stream selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """A view that streams a large CSV file."""

    def stream_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        pseudo_buffer = Echo()
        writer = unicodecsv.writer(pseudo_buffer, encoding='utf-8')

        def stream(w):
            if header:
                w.writerow(field_names)
            for obj in queryset:
                row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in
                       field_names]
                w.writerow(row)

        response = StreamingHttpResponse(stream(writer), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')
        return response

    stream_as_csv.short_description = description
    return stream_as_csv


def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """

    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % str(opts).replace('.', '_')

        writer = unicodecsv.writer(response, encoding='utf-8')
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            row = [getattr(obj, field)() if callable(getattr(obj, field)) else getattr(obj, field) for field in
                   field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = description
    return export_as_csv
