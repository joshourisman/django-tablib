# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse, HttpResponseBadRequest

try:
    from django.apps import apps
    get_model = apps.get_model
except ImportError:
    from django.db.models.loading import get_model

from .base import get_content_type
from .datasets import SimpleDataset


def export(request, queryset=None, model=None, headers=None, file_type='xls',
           filename='export', encoding='utf-8'):
    if queryset is None:
        queryset = model.objects.all()

    dataset = SimpleDataset(queryset, headers=headers)
    filename = '{0}.{1}'.format(filename, file_type)
    if not hasattr(dataset, file_type):
        raise Http404

    response_kwargs = {
        'content_type': get_content_type(file_type, encoding=encoding)
    }

    response = HttpResponse(getattr(dataset, file_type), **response_kwargs)

    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
        filename)
    return response


def generic_export(request, model_name=None):
    """
    Generic view configured through settings.TABLIB_MODELS

    Usage:
        1. Add the view to ``urlpatterns`` in ``urls.py``::
            url(r'export/(?P<model_name>[^/]+)/$',
                "django_tablib.views.generic_export"),
        2. Create the ``settings.TABLIB_MODELS`` dictionary using model names
           as keys the allowed lookup operators as values, if any::

           TABLIB_MODELS = {
               'myapp.simple': None,
               'myapp.related': {'simple__title': ('exact', 'iexact')},
           }
        3. Open ``/export/myapp.simple`` or
           ``/export/myapp.related/?simple__title__iexact=test``
    """

    if model_name not in settings.TABLIB_MODELS:
        raise Http404()

    model = get_model(*model_name.split(".", 2))
    if not model:
        raise ImproperlyConfigured(
            "Model {0} is in settings.TABLIB_MODELS but"
            " could not be loaded".format(model_name))

    qs = model._default_manager.all()

    # Filtering may be allowed based on TABLIB_MODELS:
    filter_settings = settings.TABLIB_MODELS[model_name]
    filters = {}

    for k, v in request.GET.items():
        try:
            # Allow joins (they'll be checked below) but chop off the trailing
            # lookup operator:
            rel, lookup_type = k.rsplit("__", 1)
        except ValueError:
            rel = k
            lookup_type = "exact"

        allowed_lookups = filter_settings.get(rel, None)

        if allowed_lookups is None:
            return HttpResponseBadRequest(
                "Filtering on {0} is not allowed".format(rel)
            )
        elif lookup_type not in allowed_lookups:
            return HttpResponseBadRequest(
                "{0} may only be filtered using {1}".format(
                    k, " ".join(allowed_lookups)))
        else:
            filters[str(k)] = v

    if filters:
        qs = qs.filter(**filters)

    return export(request, model=model, queryset=qs)
