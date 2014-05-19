from __future__ import absolute_import
from collections import OrderedDict

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.db.models.loading import get_model
from django.views.generic import ListView

from .base import mimetype_map
from .datasets import SimpleDataset


def export(request, queryset=None, model=None, headers=None, format='xls',
           filename='export'):
    if queryset is None:
        queryset = model.objects.all()

    dataset = SimpleDataset(queryset, headers=headers)
    filename = '%s.%s' % (filename, format)
    if not hasattr(dataset, format):
        raise Http404
    response = HttpResponse(
        getattr(dataset, format),
        mimetype=mimetype_map.get(format, 'application/octet-stream')
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


def generic_export(request, model_name=None):
    """
    Generic view configured through settings.TABLIB_MODELS

    Usage:
        1. Add the view to ``urlpatterns`` in ``urls.py``::
            url(r'export/(?P<model_name>[^/]+)/$', "django_tablib.views.generic_export"),
        2. Create the ``settings.TABLIB_MODELS`` dictionary using model names
           as keys the allowed lookup operators as values, if any::

           TABLIB_MODELS = {
               'myapp.simple': None,
               'myapp.related': {'simple__title': ('exact', 'iexact')},
           }
        3. Open ``/export/myapp.simple`` or
           ``/export/myapp.related/?simple__title__iexact=test``
    """

    if model_name not in settings.TABLIB_MODELS:
        raise Http404()

    model = get_model(*model_name.split(".", 2))
    if not model:
        raise ImproperlyConfigured(
            "Model %s is in settings.TABLIB_MODELS but"
            " could not be loaded" % model_name)

    qs = model._default_manager.all()

    # Filtering may be allowed based on TABLIB_MODELS:
    filter_settings = settings.TABLIB_MODELS[model_name]
    filters = {}

    for k, v in request.GET.items():
        try:
            # Allow joins (they'll be checked below) but chop off the trailing
            # lookup operator:
            rel, lookup_type = k.rsplit("__", 1)
        except ValueError:
            rel = k
            lookup_type = "exact"

        allowed_lookups = filter_settings.get(rel, None)

        if allowed_lookups is None:
            return HttpResponseBadRequest(
                "Filtering on %s is not allowed" % rel
            )
        elif lookup_type not in allowed_lookups:
            return HttpResponseBadRequest(
                "%s may only be filtered using %s"
                % (k, " ".join(allowed_lookups)))
        else:
            filters[str(k)] = v

    if filters:
        qs = qs.filter(**filters)

    return export(request, model=model, queryset=qs)


class BaseExportView(ListView):
    # Default file name
    filename = 'export'
    # Lookup name for format in url or GET, not used if default format is set
    format_name = 'format'
    # Default format if lookups fail
    format_default = 'csv'
    # Columns to expert, either a name or a (name, accessor) tuple, e.g. ('user', 'user__username')
    columns = []
    # Internal, used to store column names and accessors while keeping order
    _ordered_columns = OrderedDict()

    def __init__(self, *args, **kwargs):
        """
        Call parent class constructors and build ordered dict of column names and accessors
        """
        super(BaseExportView, self).__init__(*args, **kwargs)
        for column in self.columns:
            if isinstance(column, basestring):
                header = column
                accessor = column
            else:
                header = column[0]
                accessor = column[1]
            self._ordered_columns[header] = accessor

    def get_headers(self):
        """
        Return an array containing headers
        """
        return self._ordered_columns.keys()

    def get_accessors(self):
        """
        Return an array containing the accessors
        """
        return self._ordered_columns.values()

    def get_format(self):
        """
        Return the export format
        """
        format = self.kwargs.get(self.format_name, None)
        if not format:
            format = self.request.GET.get(self.format_name, None)
        if not format:
            format = self.format_default
        return format

    def render_to_cell(self, row, column):
        """
        Render a value
        """
        accessor = self._ordered_columns[column]
        value = row[accessor]
        renderer = getattr(self, 'render_%s' % column, None)
        if callable(renderer):
            cell = renderer(value=value, row=row, column=column, accessor=accessor)
        else:
            cell = value
        return cell

    def render_to_response(self, context, **kwargs):
        """
        Render the response
        """
        format = self.get_format()
        accessors = self.get_accessors()
        data = Dataset()
        data.headers = self.get_headers()
        for row in self.get_queryset().values(*accessors):
            cells = []
            for column in self._ordered_columns:
                cells.append(self.render_to_cell(row, column))
            data.append(cells)
        response = HttpResponse(
            getattr(data, format),
            mimetype=mimetype_map.get(format, 'application/octet-stream')
        )
        response['Content-Disposition'] = 'attachment; filename=%s.%s' % (self.filename, format)
        return response

