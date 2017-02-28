import string
import random

from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.html import escape

import django.contrib.auth.forms as auth_forms

from c2.accounts.models import *

def random_password():
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 12)
    return ''.join(random.choice(chars) for x in range(size))

class UserChangeForm(forms.ModelForm):
    email = forms.EmailField(label="Email")

    password = auth_forms.ReadOnlyPasswordHashField(label="Password",
        help_text="Raw passwords are not stored, so there is no way to see "
                  "this user's password, but you can change the password "
                  "using <a href=\"password/\">this form</a>.")

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password", random_password())

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = UserChangeForm
    change_password_form = auth_forms.AdminPasswordChangeForm
    change_user_password_template = None

    list_display = ('__unicode__', 'email')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),

        ('Personal info', {'fields': ('first_name', 'last_name', )}),

        ('Permissions', {'fields': ('is_staff', )}),
    )

    def get_urls(self):
        return [
            url(r'^(\d+)/password/$', self.admin_site.admin_view(self.user_change_password)),
        ] + super(UserAdmin, self).get_urls()

    def user_change_password(self, request, id, form_url=''):
        if not self.has_change_permission(request):
            raise PermissionDenied
        user = get_object_or_404(self.get_queryset(request), pk=id)
        if request.method == 'POST':
            form = self.change_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                change_message = self.construct_change_message(request, form, None)
                self.log_change(request, request.user, change_message)
                msg = 'Password changed successfully.'
                messages.success(request, msg)
                # update_session_auth_hash(request, form.user)
                return HttpResponseRedirect('..')
        else:
            form = self.change_password_form(user)

        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context = {
            'title': 'Change password: %s' % escape(user.get_username()),
            'adminForm': adminForm,
            'form_url': form_url,
            'form': form,
            'add': True,
            'change': False,
            'has_delete_permission': False,
            'has_change_permission': True,
            'has_absolute_url': False,
            'opts': self.model._meta,
            'original': user,
            'save_as': False,
            'show_save': True,
        }
        context.update(admin.site.each_context())
        return TemplateResponse(request,
            self.change_user_password_template or
            'admin/auth/user/change_password.html',
            context, current_app=self.admin_site.name)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'identifier', 'is_active', 'max_sensors')
    search_fields = ('name', 'identifier', 'is_active')
    prepopulated_fields = { 'identifier': ('name', ) }

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'team', 'user', 'role', )
    list_filter = ('role', )

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('access_key', 'team', 'name', 'is_active', 'created')
    list_filter = ('is_active', )
