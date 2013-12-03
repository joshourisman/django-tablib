from django.test import TestCase

from django_tablib import ModelDataset

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
