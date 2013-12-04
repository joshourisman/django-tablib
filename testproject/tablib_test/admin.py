from django.contrib import admin

from django_tablib import TablibAdmin
from django_tablib.admin.actions import xls_export_action, csv_export_action

from .models import TestModel


class TestModelAdmin(TablibAdmin):
    actions = [xls_export_action, csv_export_action]

admin.site.register(TestModel, TestModelAdmin)
