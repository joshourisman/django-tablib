import datetime
import tablib

from django.template.defaultfilters import date
from django.utils.encoding import smart_unicode

class Dataset(tablib.Dataset):
    def __init__(self, queryset, headers=None):
        if headers is None:
            fields = queryset.model._meta.fields
            self.headers_list = [field.name for field in fields]
        else:
            self.headers_list = headers
        data = map(self._getattrs, queryset)
        super(Dataset, self).__init__(headers=self.headers_list, *data)

    def _cleanval(self, value, attr):
        if callable(value):
            value = value()
        t = type(value)
        if t is str:
            return value
        elif t in [datetime.date, datetime.datetime]:
            return date(value, 'SHORT_DATE_FORMAT')
        else:
            return smart_unicode(value).encode('ascii', 'xmlcharrefreplace')
    
    def _getattrs(self, obj):
        attrs = []
        for attr in self.headers_list:
            attr = self._cleanval(getattr(obj, attr), attr)
            attrs.append(attr)
        return attrs
        
