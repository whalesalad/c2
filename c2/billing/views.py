import ujson as json
from restless.models import serialize

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout

from c2.accounts.models import Team, Membership, User
from c2.accounts.presenters import MembershipPresenter, UserPresenter
from c2.accounts.forms import UserForm, TeamForm, TeamUpdateForm

@staff_member_required
def index(request, template='billing/index.html'):
    teams = Team.objects.all()

    return TemplateResponse(request, template, context={
        'teams': teams
    })

def logout_view(request, template="billing/logout.html"):
    logout(request)
    return HttpResponseRedirect("/billing")

@staff_member_required
def new_team(request, template='billing/new_team.html'):
    if request.method == 'POST':
        form = TeamForm(request.POST)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/billing/teams/%s' % (form.instance.identifier, ))

    return TemplateResponse(request, template)

@staff_member_required
def team_detail(request, identifier, template='billing/team_detail.html'):
    team = Team.objects.get(identifier=identifier)

    if request.method == 'POST':
        form = TeamUpdateForm(request.POST, instance=team)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/billing')
        else:
            return HttpResponse('Error updating account information', status=500)

    return TemplateResponse(request, template, context={
        'team': team,
        'sensors': team.sensors.count()
    })

@staff_member_required
def new_team_member(request, identifier, template='billing/new_team_member.html'):
    team = Team.objects.get(identifier=identifier)

    if request.method == 'POST':
        form = UserForm(request.POST)

        if form.is_valid():
            form.save(identifier=identifier)
            return HttpResponseRedirect("/billing/teams/%s" % (identifier, ))
        else:
            return HttpResponse("An error occurred while adding the user to the account.  Please try again later", status=500)

    return TemplateResponse(request, template, context= {
        "identifier": identifier
    })

@staff_member_required
def team_members(request, identifier, template="billing/team_members.html"):
    team = Team.objects.get(identifier=identifier)

    members = []
    for member in team.memberships.prefetch_related('user').all():
            u = UserPresenter(member.user).serialized
            u['membership'] = MembershipPresenter(member).serialized
            members.append(u)

    return TemplateResponse(request, template, context= {
        "identifier": identifier,
        "members": members
    })
