from django import get_version
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

from django_tablib.datasets import SimpleDataset
from django_tablib.base import mimetype_map


def tablib_export_action(modeladmin, request, queryset, format="xls"):
    """
    Allow the user to download the current filtered list of items

    :param format:
        One of the formats supported by tablib (e.g. "xls", "csv", "html",
        etc.)
    """

    dataset = SimpleDataset(queryset, headers=None)
    filename = '%s.%s' % (
        smart_str(modeladmin.model._meta.verbose_name_plural), format)

    response_kwargs = {}
    key = 'content_type' if get_version().split('.')[1] > 6 else 'mimetype'
    response_kwargs[key] = mimetype_map.get(format, 'application/octet-stream')

    response = HttpResponse(getattr(dataset, format), **response_kwargs)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


def xls_export_action(*args, **kwargs):
    return tablib_export_action(format="xls", *args, **kwargs)
xls_export_action.__doc__ = tablib_export_action.__doc__
xls_export_action.short_description = _("Export to Excel")


def csv_export_action(*args, **kwargs):
    return tablib_export_action(format="csv", *args, **kwargs)
csv_export_action.__doc__ = tablib_export_action.__doc__
csv_export_action.short_description = _("Export to CSV")
