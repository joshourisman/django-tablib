# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import django
from distutils.version import LooseVersion
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import Http404


from django_tablib.base import mimetype_map
from django_tablib.views import export

from . import actions as django_tablib_actions

try:
    # Removed in Django 1.6; default to stdlib.
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper

INVALID_EXPORT_FORMAT_ERROR_MSG = (
    "{0} is not a valid export format, "
    "please choose from the following options: {1}")


class TablibAdmin(admin.ModelAdmin):
    change_list_template = 'tablib/change_list.html'
    formats = []
    headers = None
    export_filename = 'export'
    # enable Export to _format_ admin actions by default, this allows to export
    # only selected items.
    enable_admin_actions = True
    export_encoding = 'utf-8'

    def __init__(self, *args, **kwargs):
        for export_format in self.formats:
            if export_format not in mimetype_map:
                raise ValueError(INVALID_EXPORT_FORMAT_ERROR_MSG.format(
                    export_format, ', '.join(mimetype_map.keys())))
        super(TablibAdmin, self).__init__(*args, **kwargs)

    def get_info(self):
        """
        Helper method to get model info in a form of (app_label, model_name).
        Avoid deprecation warnings and failures with different Django versions.
        """
        if LooseVersion(django.get_version()) < LooseVersion('1.7.0'):
            info = self.model._meta.app_label, self.model._meta.module_name
        else:
            info = self.model._meta.app_label, self.model._meta.model_name
        return info

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^tablib-export/(?P<export_format>\w+)/$',
                wrap(self.tablib_export),
                name='{0}_{1}_tablib_export'.format(*self.get_info())),
        ]
        urlpatterns += super(TablibAdmin, self).get_urls()
        return urlpatterns

    def tablib_export(self, request, export_format):
        if export_format not in self.formats:
            raise Http404
        queryset = self.get_tablib_queryset(request)
        filename = datetime.datetime.now().strftime(self.export_filename)
        return export(request, queryset=queryset, model=self.model,
                      headers=self.headers, file_type=export_format,
                      filename=filename, encoding=self.export_encoding)

    def get_tablib_queryset(self, request):
        # allow other admin clases to override change list view,
        # taken from django ModelAdmin
        ChangeList = self.get_changelist(request)

        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = (self.get_search_fields(request)
                         if hasattr(self, 'get_search_fields')
                         else self.search_fields)

        cl = ChangeList(
            request,
            self.model,
            list_display,
            list_display_links,
            list_filter,
            self.date_hierarchy,
            search_fields,
            self.list_select_related,
            self.list_per_page,
            self.list_max_show_all,
            self.list_editable,
            self,
        )
        return cl.get_queryset(request)

    def changelist_view(self, request, extra_context=None):
        context = {'request': request}
        urls = []
        for export_format in self.formats:
            urls.append(
                (export_format, reverse(
                    'admin:{0}_{1}_tablib_export'.format(*self.get_info()),
                    kwargs={'export_format': export_format}),))
        context['urls'] = urls
        context.update(extra_context or {})

        return super(TablibAdmin, self).changelist_view(request, context)

    def get_actions(self, request):
        actions = super(TablibAdmin, self).get_actions(request)
        if not self.enable_admin_actions:
            return actions
        export_actions = {}

        # build export actions
        for export_format in self.formats:
            action_func_name = '{0}_export_action'.format(export_format)
            if not hasattr(django_tablib_actions, action_func_name):
                continue
            # get action and it's attributes
            action_func = getattr(django_tablib_actions, action_func_name)
            short_description = getattr(action_func, 'short_description',
                                        action_func_name)
            export_actions[action_func_name] = (action_func, action_func_name,
                                                short_description)
        # super actions are more preferable
        export_actions.update(actions)
        return export_actions
