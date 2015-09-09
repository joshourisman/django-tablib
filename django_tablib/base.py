# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import tablib

from django.template.defaultfilters import date
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

mimetype_map = {
    'xls': 'application/vnd.ms-excel',
    'csv': 'text/csv',
    'html': 'text/html',
    'yaml': 'text/yaml',
    'json': 'application/json',
}


def get_content_type(export_format, encoding='utf-8'):
    """
    Simple wrapper to ensure that content type is set with respect to encoding
    """
    return '{0}; charset={1}'.format(
        mimetype_map.get(export_format, 'application/octet-stream'),
        encoding)


class BaseDataset(tablib.Dataset):

    def __init__(self):
        data = map(self._getattrs, self.queryset)
        super(BaseDataset, self).__init__(headers=self.header_list, *data)

    def _cleanval(self, value, attr):
        if callable(value):
            value = value()
        elif value is None or tablib.compat.unicode(value) == "None":
            value = ""

        if isinstance(value, bool):
            value = _("Y") if value else _("N")
        elif isinstance(value, (datetime.date, datetime.datetime)):
            value = date(value, 'SHORT_DATE_FORMAT')

        return force_text(value)

    def _getattrs(self, obj):
        attrs = []
        for attr in self.attr_list:
            if callable(attr):
                attr = self._cleanval(attr(obj), attr)
            else:
                if hasattr(obj, 'get_{0}_display'.format(attr)):
                    value = getattr(obj, 'get_{0}_display'.format(attr))()
                else:
                    value = getattr(obj, attr)
                attr = self._cleanval(value, attr)
            attrs.append(attr)
        return attrs

    def append(self, *args, **kwargs):
        # Thanks to my previous decision to simply not support columns, this
        # dumb conditional is necessary to preserve backwards compatibility.
        if len(args) == 1:
            # if using old syntax, just set django_object to args[0] and
            # col to None
            django_object = args[0]
            col = None
        else:
            # otherwise assume both row and col may have been passed and
            # handle appropriately
            django_object = kwargs.get('row', None)
            col = kwargs.get('col', None)

        # make sure that both row and col are in a format that can be passed
        # straight to tablib
        if django_object is not None:
            row = self._getattrs(django_object)
        else:
            row = django_object

        super(BaseDataset, self).append(row=row, col=col)
