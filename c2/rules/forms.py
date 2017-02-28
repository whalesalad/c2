from django import forms

from c2.rules.models import RuleConfiguration

class RuleConfigurationForm(forms.ModelForm):
    class Meta:
        model = RuleConfiguration
        fields = [ 'enabled', 'exclude', ]
