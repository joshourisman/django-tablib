django-tablib: tablib for Django
================================

django-tablib is a helper library for Django that allows Django models to be used to generate tablib datasets with introspection of the fields on the models if no headers are provided. If headers are provided they can reference any attribute, fields, properties, or methods on the model.

Overview
--------
`django_tablib.ModelDataset()`
    A wrapper around tablib.Dataset that handles the conversion of Django QuerySets to a format that tablib can work with.

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
        class Meta:
	    model = MyModel
	    fields = [
	        'id',
		'myfield1',
		'myfield2',
	    ]

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
        class Meta:
	    model = MyModel
	    fields = [
                'boring_field_name',
		'id',
		'some_other_field',
	    ]
	    headers = {
	        'boring_field_name': 'Awesome Descriptive Column Header',
	    }

    data = MyModelDataset()

Add a new row: ::

    >>> data.append(MyModel(**values))

Add a new column: ::

    >>> data.append(col=['header', 'value1', 'value2' ... 'valuen'])

Delete a row: ::

    >>> del data[1]

For everything else see the tablib documentation!
