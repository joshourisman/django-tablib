from django.http import HttpResponse

from core import Dataset

def export(request, queryset=None, model=None, headers=None):
    if queryset is None:
        queryset = model.objects.all()

    dataset = Dataset(queryset, headers=headers)
    filename = 'export.xls'
    response = HttpResponse(dataset.xls, mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
    
