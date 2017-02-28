from django.conf.urls import patterns, url

urlpatterns = patterns('c2.playground.views',
    url(r'^$', 'index', {}, name='playground-index'),
    url(r'^delay/?$', 'advisory_delay', {}, name='playground-delay'),

    url(r'^advisories/?$', 'advisory_list', {}, name='advisory-list'),
    url(r'^advisories/(?P<advisory_id>\d+)/?$', 'advisory_detail', {}, name='advisory-detail'),

    url(r'^snapshots/?$', 'snapshot_list', { 'template': 'playground/sensor_snapshot_list.html' }, name='playground-snapshots'),
    url(r'^snapshots/(?P<identifier>[-\w]+)/(?P<uuid>[\w]{8}(-[\w]{4}){3}-[\w]{12})/(?P<key>[-\w]+)?/?$', 'snapshot_detail', { 'template': 'playground/sensor_snapshot_detail.html' }, name='playground-snapshot-detail'),

    url(r'^events/?$', 'event_list', { 'template': 'playground/event_list.html' }, name='playground-event-list'),
    url(r'^events/(?P<key_filter>\w+)/?$', 'event_list', { 'template': 'playground/event_list.html' }),
    # url(r'^events/(?P<event_id>\d+)/?$', EventDetail.as_view()),
)
