from django.test import TestCase

from django_tablib import ModelDataset, Field

from .models import TestModel


class DjangoTablibTestCase(TestCase):
    def setUp(self):
        TestModel.objects.create(field1='value')

    def test_declarative_fields(self):
        class TestModelDataset(ModelDataset):
            field1 = Field(header='Field 1')
            field2 = Field(attribute='field1')

            class Meta:
                model = TestModel

        data = TestModelDataset()

        self.assertEqual(len(data.headers), 3)
        self.assertTrue('id' in data.headers)
        self.assertFalse('field1' in data.headers)
        self.assertTrue('field2' in data.headers)
        self.assertTrue('Field 1' in data.headers)

        self.assertEqual(data[0][0], data[0][1])
