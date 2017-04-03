django-tablib: tablib for Django
================================

django-tablib is a helper library for Django that allows tablib datasets to be generated from Django models.

Overview
--------
`django_tablib.ModelDataset()`
    A wrapper around tablib.Dataset that handles the conversion of Django QuerySets to a format that tablib can work with in the model of Django's ModelForm and ModelAdmin.

Usage
-----

The below examples are all based on this model: ::

    from django.db import models

    class MyModel(models.Model):
        myfield1 = models.TextField()
        myfield2 = models.TextField()


Create a tablib Dataset from a Django model, automatically introspecting all fields from the model: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        class Meta:
            model = MyModel

    # This dataset will have the fields 'id', 'myfield1' and 'myfield2'.
    data = MyModelDataset()

Create a tablib Dataset from a Django model, including only certain, desired fields: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        class Meta:
            model = MyModel
            fields = ['id', 'myfield1']

    # This dataset will have the fields 'id', and 'myfield1'.
    data = MyModelDataset()

Create a tablib Dataset from a Django model, excluding certain, undesired fields: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        class Meta:
            model = MyModel
            exclude = ['myfield2']

    # This dataset will have the fields 'id', and 'myfield1'.
    data = MyModelDataset()

Create a tablib Dataset from a Django model declaratively specifying the fields to be used: ::

    from django_tablib import ModelDataset, Field
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        myfield1 = Field()
        myfield2 = Field()

        class Meta:
            model = MyModel

    # This dataset will have the fields 'id', 'myfield1' and 'myfield2'.
    data = MyModelDataset()

Create a tablib Dataset from a Django QuerySet: ::

    from django_tablib import ModelDataset
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        class Meta:
            queryset = MyModel.objects.filter(is_awesome=True)

    # This dataset will have the fields 'id', 'myfield1' and 'myfield2'.
    data = MyModelDataset()

Create a tablib Dataset from a Django model declaratively specifying fields and their headers: ::

    from django_tablib import ModelDataset, Field
    from myapp.models import MyModel

    class MyModelDataset(ModelDataset):
        myfield1 = Field(header='No More Boring Field Names!')

        class Meta:
            model = MyModel

    # This dataset will have the fields 'id',
    # 'No More Boring Field Names' and 'myfield2'.
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

django-tablib supports Django 1.8 and 1.9. 1.10 support is experimental.
Older versions might work, but have not been actively tested.
