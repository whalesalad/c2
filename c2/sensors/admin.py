import pprint

from django.contrib import admin, messages
from django.conf.urls import url
from django.utils import timezone

from c2.sensors.models import *

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'team_name', 'uuid', 'created', 'modified', )
    list_filter = ('team', )

    def team_name(self, obj):
        return obj.team.name
    team_name.short_description = 'Team'

@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'uuid', 'name', 'is_user', 'team', )
    list_filter = ('uuid', 'name', 'is_user', 'team', )
