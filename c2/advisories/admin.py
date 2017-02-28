from django.contrib import admin

from c2.advisories.models import *

ADVISORY_TIME_FORMAT = '%b %d, %Y - %H:%M:%S (%Z)'

@admin.register(Advisory)
class AdvisoryAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'team', 'rule', 'created', )
    list_filter = ('rule', 'team')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'advisory', 'unread', )
    list_filter = ('user', 'advisory')
