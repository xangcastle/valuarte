from .utils import json, Codec, Filter
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelform_factory
from django.template.loader import render_to_string
from django.http import HttpResponse


@csrf_exempt
def get_object(request):
    instance = Filter(app_label=request.POST.get('app_label'),
                      model_name=request.POST.get('model')
                      ).get_instance(int(request.POST.get('id')))
    return HttpResponse(json.dumps(instance.to_json(), cls=Codec), content_type='application/json')


@csrf_exempt
def get_collection(request):
    queryset = Filter(app_label=request.POST.get('app_label'),
                      model_name=request.POST.get('model')).filter_by_json(request.POST.get('filters', None))
    return HttpResponse(json.dumps([x.to_json() for x in queryset], cls=Codec),
                        content_type='application/json')


@csrf_exempt
def autocomplete(request):
    result = []
    column = request.GET.get('column_name')
    queryset = Filter(app_label=request.GET.get('app_label'),
                      model_name=request.GET.get('model')
                      ).filter_by_list(
        [('{}__like'.format(column),
          request.GET.get('term')), ])
    for q in queryset:
        result.append({'obj': q.to_json(),
                       'label': str(q),
                       'value': q.to_json()[column]})
    return HttpResponse(json.dumps(result, cls=Codec), content_type="application/json")


@csrf_exempt
def object_execute(request):
    instance = Filter(app_label=request.POST.get('app_label'),
                      model_name=request.POST.get('model')
                      ).get_instance(int(request.POST.get('id')))
    try:
        result = getattr(instance, request.POST.get('method'))(request)
    except:
        try:
            result = getattr(instance, request.POST.get('method'))()
        except:
            result = str(getattr(instance, request.POST.get('method')))
    return HttpResponse(json.dumps({'result': result}, cls=Codec), content_type='application/json')


@csrf_exempt
def get_html_form(request, form=None):
    if request.method == "GET":
        data = {"method": "POST"}
        filter = Filter(app_label=request.GET.get('app_label'),
                        model_name=request.GET.get('model'))
        data['fields'] = request.GET.get('fields')
        data['action'] = '/admin/ajax/get_html_form/'
        data['app_label'] = filter.app_label
        data['model'] = filter.model_name
        id = request.GET.get('id', None)
        if not form:
            form = modelform_factory(filter.model, fields=data['fields'].split("-"))
            print form
            if id:
                form = form(instance=filter.get_instance(int(id)))
                data['id'] = id
            else:
                form = form()
        data['form'] = form
        return HttpResponse(render_to_string("ajax/form.html", data, request))
    if request.method == "POST":
        result = "error"
        filter = Filter(app_label=request.POST.get('app_label'),
                        model_name=request.POST.get('model'))
        form = modelform_factory(filter.model, fields=request.POST.get('fields').split("-"))
        id = request.POST.get('id', None)
        if id:
            form = form(request.POST or None, instance=filter.get_instance(int(id)))
        else:
            form = form(request.POST)
        if form.is_valid():
            form.save()
            result = "actualizado"
    return HttpResponse(json.dumps({"result": result}), content_type="application/json")


