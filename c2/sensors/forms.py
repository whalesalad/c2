import json

from django import forms

from c2.sensors.models import Sensor, Cluster

class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['name', 'groups', ]


class ClusterForm(forms.ModelForm):
    class Meta:
        model = Cluster
        fields = ['name', ]