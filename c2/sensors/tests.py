import os
import time
import mock
import json
import pprint

from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from c2.accounts.models import Team
from c2.sensors.models import Sensor
from c2.snapshot.presenters import SnapshotPresenter
from c2.utils.test_utils import fake_snapshot_payload, json_from_fixture, advisory_messages


class SensorTest(TestCase):
    """
    High-level Sensor tests.
    """
    fixtures = [ 'base' ]

    def setUp(self):
        self.defaults = dict(name="salad.local",
                             team=Team.objects.get(identifier='example'))
        Sensor.snapshot = mock.PropertyMock(return_value=json_from_fixture('snapshot.json'))

        self.payload = {
            "event": "sensor_new",
            "id": "ea8263ba-c8f2-11e4-843f-0aafae6a9f0b",
            "sensor": "e88836d5-7c87-46eb-8094-3ffe219fb16f",
            "team": "example",
            "ts": 1426115075.14476,
            "value": {}
        }

    def test_valid_sensor_enrollment(self):
        s = Sensor.create_from_payload(self.payload)
        self.assertIsInstance(s, Sensor)

    def test_invalid_sensor_enrollment_bad_team(self):
        self.payload["team"] = "evil-corporation"

        s = Sensor.create_from_payload(self.payload)
        self.assertIsNone(s)

    def test_setting_sensor_groups(self):
        s = Sensor.objects.create(**self.defaults)

        s.groups = ['web', 'database']
        s.save()

        self.assertItemsEqual(s.groups, ['web', 'database'])

    def test_setting_sensor_tags(self):
        s = Sensor.objects.create(**self.defaults)

        s.tags = dict(admin='trent', aws_zone='us-east')
        s.save()

        self.assertItemsEqual(s.tags, {'admin': 'trent', 'aws_zone': 'us-east'})
