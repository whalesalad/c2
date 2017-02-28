import pprint
import datetime

from django.utils.timezone import utc

from c2.api.presenter import BasePresenter

class RulePresenter(BasePresenter):
    fields = ('name', 'slug', 'description', )

class RuleConfigurationPresenter(BasePresenter):

    @property
    def serialized(self):
        def fixup(rule, serialized):
            serialized.update(RulePresenter(rule.rule).serialized)
            return serialized

        return self.serialize(self.objects, fields=[
            'enabled',
            ('configuration', lambda r: r.config.serialized),
            ('exclude', lambda r: r.exclude or [])
        ], fixup=fixup)
