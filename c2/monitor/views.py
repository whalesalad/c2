from django.template.response import TemplateResponse
from django.contrib.admin.views.decorators import staff_member_required

from c2.advisories.models import Advisory
from c2.advisories.presenters import AdvisoryPresenter 

from restless.http import JSONResponse

@staff_member_required
def advisories(request):
    advisories = Advisory.objects.prefetch_related('sensor__team')[:40]

    return JSONResponse(AdvisoryPresenter(advisories).serialized)

@staff_member_required
def monitor(request, template):
    return TemplateResponse(request, template, context={
        'page': { 'title': 'Home', 'class': 'home' }
    })