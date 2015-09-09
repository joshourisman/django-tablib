# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import get_version
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from django_tablib.datasets import SimpleDataset
from django_tablib.base import mimetype_map


def tablib_export_action(modeladmin, request, queryset, file_type="xls"):
    """
    Allow the user to download the current filtered list of items

    :param file_type:
        One of the formats supported by tablib (e.g. "xls", "csv", "html",
        etc.)
    """

    dataset = SimpleDataset(queryset, headers=None)
    filename = '{0}.{1}'.format(
        smart_str(modeladmin.model._meta.verbose_name_plural), file_type)

    response_kwargs = {}
    key = 'content_type' if get_version().split('.')[1] > 6 else 'mimetype'
    response_kwargs[key] = mimetype_map.get(
        file_type, 'application/octet-stream')

    response = HttpResponse(getattr(dataset, file_type), **response_kwargs)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(
        filename)
    return response


def xls_export_action(*args, **kwargs):
    return tablib_export_action(file_type="xls", *args, **kwargs)
xls_export_action.__doc__ = tablib_export_action.__doc__
xls_export_action.short_description = _("Export to Excel")


def csv_export_action(*args, **kwargs):
    return tablib_export_action(file_type="csv", *args, **kwargs)
csv_export_action.__doc__ = tablib_export_action.__doc__
csv_export_action.short_description = _("Export to CSV")


def html_export_action(*args, **kwargs):
    return tablib_export_action(file_type="html", *args, **kwargs)
html_export_action.__doc__ = tablib_export_action.__doc__
html_export_action.short_description = _("Export to HTML")