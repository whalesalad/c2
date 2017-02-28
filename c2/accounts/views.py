#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import pprint
import requests

from django.contrib import auth
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from restless.views import Endpoint
from restless.models import serialize
from restless.modelviews import DetailEndpoint, ActionEndpoint
from restless.http import Http201, Http403, Http404, Http400, Http422, JSONResponse

from c2.api.utils import AuthenticatedEndpoint
from c2.accounts.forms import UpdateUserForm
from c2.accounts.models import Membership
from c2.accounts.presenters import *
from c2 import settings

KEYMASTER_HOST = settings.KEYMASTER_HOST

User = auth.get_user_model()

logger = logging.getLogger('console')


class UserList(Endpoint):
    def post(self, request):
        if request.user.is_authenticated():
            return Http403("You cannot create a new user while you're logged-in.")

        form = UpdateUserForm(request.data)

        if form.is_valid():
            user = form.save()
            response = UserPresenter(user).serialized
            response['token'] = user.fresh_token
            return Http201(response)

        return Http400(reason="The user could not be created.", details=form.errors)


class UserDetail(AuthenticatedEndpoint):
    def get(self, request):
        return UserPresenter(request.user).serialized

    def post(self, request):
        if not request.user.is_authenticated():
            return Http403("You must log in to modify your user resource.")

        user = request.user

        form = UpdateUserForm(request.data, instance=user)

        if form.is_valid():
            user = form.save()
            return UserPresenter(user).serialized

        return Http400("Derp derp.", details=form.errors)


class UserLogin(Endpoint):
    def post(self, request):
        user = None

        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if not (username and password):
            return Http400("Both a username and a password field are required for authentication.")

        user = auth.authenticate(username=username, password=password)

        if not user:
            return Http400("The username and password combination that you provided is incorrect.")

        return JSONResponse({ 'uid': user.id, 'token': user.fresh_token })


class TeamList(AuthenticatedEndpoint):
    @classmethod
    def serialize_team_with_membership(self, membership, team=None):
        if not team:
            team = membership.team

        team = TeamPresenter(team).serialized
        team['membership'] = MembershipPresenter(membership).serialized

        return team

    def get(self, request):
        memberships = request.user.memberships.all()
        teams = [TeamList.serialize_team_with_membership(m) for m in memberships]
        return serialize(teams)


class TeamDetail(AuthenticatedEndpoint):
    def get(self, request, identifier):
        try:
            membership = request.user.memberships \
                .prefetch_related('team', 'team__keys') \
                .get(team__identifier=identifier)

        except Membership.DoesNotExist:
            return Http403("You cannot access this team.")

        team = TeamList.serialize_team_with_membership(membership)

        # Add all the members to the team object
        team['members'] = []
        for member in membership.team.memberships.prefetch_related('user').all():
            u = UserPresenter(member.user).serialized
            u['membership'] = MembershipPresenter(member).serialized
            team['members'].append(u)

        # Add all the keys to the team object
        team['keys'] = APIKeyPresenter(membership.team.keys.all()).serialized

        return team


class MembershipDetail(DetailEndpoint):
    model = Membership
    lookup_field = 'membership_id'

    def get_instance(self, request, membership_id):
        membership = Membership.objects.get(pk=membership_id)

        if request.user.id == membership.user_id:
            your_membership = membership
        else:
            your_membership = Membership.objects.get(user_id=request.user.id, team_id=membership.team_id)

        if your_membership:
            return (membership, your_membership)
        else:
            return Http403("You cannot access this team membership.")

    def get(self, request, membership_id):
        theirs, yours = self.get_instance(request, membership_id)
        return MembershipPresenter(theirs).serialized

    def put(self, request, membership_id):
        """
        A membership object does not need to ever be modified. The only
        value that can be changed is whether or not is_admin is true.
        For simplicity, a PUT in this case will simply toggle the value.

        """
        theirs, yours = self.get_instance(request, membership_id)

        if yours.is_admin:
            theirs.is_admin = not theirs.is_admin
            theirs.save()

        return MembershipPresenter(theirs).serialized

    def delete(self, request, membership_id):
        theirs, yours = self.get_instance(request, membership_id)

        if yours.is_admin:
            member_name = theirs.user.full_name
            team_name = yours.team.name
            theirs.delete()

        return JSONResponse({
            'messages': [('success', '%s was removed from %s successfully.' % (member_name, team_name))]
        })


class KeyList(AuthenticatedEndpoint):
    def get(self, request):
        identifier = request.user.team.identifier
        url = "%s/api/keys/%s" % (KEYMASTER_HOST, identifier, )
        r = requests.get(url)
        data = r.json()

        return [ key for key in data['keys'] ]

    def post(self, request):
        identifier = request.user.team.identifier

        url = "%s/api/keys/%s" % (KEYMASTER_HOST, identifier, )

        r = requests.post(url, data=request.body)
        if r.status_code == 400:
            return Http400({ "error": "Key could not be added" })

        return r.json()

class KeyDetail(AuthenticatedEndpoint):
    def delete(self, request, access_key):
        identifier = request.user.team.identifier
        url = "%s/api/keys/%s/%s" % (KEYMASTER_HOST, identifier, access_key, )
        r = requests.delete(url)

        if r.status_code == 400:
            return Http400({ "error": "Key could not be removed." })

        return "Key Successfully Removed"

    def get(self, request, access_key):
        identifier = request.user.team.identifier
        url = "%s/api/keys/%s/%s" % (KEYMASTER_HOST, identifier, access_key, )
        r = requests.get(url)

        if r.status_code in [400, 404]:
            return Http400({ "error": "Could not fetch key information" })

        return r.json()

@require_POST
@csrf_exempt
def update_password(request):
    payload = json.loads(request.body)

    password = payload.get('password', None)
    password_confirm = payload.get('password_confirm', None)

    unique = set(filter(None, [password, password_confirm]))

    if len(unique) > 1:
        return Http422("The two passwords provided do not match.")

    if len(unique) == 1:
        if len(password) < 7:
            return Http422('Your password must be at least 7 characters long, you entered %s.' % len(password))

        request.user.set_password(password)
        request.user.save()

        return JSONResponse({
            'messages': [('success', 'Your password has been updated successfully.')]
        })

    return Http422('Enter your new password, then verify it one more time confirmation field.')


