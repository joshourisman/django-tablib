from __future__ import absolute_import

import datetime
import tablib

from django.template.defaultfilters import date
from django.utils.encoding import smart_unicode

class NoObjectsException(Exception):
    pass

class DatasetOptions(object):
    def __init__(self, options=None):
        self.model = getattr(options, 'model', None)
        self.queryset = getattr(options, 'queryset', None)

class DatasetMetaclass(type):
    def __new__(cls, name, bases, attrs):
        try:
            parents = [b for b in bases if issubclass(b, ModelDataset)]
        except NameError:
            parents = None
        new_class = super(DatasetMetaclass, cls).__new__(cls, name,
                                                         bases, attrs)
        if not parents:
            return new_class

        opts = new_class._meta = DatasetOptions(getattr(new_class,
                                                        'Meta', None))

        if not opts.model and not opts.queryset:
            raise NoObjectsException("You must set a model or non-empty "
                                     "queryset for each Dataset subclass")
        if opts.queryset:
            queryset = opts.queryset
            model = queryset.model
            new_class.queryset = queryset
            new_class.model = model
        else:
            model = opts.model
            queryset = model.objects.all()
            new_class.model = model
            new_class.queryset = queryset
        
        return new_class

class BaseDataset(tablib.Dataset):
    def __init__(self):
        data = map(self._getattrs, self.queryset)
        super(BaseDataset, self).__init__(headers=self.header_list, *data)

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
        for attr in self.attr_list:
            attr = self._cleanval(getattr(obj, attr), attr)
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

class ModelDataset(BaseDataset):
    __metaclass__ = DatasetMetaclass

    def __init__(self, *args, **kwargs):
        if self.fields:
            fields = self.fields
        else:
            fields = [field.name for field in model._meta.fields]
        self.attr_list = fields
        if self.headers:
            header_dict = self.headers
            header_list = [self.headers.get(field, field) for field in fields]
        else:
            header_dict = None
            header_list = fields
        self.header_dict = header_dict
        self.header_list = header_list
        super(ModelDataset, self).__init__(*args, **kwargs)
        
