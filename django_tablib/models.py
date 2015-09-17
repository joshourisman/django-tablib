# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

import six
from copy import deepcopy

from .base import BaseDataset
from .fields import Field


class NoObjectsException(Exception):
    pass


class DatasetOptions(object):
    def __init__(self, options=None):
        self.model = getattr(options, 'model', None)
        self.queryset = getattr(options, 'queryset', None)
        self.fields = getattr(options, 'fields', [])
        self.exclude = getattr(options, 'exclude', [])


class DatasetMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = {}
        declared_fields = {}

        try:
            parents = [b for b in bases if issubclass(b, ModelDataset)]
            parents.reverse()

            for p in parents:
                parent_fields = getattr(p, 'base_fields', {})

                for field_name, field_object in parent_fields.items():
                    attrs['base_fields'][field_name] = deepcopy(field_object)
        except NameError:
            pass

        for field_name, obj in attrs.copy().items():
            if issubclass(type(obj), Field):
                field = attrs.pop(field_name)
                declared_fields[field_name] = field

        attrs['base_fields'].update(declared_fields)
        attrs['declared_fields'] = declared_fields

        new_class = super(DatasetMetaclass, cls).__new__(cls, name,
                                                         bases, attrs)
        opts = new_class._meta = DatasetOptions(getattr(new_class,
                                                        'Meta', None))

        if new_class.__name__ == 'ModelDataset':
            return new_class

        if not opts.model and not opts.queryset:
            raise NoObjectsException("You must set a model or non-empty "
                                     "queryset for each Dataset subclass")
        if opts.queryset is not None:
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


class ModelDataset(six.with_metaclass(DatasetMetaclass, BaseDataset)):

    def __init__(self, *args, **kwargs):
        included = [field.name for field in self.model._meta.fields]
        if self._meta.fields:
            included = filter(lambda x: x in self._meta.fields, included)
        if self._meta.exclude:
            included = filter(lambda x: x not in self._meta.exclude, included)

        self.fields = dict((field, Field()) for field in included)

        self.fields.update(deepcopy(self.base_fields))

        self.header_dict = dict(
            (field.header or name, field.attribute or name)
            for name, field in self.fields.items())

        self.header_list = self.header_dict.keys()
        self.attr_list = [self.header_dict[h] for h in self.header_list]
        super(ModelDataset, self).__init__(*args, **kwargs)
