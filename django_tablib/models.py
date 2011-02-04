from __future__ import absolute_import

from .base import BaseDataset

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

class ModelDataset(BaseDataset):
    __metaclass__ = DatasetMetaclass

    fields = None
    headers = None

    def __init__(self, *args, **kwargs):
        if self.fields is not None:
            fields = self.fields
        else:
            fields = [field.name for field in self.model._meta.fields]
        self.attr_list = fields
        if self.headers is not None:
            header_dict = self.headers
            header_list = [self.headers.get(field, field) for field in fields]
        else:
            header_dict = None
            header_list = fields
        self.header_dict = header_dict
        self.header_list = header_list
        super(ModelDataset, self).__init__(*args, **kwargs)
        
