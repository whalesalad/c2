import uuid

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from c2.accounts.models import *
from c2.accounts.utils.team_name import TeamName

@receiver(post_save, sender=User)
def set_default_team_for_user(sender, instance, **kwargs):
    if not instance.memberships.exists():
        team = Team.objects.get(identifier=getattr(instance, '_identifier', None))
        membership = Membership.objects.create(user=instance, team=team, role="A")


def apikey_from_dynamo(apikey):
    return apikey_dynamo.get_item(access_key=apikey.access_key)


# XXX Disabled
# For Amazon DynamoDB
# http://docs.pythonboto.org/en/latest/dynamodb2_tut.html
# apikey_dynamo = Table('api_keys')
# @receiver(post_save, sender=APIKey)
def sync_apikey_with_dynamo(sender, instance, **kwargs):
    """
    When an APIKey object is saved, this signal is triggered.
    At this point, if the APIKey is enabled, ensure that the necessary
    fields are pushed/syncd to Dynamo.

    This logic should be moved into a separate class so that a higher-
    level abstraction exists. Something like APIKeyStore(instance).sync()

    XXX what is currently below is pseudo-code that has not been tested.

    XXX right now pseudo-code does not consider the key missing

    """
    key = apikey_from_dynamo(instance)

    if instance.is_active:
        key['secret_key'] = instance.secret_key
        resp = key.save()
    else:
        resp = key.delete()

    return resp


# XXX Disabled
# @receiver(post_delete, sender=APIKey)
def remove_apikey_from_dynamo(sender, instance, **kwargs):
    """
    Similar to above 'sync_apikey_with_dynamo' but as this is a post_delete
    hook, this will remove the key from Dynamo.

    """
    key = apikey_from_dynamo(instance)
    return key.delete()


@receiver(pre_save, sender=Team)
def set_team_identifier(sender, instance, **kwargs):
    """
    Set the team's identifier based on the name. While we're at it, let's
    prevent any unicode errors on the name by unicoding it (is that a word?)

    One thing we'll do is make sure that the identifier is unique by appending
    an '-n' where n is an incremented number until nothing

    """
    instance.name = unicode(instance.name)

    if not instance.identifier:
        identifier = slugify(instance.name)

        i = 0
        while Team.objects.filter(identifier=identifier).exists():
            i += 1
            identifier = '%s-%s' % (identifier, i)

        instance.identifier = identifier

@receiver(post_save, sender=Team)
def create_initial_apikey_for_team(sender, instance, **kwargs):
    """
    Create a default API Key for the team upon creation.

    """
    if not instance.keys.exists():
        instance.keys.create()
