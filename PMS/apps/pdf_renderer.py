from io import BytesIO

import xhtml2pdf.pisa as pisa
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template


class Render:

    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response,
                                default_css=open(settings.STATIC_ROOT + '/pisa-css/test.css', 'r').read())
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)
