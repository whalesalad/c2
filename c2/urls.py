import os

from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from c2.accounts.views import *
from c2.sensors.views import *
from c2.rules.views import *
from c2.advisories.views import *
from c2.stats.views import *

admin.site.site_header = 'Example Sensors Admin'
admin.site.site_title = 'Example Sensors Admin'

def playground_allowed():
    allowed_envs = ('development', 'staging', )
    return settings.DJANGO_ENV in allowed_envs

stats_patterns = patterns('',
    # Dashboard related statistics
    url(r'^assets/?$', AssetStats.as_view()),
    url(r'^events/?$', EventStats.as_view()),
    url(r'^advisories/?$', AdvisoryStats.as_view()),

    # Timeseries based statistics, backed by local REDIS
    url(r'^timeseries/assets/?$', AssetTimeseriesStats.as_view()),
    url(r'^timeseries/clusters/?$', ClusterTimeseriesStats.as_view()),
    url(r'^timeseries/events/?$', EventTimeseriesStats.as_view()),
    url(r'^timeseries/advisories/type?$', AdvisoryTimeseriesStats.as_view()),
    # url(r'^timeseries/advisories/severity?$', AdvisoryTimeseriesStats.as_view()),
)

api_patterns = patterns('',
    # User Account/Login Related URLs
    url(r'^authenticate/?$', UserLogin.as_view()),
    url(r'^keys/?$', KeyList.as_view()),
    url(r'^keys/(?P<access_key>[\w]{16,32})/?$', KeyDetail.as_view()),

    url(r'^memberships/(?P<membership_id>\d+)$', MembershipDetail.as_view()),

    url(r'^teams/?$', TeamList.as_view()),
    url(r'^teams/(?P<identifier>[-\w]+)/?$', TeamDetail.as_view()),

    url(r'^user/?$', UserDetail.as_view()),
    url(r'^user/password/?$', 'c2.accounts.views.update_password'),
    url(r'^users/?$', UserList.as_view()),

    # Application Data
    url(r'^assets/?$', CloudAssetList.as_view()),
    url(r'^clusters/?$', SensorClusterList.as_view()),
    url(r'^groups/?$', SensorGroupList.as_view()),
    url(r'^stats/?', include(stats_patterns)),

    url(r'^advisories/?$', AdvisoryList.as_view()),
    url(r'^advisories/(?P<advisory_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/?$', AdvisoryDetail.as_view()),
    url(r'^advisories/(?P<advisory_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/events/?$', AdvisoryEvents.as_view()),
    url(r'^advisories/(?P<sensor_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/tree/?$', AdvisoryProcessInfo.as_view()),

    url(r'^notifications/?$', NotificationList.as_view()),
    url(r'^notifications/(?P<advisory_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/?$', NotificationDetail.as_view()),

    url(r'^events/?$', EventsList.as_view()),
    url(r'^events/(?P<event_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/?$', EventDetail.as_view()),

    url(r'^rules/?$', RuleList.as_view()),
    url(r'^rules/(?P<rule_slug>[\w-]+)$', RuleDetail.as_view()),

    url(r'^sensors/?$', SensorList.as_view()),
    url(r'^sensors/(?P<sensor_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/advisories/?', SensorAdvisories.as_view()),
    url(r'^sensors/(?P<sensor_id>[\w]{8}(-[\w]{4}){3}-[\w]{12})/?', SensorDetail.as_view()),
)

urlpatterns = patterns('',
    url(r'^/?$', 'c2.utils.views.home', { 'template': 'index.html' }, name='home'),

    url(r'^monitor/?$', 'c2.monitor.views.monitor', {'template':'monitor/index.html'}, name='monitor'), # Internal dashboard
    url(r'^monitor/advisories/?$', 'c2.monitor.views.advisories'), #advisory json


    url(r'^ping/?$', 'c2.utils.views.ping'),                    # Used as heartbeat For ELB

    url(r'^api/',           include(api_patterns)),             # Above, the api_patterns
    url(r'^internal/',      include('c2.api.internal.urls')),   # Private/Internal API URLs only accessible inside of AWS VPC
    url(r'^admin/',         include(admin.site.urls)),          # Admin
    url(r'^billing/',       include('c2.billing.urls')),        # Billing
)

if playground_allowed():
    urlpatterns += patterns('',
        url(r'^playground/',    include('c2.playground.urls')),     # Debug/Playground
    )
