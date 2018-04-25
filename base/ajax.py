from .utils import json, Codec, Filter
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms import modelform_factory
from django.template.loader import render_to_string
import operator


@csrf_exempt
def get_collection(request):
    queryset = Filter(app_label=request.POST.get('app_label'),
                      model_name=request.POST.get('model')).filter_by_json(request.POST.get('filters', None))
    return HttpResponse(json.dumps([x.to_json() for x in queryset], cls=Codec),
                        content_type='application/json')


@csrf_exempt
def get_object(request):
    instance = Filter(app_label=request.POST.get('app_label'),
                      model_name=request.POST.get('model')
                      ).get_instance(int(request.POST.get('id')))
    return HttpResponse(json.dumps(instance.to_json(), cls=Codec), content_type='application/json')


@csrf_exempt
def object_update(request):
    result = ""
    instance = Filter(app_label=request.POST.get('app_label'),
                      model_name=request.POST.get('model')
                      ).get_instance(int(request.POST.get('id')))
    data = request.POST.get('data', None)
    if data:
        for k, v in json.loads(str(data).replace("'", "\"")).items():
            setattr(instance, k, v)
        instance.save()
    return HttpResponse(json.dumps({'result': result, 'intance': instance.to_json()}, cls=Codec),
                        content_type='application/json')


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
def autocomplete(request):
    result = []
    type_search = '{}__like'
    type_ = request.GET.get('type_search',None)
    if type_ :
       if type_ == "1" :
        type_search = '{}__istartswith'
       elif type_ == "2" :
        type_search = '{}__iendswith'

    columns = request.GET.get('column_name').split(",")
    columns = [(type_search.format(column), request.GET.get('term')) for column in columns]
    queryset = Filter(app_label=request.GET.get('app_label'),
                      model_name=request.GET.get('model')
                      ).filter_by_list(columns, operator.or_)
    for q in queryset:
        result.append({'obj': q.to_json(),
                       'label': str(q),
                       'value': q.to_json()[column]})
    return HttpResponse(json.dumps(result, cls=Codec), content_type="application/json")


@csrf_exempt
def get_html_form(request, form=None):
    resp = {}
    if request.method == "GET":
        data = {"method": "POST"}
        filter = Filter(app_label=request.GET.get('app_label'),
                        model_name=request.GET.get('model'))
        data['fields'] = request.GET.get('fields')
        action = request.GET.get('action')
        if action:
            data['action'] = action
        else:
            data['action'] = '/admin/ajax/get_html_form/'
        data['app_label'] = filter.app_label
        data['model'] = filter.model_name
        id = request.GET.get('id', None)
        if not form:
            form = modelform_factory(filter.model, fields=data['fields'].split("-"))
            if id:
                form = form(instance=filter.get_instance(int(id)))
                data['id'] = id
            else:
                form = form()
        data['form'] = form
        return HttpResponse(render_to_string("ajax/form.html", data, request))
    if request.method == "POST":
        filter = Filter(app_label=request.POST.get('app_label'),
                        model_name=request.POST.get('model'))
        form = modelform_factory(filter.model, fields=request.POST.get('fields').split("-"))
        id = request.POST.get('id', None)
        if id:
            form = form(request.POST, request.FILES or None, instance=filter.get_instance(int(id)))
        else:
            form = form(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            obj = form.instance
            resp = {"result": "actualizado", "object": obj.to_json()}
        else:
            err = ""
            for e in form.errors:
                err += "error en el campo " + str(e)
            resp = {'error': err}
    return HttpResponse(json.dumps(resp), content_type="application/json")
