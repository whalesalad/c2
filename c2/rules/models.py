import ujson as json

from django.db import models

from c2.accounts.models import Team
from c2.utils.models.mixins import TimestampedMixin, JSONSerializable

from djorm_pgarray.fields import TextArrayField
from django_extensions.db.fields.json import JSONField

class Configuration(object):
    def __init__(self, base_config=None, user_config=None):
        if base_config:
            self.base = base_config
        else:
            self.base = None

        if user_config:
            self.user = user_config
        else:
            if self.base:
                self.user = self.base
            else:
                self.user = {}

    @staticmethod
    def values_from_full_config(serialized):
        """
        Takes a full serialized object (from a POST for example)
        and simplifies it into {key:value} format.

        """

        if not serialized:
            return None

        for k,v in serialized.items():
            serialized[k] = v['value']

        return serialized


    def __getattr__(self, key):
        return self.user.get(key, None)

    @property
    def serialized(self):
        if not self.base:
            return None

        base = dict(self.base)

        return base


class Rule(JSONSerializable, models.Model):
    """
    Represents a rule for creating advisories.
    """

    RULE_GROUPS = (
        ('system',      u'System'),
        ('network',     u'Network'),
        ('auth',        u'Authentication'),
        ('security',    u'Security'),
        ('malware',     u'Malware'),
        ('config',      u'Configuration'),
    )

    name          = models.CharField(u'Name', max_length=250)
    slug          = models.SlugField(u'Slug', max_length=50, db_index=True)
    description   = models.TextField(u'Description', null=True, blank=True)

    public        = models.BooleanField('Whether or not this rule is exposed to the user.', default=True)
    category      = models.CharField(u'Category', max_length=25, choices=RULE_GROUPS, null=True)

    configuration = JSONField(default={}, blank=True, null=True)

    def __unicode__(self):
        return self.name

    def configuration_for_team(self, team=None, identifier=None):
        params = dict()

        if team:
            params['team'] = team
        elif identifier:
            params['team__identifier'] = identifier

        return self.configurations.get(**params)

    @property
    def underscored(self):
        return self.slug.replace('-', '_')


class RuleConfiguration(JSONSerializable, TimestampedMixin, models.Model):
    """
    Represents a team's preferences for a rule.
    """
    rule            = models.ForeignKey(Rule, related_name='configurations')
    team            = models.ForeignKey(Team, related_name='configurations')

    enabled         = models.BooleanField(u'Enabled for Team', default=True)

    # Groups to exclude from this rule
    exclude         = TextArrayField()

    # JSON blob for storing preferences related to this rule
    configuration   = JSONField(default={}, blank=True, null=True)

    class Meta:
        unique_together = ('rule', 'team')
        get_latest_by = 'created'

    @property
    def base_config(self):
        return self.rule.configuration

    @property
    def default_config(self):
        return Configuration(self.base_config)

    @property
    def config(self):
        return Configuration(self.base_config, self.configuration)

