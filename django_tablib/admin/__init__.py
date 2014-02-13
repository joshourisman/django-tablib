import datetime
import django

from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.core.urlresolvers import reverse
from django.http import Http404

from django_tablib.base import mimetype_map
from django_tablib.views import export

try:
    # Removed in Django 1.6; default to stdlib.
    from functools import update_wrapper
except ImportError:
    from django.utils.functional import update_wrapper


class TablibAdmin(admin.ModelAdmin):
    change_list_template = 'tablib/change_list.html'
    formats = []
    headers = None
    export_filename = 'export'

    def __init__(self, *args, **kwargs):
        for format in self.formats:
            if format not in mimetype_map:
                msg = "%s is not a valid export format, please choose" \
                    " from the following options: %s" % (
                        format,
                        ', '.join(mimetype_map.keys()),
                    )
                raise ValueError(msg)
        super(TablibAdmin, self).__init__(*args, **kwargs)

    def get_urls(self):
        try:
            from django.conf.urls import patterns, url
        except ImportError:  # Django <1.4
            from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.module_name

        urlpatterns = patterns(
            '',
            url(r'^tablib-export/(?P<format>\w+)/$',
                wrap(self.tablib_export),
                name='%s_%s_tablib_export' % info),
        )
        urlpatterns += super(TablibAdmin, self).get_urls()
        return urlpatterns

    def tablib_export(self, request, format):
        if format not in self.formats:
            raise Http404
        queryset = self.get_tablib_queryset(request)
        filename = datetime.datetime.now().strftime(self.export_filename)
        return export(request, queryset=queryset, model=self.model,
                      headers=self.headers, format=format, filename=filename)

    def get_tablib_queryset(self, request):
        cl_args = (request, self.model, )
        if django.VERSION >= (1, 5):
            list_display = self.get_list_display(request)
            list_display_links = self.get_list_display_links(request, list_display)
            list_filter = self.get_list_filter(request)

            cl_args += (list_display, list_display_links,
                        list_filter, self.date_hierarchy, self.search_fields,
                        self.list_select_related, self.list_per_page,
                        self.list_max_show_all, self.list_editable, self,)
            return ChangeList(*cl_args).get_query_set(request)
        elif django.VERSION >= (1, 4):
            list_display = self.get_list_display(request)
            list_display_links = self.get_list_display_links(request, list_display)

            cl_args += (list_display, list_display_links,
                        self.list_filter, self.date_hierarchy, self.search_fields,
                        self.list_select_related, self.list_per_page,
                        self.list_max_show_all, self.list_editable, self,)
            return ChangeList(*cl_args).get_query_set(request)
        else:
            cl_args += (list_display, list_display_links,
                        self.list_filter, self.date_hierarchy, self.search_fields,
                        self.list_select_related, self.list_per_page,
                        self.list_editable, self,)
            return ChangeList(*cl_args).get_query_set()

    def changelist_view(self, request, extra_context=None):
        info = self.model._meta.app_label, self.model._meta.module_name
        context = {'request': request}
        urls = []
        for format in self.formats:
            urls.append(
                (format, reverse(
                    'admin:%s_%s_tablib_export' % info,
                    kwargs={'format': format}),))
        context['urls'] = urls
        context.update(extra_context or {})

        return super(TablibAdmin, self).changelist_view(request, context)
