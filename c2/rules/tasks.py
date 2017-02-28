#!/usr/bin/env python
# -*- coding: utf-8 -*-

from jinja2 import Environment

from celery.utils.log import get_task_logger

from datetime import datetime

from c2.celery_app import app
from c2.rules.models import Rule, RuleConfiguration
from c2.advisories.models import Advisory
from c2.accounts.models import Team
from c2.sensors.models import Sensor

from c2.utils.formatting import human_bytes

jinja_env = Environment()

logger = get_task_logger(__name__)

event_to_rule_mapping = {
    "unexpected_child_process": "process-anomaly",
    "anomalous_package": "package-anomaly",
    "anomalous_process_behavior": "process-anomaly",
    "malicious_file": "malicious-file",
}

TITLES = {
    "anomalous_package": "Abnormal package installed ({{ message.feature.split(':')[1] }})",
    "anomalous_process_behavior": "Abnormal process behavior ({{ message.value.process.pid }})",
    "unexpected_child_process": "Abnormal process behavior ({{ message.pid }})",
    "malicious_file": "Malicious file ({{ message.id }})detected",
}

def generate_title(payload):
    tmpl = TITLES.get(payload["event"], None)

    if tmpl:
        template = jinja_env.from_string(tmpl)
        try:
            title = template.render(payload["value"])
            return title
        except Exception as e:
            logger.error("Error templating advisory title. %s" % e)
            return "Advisory"

def create_advisory(rule, payload):
    """
    Process a rule and payload to generate an an advisory

    """
    title = generate_title(payload)

    try:
        sensor = Sensor.objects.get(pk=payload.get("sensor"))
    except Sensor.DoesNotExist:
        logger.error("Error creating advisory from event(%s). Sensor does not exist." % payload["event_id"])
        return None
    try:
        team = Team.objects.get(identifier=payload["team"])
        advisory = Advisory.objects.create(uuid=payload["event_id"],
                                           title=title,
                                           rule=rule,
                                           team=team,
                                           sensor=sensor)
    except Exception as e:
        logger.error('Error creating advisory from event(%s)' % (payload["event_id"], ))
        advisory = None

    return advisory

@app.task
def create_advisory_from_event_payload(payload):
    """
    Celery task for creating an advisories and related events.

    """
    rule_slug = event_to_rule_mapping.get(payload['event'], None)

    if not rule_slug:
        return

    rule = Rule.objects.get(slug=rule_slug)

    # config = RuleConfiguration.objects.get(rule__slug=rule_slug, team=payload['identifier'])

    # Die if the team has this rule disabled
    # if not config.enabled:
        # return None

    # Die if the sensor has a group that is in the exclude
    # if set(config.exclude or []) & set(sensor.groups or []):
    #     return None

    # If we're still here, create the advisory
    advisory = create_advisory(rule, payload)

    return advisory
