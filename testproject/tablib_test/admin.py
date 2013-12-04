from django.contrib import admin

from django_tablib import TablibAdmin

from .models import TestModel


class TestModelAdmin(TablibAdmin):
    pass

admin.site.register(TestModel, TestModelAdmin)
