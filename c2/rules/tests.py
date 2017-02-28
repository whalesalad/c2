import json
import pprint

from django.test import TestCase

from c2.rules.models import Rule

# move this
from c2.rules.models import Configuration

event_json = '''{
  "uuid": "5a1ad000-6969-474f-a2e0-144f8f743c6f",
  "key": "hostname",
  "event": "change",
  "ts": 1403303452,
  "old": {
    "ts": 1303303452,
    "value": {
      "fqdn": "dev-jwarren2.ec2.pin220.com",
      "hostname": "dev-jwarren2"
    }
  },
  "new": {
    "ts": 1403303452,
    "value": {
      "fqdn": "dev-jwarren999999.ec2.pin220.com",
      "hostname": "dev-jwarren999999"
    }
  }
}'''

class RuleTest(TestCase):
    def setUp(self):
        self.sensor = Sensor.objects.create(team=Team.objects.get(identifier="example"))


class ConfigurationTest(TestCase):
    """
    Tests for the base configuration parameters for a rule.

    """

    def setUp(self):
        user_base_config = json.loads("""
        {
            "user_added": {
                "label": "User Added",
                "type": "boolean",
                "default": true
            },
            "user_removed": {
                "label": "User Removed",
                "type": "boolean",
                "default": true
            },
            "user_modified": {
                "label": "User Modified",
                "type": "boolean",
                "default": true
            }
        }
        """)

        user_config = json.loads("""
            {
                "user_added": true,
                "user_removed": true,
                "user_modified": false
            }
        """)

        self.config = Configuration(user_base_config, user_config)

    def test_serialized(self):
        values = self.config.serialized.values()

        for v in values:
            self.assertIn('label', v)
            self.assertIn('type', v)

    def test_default_values(self):
        self.assertEqual(self.config.user_added, True)
        self.assertEqual(self.config.user_removed, True)
        self.assertEqual(self.config.user_modified, False)

    def test_changing_value(self):
        self.config.user_modified = True
        self.assertEqual(self.config.user_modified, True)

    def test_empty_values(self):
        config = Configuration(None, None)
