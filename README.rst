django-tablib: tablib for Django
================================

django-tablib is a helper library for Django that allows Django models to be used to generate tablib datasets with introspection of the fields on the models if no headers are provided. If headers are provided they can reference any attribute, fields, properties, or methods on the model.

Overview
--------
`django_tablib.Dataset()`
    A wrapper around tablib.Dataset that handles the conversion of Django QuerySets to a format that tablib can work with.

Usage
-----

Create a tablib Dataset from a Django QuerySet, automatically introspecting all fields from the model: ::

    from myapp.models import MyModel

    data = django_tablib.Dataset(MyModel.objects.all())

Create a tablib Dataset from a Django QuerySet with a custom list of headers: ::

    from myapp.models import MyModel

    headers = ['id', 'myfield1', 'myfield2']
    data = django_tablib.Dataset(MyModel.objects.all(), headers=headers)

Create a tablib Dataset from a Django QuerySet with a dictionary mapping custom headers to attributes of your Django objects: ::

    from myapp.models import MyModel

    data = django_tablib.Dataset(MyModel.objects.all(), headers = {
        'Awesome Descriptive Column Header': 'boring_field_name',
    })

Add a new row: ::

    >>> data.append(MyModel(**values))

Add a new column: ::

    >>> data.append(col=['header', 'value1', 'value2' ... 'valuen'])

Delete a row: ::

    >>> del data[1]

For everything else see the tablib documentation!

Django Integration
------------------

django_tablib now provides a generic Django view to automatically export your
querysets to an Excel spreadsheet. In your urls.py::

    (r'^export/$', 'django_tablib.views.export', {
        'model': MyModel,
    })

If you have many models to export you may prefer use the generic export view:

#. Add the view to ``urlpatterns`` in ``urls.py``::

    url(r'export/(?P<model_name>[^/]+)/$', "django_tablib.views.generic_export"),

#. Create the ``settings.TABLIB_MODELS`` dictionary using lower-case model
   names in "app.model" format as keys and the permitted `field lookups
   <http://docs.djangoproject.com/en/dev/ref/models/querysets/#field-lookups>`_
   or ``None`` as values::

       TABLIB_MODELS = {
           'myapp.simple': None,
           'myapp.related': {'simple__title': ('exact', 'iexact')},
       }

#. Open ``/export/myapp.simple`` or
   ``/export/myapp.related/?simple__title__iexact=test``
