from restless.http import Http403, Http404
from restless.models import serialize

from c2.api.utils import AuthenticatedEndpoint

from c2.rules.forms import RuleConfigurationForm
from c2.rules.models import Rule, RuleConfiguration, Configuration
from c2.rules.presenters import RulePresenter, RuleConfigurationPresenter

class RuleList(AuthenticatedEndpoint):

    @property
    def rules(self):
        if not getattr(self, '_rules', False):
            self._rules = Rule.objects.filter(public=True)

        return self._rules

    def get(self, request):
        configurations = []

        for r in self.rules:
            config, created = r.configurations.get_or_create(team=request.user.team)
            configurations.append(config)

        return RuleConfigurationPresenter(configurations).serialized


class RuleDetail(AuthenticatedEndpoint):
    def get(self, request, rule_slug):
        config, created = request.user.team.configurations.get_or_create(rule__slug=rule_slug)

        return RuleConfigurationPresenter(config).serialized

    def put(self, request, rule_slug):
        config = request.user.team.configurations.get(rule__slug=rule_slug)

        config.enabled = request.data.get('enabled', config.enabled)
        config.exclude = request.data.get('exclude', config.exclude)
        config.configuration = Configuration.values_from_full_config(request.data['configuration'])

        config.save()

        return RuleConfigurationPresenter(config).serialized