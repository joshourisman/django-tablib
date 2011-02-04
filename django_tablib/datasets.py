from __future__ import absolute_import

from .base import BaseDataset

class SimpleDataset(BaseDataset):
    def __init__(self, queryset, headers=None):
        self.queryset = queryset
        if headers is None:
            fields = queryset.model._meta.fields
            self.header_list = [field.name for field in fields]
            self.attr_list = self.header_list
        elif type(headers) is dict:
            self.header_dict = headers
            self.header_list = self.header_dict.keys()
            self.attr_list = self.header_dict.values()
        elif type(headers) is list:
            self.header_list = headers
            self.attr_list = headers
        super(SimpleDataset, self).__init__()
        
