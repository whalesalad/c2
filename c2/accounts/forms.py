import pprint

from django import forms

from c2.accounts.models import User, Team

class UserForm(forms.ModelForm):
    full_name = forms.CharField(max_length=65, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email', 'full_name', )

    def clean(self):
        remove = []
        for key, val in self.cleaned_data.iteritems():
            if not val:
                remove.append(key)

        for key in remove:
            del self.cleaned_data[key]

        return self.cleaned_data

    def save(self, identifier=None, commit=True):
        parts = self.cleaned_data["full_name"].split(' ')
        first_name, last_name = parts[0], parts[1]

        if identifier:
            data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": self.cleaned_data["email"],
                "password": "YUn!!CE7a$"
            }

            q = User.objects.create_user(**data)
        else:
            q = super(UserForm, self).save(False)

        if commit:
            q._identifier = identifier
            q.save()

        return q

class UpdateUserForm(forms.ModelForm):
    full_name = forms.CharField(max_length=65, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email', 'full_name', )

    def clean(self):
        remove = []
        for key, val in self.cleaned_data.iteritems():
            if not val:
                remove.append(key)

        for key in remove:
            del self.cleaned_data[key]

        return self.cleaned_data

    def save(self, commit=True):
        q = super(UpdateUserForm, self).save(False)

        if self.cleaned_data.get('full_name'):
            q.full_name = self.cleaned_data['full_name']

        if commit:
           q.save()

        return q


class TeamForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ('name', 'max_sensors', )


class TeamUpdateForm(forms.ModelForm):

    class Meta:
        model = Team
        fields = ('is_active', 'max_sensors', )
