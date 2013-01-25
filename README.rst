django-tablib: tablib for Django
================================

django-tablib is a helper library for Django that allows Django models to be used to generate tablib datasets with introspection of the fields on the models if no headers are provided. If headers are provided they can reference any attribute, fields, properties, or methods on the model.

Overview
--------
`django_tablib.ModelDataset()`
    A wrapper around tablib.Dataset that handles the conversion of Django QuerySets to a format that tablib can work with in the model of Django's ModelForm and ModelAdmin.

Usage
-----

Create a tablib Dataset from a Django model, automatically introspecting all fields from the model: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        class Meta:
	    model = MyModel

    data = MyModelDataset()

Create a tablib Dataset from a Django model with a custom list of fields: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        fields = [
            'id',
            'myfield1',
            'myfield2',
        ]
        class Meta:
	    model = MyModel

    data = MyModelDataset()

Create a tablib Dataset from a Django QuerySet: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        class Meta:
	    queryset = MyModel.objects.filter(is_awesome=True)

    data = MyModelDataset()

Create a tablib Dataset from a Django model with a dictionary mapping custom headers to attributes of your Django objects: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        fields = [
            'boring_field_name',
            'id',
            'some_other_field',
        ]
        headers = {
            'boring_field_name': 'Awesome Descriptive Column Header',
        }
        class Meta:
	    model = MyModel

    data = MyModelDataset()

Add a new row: ::

    >>> data.append(MyModel(**values))

Add a new column: ::

    >>> data.append(col=['header', 'value1', 'value2' ... 'valuen'])

Delete a row: ::

    >>> del data[1]

For everything else see the tablib documentation!

Django Integration
------------------

`django_tablib.views.export`
    django_tablib provides a generic Django view to automatically export your querysets to an Excel spreadsheet. In your urls.py::

        (r'^export/$', 'django_tablib.views.export', {
            'model': MyModel,
        })

`django_tablib.views.generic_export`
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

`django_tablib.admin.TablibAdmin`
    For easy exporting of your models directly from the Django admin, django_tablib now provides a ModelAdmin subclass giving you a button to export to Excel straight from the change list::

        from django.contrib import admin
        from django_tablib.admin import TablibAdmin
        from myapp.models import MyModel
    
        class MyModelAdmin(TablibAdmin):
            formats = ['xls', 'json', 'yaml', 'csv', 'html',]
    
        admin.site.register(MyModel, MyModelAdmin)

    You can also customize which fields from ``MyModel`` are used by supplying a ``headers`` list::

        from django.contrib import admin
        from django_tablib.admin import TablibAdmin
        from myapp.models import MyModel
    
        class MyModelAdmin(TablibAdmin):
            formats = ['xls', 'json', 'yaml', 'csv', 'html',]
            headers = ['field_one', 'field_two',]
    
        admin.site.register(MyModel, MyModelAdmin)

That's it!

Compatibility
-------------

django-tablib has been tested with Django 1.4. On Django 1.5 it does throw a deprecation warning (see `issue #25`_).

.. _`issue #25`: https://github.com/joshourisman/django-tablib/issues/25
