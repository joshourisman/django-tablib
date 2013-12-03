from django.test import TestCase

from django_tablib import ModelDataset, Field

from .models import TestModel


class DjangoTablibTestCase(TestCase):
    def test_model_dataset(self):
        class TestModelDataset(ModelDataset):
            class Meta:
                model = TestModel

        data = TestModelDataset()

        self.assertEqual(len(data.headers), 2)
        self.assertTrue('id' in data.headers)
        self.assertTrue('field1' in data.headers)

    def test_fields(self):
        class TestModelDataset(ModelDataset):
            fields = ['field1']

            class Meta:
                model = TestModel

        data = TestModelDataset()

        self.assertEqual(len(data.headers), 1)
        self.assertTrue('id' not in data.headers)
        self.assertTrue('field1' in data.headers)

    def test_headers(self):
        class TestModelDataset(ModelDataset):
            fields = ['field1']
            headers = {'field1': 'Field 1'}

            class Meta:
                model = TestModel

        data = TestModelDataset()

        self.assertEqual(len(data.headers), 1)
        self.assertTrue('id' not in data.headers)
        self.assertTrue('field1' not in data.headers)
        self.assertTrue('Field 1' in data.headers)

    def test_declarative_fields(self):
        class TestModelDataset(ModelDataset):
            field1 = Field()

            class Meta:
                model = TestModel

        data = TestModelDataset()

        self.assertEqual(len(data.headers), 1)
        self.assertTrue('id' not in data.headers)
        self.assertTrue('field1' in data.headers)
