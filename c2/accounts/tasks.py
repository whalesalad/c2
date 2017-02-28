#!/usr/bin/env python
# -*- coding: utf-8 -*-

from celery.utils.log import get_task_logger

from c2.celery_app import app
from c2.accounts.models import Team

logger = get_task_logger(__name__)


# @app.task
# def sync_with_aws(identifier):
#     """
#     Identifier can be a string, in which case this is a team name and
#     the AmazonKey key needs to be fetched, or it can be an integer, in
#     which case it is the primary key of an AmazonKey object.

#     """

#     try:
#         identifier = int(identifier)
#     except:
#         pass

#     if isinstance(identifier, basestring):
#         team = Team.objects.get(identifier=identifier)
#         key = AmazonKey.objects.get(team=team)
#     elif isinstance(identifier, int):
#         key = AmazonKey.objects.prefetch_related('team').get(pk=identifier)
#         team = key.team

#     logger.info("Syncing AWS data information for %s" % team.name)

#     svc = key.get_svc()

#     send_aws_info_to_endpoint.delay(identifier, svc.to_dict())

#     updated_sensors = []

#     for sensor in team.sensors.all():
#         ip_address = sensor.snapshot.ip_addresses['data'].get('primary', None)
#         match = svc.instances.get(ip_address, None)

#         if not match:
#             logger.info("Sensor %s was not found in AWS." % (sensor.name))
#             continue

#         logger.info("Found sensor %s as instance %s" % (sensor.name, match['id'], ))

#         new_tags = match['tags']

#         # Try to set the Sensor's name from the instance metadata
#         # this will also remove it from the tags so it's not the name
#         # *and* a tag at the same time.
#         try:
#             sensor.name = new_tags.pop('Name')
#         except KeyError:
#             pass

#         # Grab the tags so we don't overwrite any existing ones,
#         # then update with the new tags, adding the instance id.
#         tags = sensor.tags
#         tags.update(match['tags'])
#         tags.update({ 'aws_instance_id': match['id'] })
#         sensor.tags = tags

#         sensor.save()

#         updated_sensors.append(sensor)

#     return updated_sensors