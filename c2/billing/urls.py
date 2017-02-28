from django.conf.urls import patterns, url

urlpatterns = patterns('c2.billing.views',
    url(r'^$', 'index', {}, name='billing-index'),
    url(r'^logout/?$', 'logout_view', {}, name='billing-logout'),
    url(r'^teams/new/?$', 'new_team', {}, name='new-team'),
    url(r'^teams/(?P<identifier>[^/]+)/members/?$', 'team_members', {}, name='team-members'),
    url(r'^teams/(?P<identifier>[^/]+)/?$', 'team_detail', {}, name='team-detail'),
    url(r'^teams/(?P<identifier>[^/]+)/new/?$', 'new_team_member', {}, name='new-team-member'),
)
