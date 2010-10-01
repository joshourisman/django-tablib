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

Add a new row (adding of columns is not supported): ::

    >>> data.append(MyModel(**values)

Delete a row: ::

    >>> del data[1]

For everything else see the tablib documentation!
