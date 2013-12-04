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
    response = HttpResponse(
        getattr(dataset, format), mimetype=mimetype_map.get(
            format, 'application/octet-stream'))
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
