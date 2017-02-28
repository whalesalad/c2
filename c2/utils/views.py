import random

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import get_resolver
from django.template.response import TemplateResponse

from restless.http import JSONResponse

def landing(request, template):
    return TemplateResponse(request, template, context={
        'page': { 'title': 'Home', 'class': 'home' }
    })

def home(request, template):
    return TemplateResponse(request, template, context={
        'page': { 'title': 'Home', 'class': 'home' }
    })


@login_required
def dashboard(request, template):
    return TemplateResponse(request, template, context={
        'page': { 'title': 'Home', 'class': 'home' }
    })


@login_required
def visualsearch(request, template):
    return TemplateResponse(request, template, context={
        'page': { 'title': 'Home', 'class': 'home' }
    })


@login_required
def api_landing(request, template):
    page = { 'title': 'Welcome to the API', 'class': 'api' }

    if request.is_json:
        return JSONResponse(page['title'])

    return TemplateResponse(request, template, context={
        'page': page,
    })

def ping(request):
    """
    Simple Ping endpoint for ELB to hit.

    """
    return JSONResponse({ 'bear': 'claw' })