from __future__ import absolute_import

from .base import BaseDataset


class SimpleDataset(BaseDataset):
    def __init__(self, queryset, headers=None, encoding='utf-8'):
        self.queryset = queryset
        self.encoding = encoding
        if headers is None:
            # We'll set the queryset to include all fields including calculated
            # aggregates using the same names as a values() queryset:
            v_qs = queryset.values()
            headers = []
            headers.extend(v_qs.query.extra_select)
            headers.extend(v_qs.field_names)
            headers.extend(v_qs.query.aggregate_select)

            self.header_list = headers
            self.attr_list = headers
        elif isinstance(headers, dict):
            self.header_dict = headers
            self.header_list = self.header_dict.keys()
            self.attr_list = self.header_dict.values()
        elif isinstance(headers, (tuple, list)):
            self.header_list = headers
            self.attr_list = headers
        super(SimpleDataset, self).__init__()
