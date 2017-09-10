import os
import xlwt
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse

import pdfkit

def render_to_pdf(template_src, context_dict):
    print("render_to_pdf: Start rendering PDF")
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context_dict)

    pwd = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css = pwd + '/static/dtracking/css/bootstrap.css'
    print("render_to_pdf: Loading Template")
    pdfkit.from_string(html, 'out.pdf', css=css)
    pdf = open("out.pdf")
    print("render_to_pdf: PDF Rendered")
    response = HttpResponse(pdf.read(), content_type='application/pdf')
    pdf.close()
    return response

def render_to_excel(filename, data):
        book = xlwt.Workbook(encoding='utf8')
        sheet = book.add_sheet(filename)
        default_style = xlwt.Style.default_style
        for r, d in enumerate(data):
            for c in range(0, len(d)):
                sheet.write(r, c, d[c], style=default_style)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename='+filename+'.xls'
        book.save(response)
        return response