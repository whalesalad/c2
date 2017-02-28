from django.conf.urls import patterns, url

urlpatterns = patterns('c2.api.internal.views',
    url(r'^verify_token/$', 'verify_token'),
    url(r'^verify/(?P<access_key>[A-Z0-9]{20})$', 'verify_access_key'),
)
