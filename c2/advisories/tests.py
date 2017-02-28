import mock

from django.test import TestCase

from c2.accounts.models import Team
from c2.sensors.models import Sensor
from c2.rules.models import Rule
from c2.rules.tasks import create_advisory_from_event_payload
from c2.advisories.models import Advisory, Notification

from c2.utils.test_utils import json_from_fixture


class AdvisoryTest(TestCase):
    """
    High-level Advisory tests.

    """

    fixtures = [ 'base', 'rules', ]

    def setUp(self):
        Sensor.snapshot = mock.PropertyMock(return_value=json_from_fixture('snapshot.json'))

        self.advisory_defaults = {
            "uuid": "fac675da-cc09-11e4-99b1-0aafae6a9f0b",
            "rule": Rule.objects.get(pk=1),
            "title": "Test Advisory #1",
            "team": Team.objects.get(pk=1),
        }

        sensor_defaults = {
            "uuid": "8bccb039-cba7-44cd-bccf-0181ace66389",
            "name": "salad.local",
            "team": Team.objects.get(identifier="foobar"),
            "groups": ['web', 'database']
        }

        self.proc_anomaly_payload = {
            "event": "anomalous_process_behavior",
            "event_id": "fac675da-cc09-11e4-99b1-0aafae6a9f0b",
            "sensor": "8bccb039-cba7-44cd-bccf-0181ace66389",
            "team": "foobar",
            "ts": 1426530396.203901,
            "value": {
                "message": {
                    "key": "proc_event",
                    "ts": 1426530361.246516,
                    "type": "item",
                    "uuid": "fff33b63-3923-43ed-aa55-e472550416af",
                    "value": {
                        "exit_code": 0,
                        "exit_signal": 17,
                        "kernel_ts": 338538.726846493,
                        "name": "PROC_EVENT_EXIT",
                        "process": {
                            "cmdline": "CRON",
                            "cpu_percent": 0.0,
                            "create_time": 1426530360.71,
                            "cwd": "/var/spool/cron",
                            "exe": "/usr/sbin/cron",
                            "gid": 0,
                            "id": "783|1426530360.71",
                            "memory_percent": 0.13,
                            "name": "cron",
                            "num_threads": 1,
                            "pid": 783,
                            "ppid": 1129,
                            "uid": 0
                        }
                    },
                    "version": 2
                },
                "results": [
                    {
                        "closest_cluster_value": 1.0,
                        "data_type": "name",
                        "data_type_entropy": 0.0,
                        "datum_value": 0.0,
                        "feature": "name:cron"
                    },
                    {
                        "closest_cluster_value": 1.0,
                        "data_type": "exit_code",
                        "data_type_entropy": 0.0,
                        "datum_value": 0.0,
                        "feature": "exit_code:0"
                    },
                    {
                        "closest_cluster_value": 1.0,
                        "data_type": "exit_signal",
                        "data_type_entropy": 0.0,
                        "datum_value": 0.0,
                        "feature": "exit_signal:17"
                    },
                    {
                        "closest_cluster_value": 1.0,
                        "data_type": "cwd",
                        "data_type_entropy": 0.3505638207,
                        "datum_value": 0.0,
                        "feature": "cwd:/root"
                    },
                    {
                        "closest_cluster_value": 1.0,
                        "data_type": "uid",
                        "data_type_entropy": 0.0,
                        "datum_value": 0.0,
                        "feature": "uid:0"
                    }
                ]
            }
        }

        self.package_anomaly_payload = {
            "event": "anomalous_package",
            "event_id": "3b379880-cc21-11e4-8063-0aafae6a9f0b",
            "sensor": "8bccb039-cba7-44cd-bccf-0181ace66389",
            "team": "foobar",
            "ts": 1426540382.744352,
            "value": {
                "ref": [
                    "123"
                ],
                "message": {
                    "CI_high": 0.4548357108,
                    "CI_low": -0.1018945343,
                    "feature": "package:supervisor",
                    "group": "d8bccc7f-f80d-4753-87dd-6097f97c2497",
                    "id": "33dfc688-5492-4c85-b32c-d832e1f6865d",
                    "mean": 0.1764705882,
                    "value": 1.0
                }
            }
        }

        self.malicious_file_payload = {
            "event": "malicious_file",
            "event_id": "35d20180-dce0-11e4-9ada-0a23f4a685af",
            "sensor": "8bccb039-cba7-44cd-bccf-0181ace66389",
            "team": "foobar",
            "ts": 1426540382.744352,
            "value": {
                "message": {
                    "gid": 42,
                    "hash": "sha1:0bcbded1f6be79a2818bc1623842a17e0b642c04",
                    "id": "/etc/gshadow",
                    "mode": 33184,
                    "pathname": "/etc/gshadow",
                    "size": 630,
                    "uid": 0
                },
                "ref": [
                    "ffdc2de0-8e86-42db-bd8a-7b1015cfd929"
                ]
            }
        }

        self.unexpected_child_process_payload = {
            "event": "unexpected_child_process"
            "event_id": "1ef70bb2-dfca-11e4-9f85-0a23f4a685af",
            "ts": 1426540382.744352,
            "team": "foobar",
            "sensor": "ee6dc0e8-10ba-478d-91d5-b6007a690ddf",
            "value": {
                "message": {
                    "ppid_cwd": "/var/www/html",
                    "parent_process": "/usr/sbin/apache2",
                    "pid": 28863,
                    "ppid_cmdline": "sh -c ls wp-config.php",
                    "node_id": "cf7b37ae-0525-42f3-8392-190ab9023ee1",
                    "parent_node_id": "f22fb568-65aa-482e-8ef0-7dcb3dce8ecf"
                },
                "ref": [ ],
                "payload": { }
            },
        }

        self.sensor, _ = Sensor.objects.get_or_create(**sensor_defaults)

    def test_existence_of_advisory_objects(self):
        self.assertIsNotNone(Advisory)
        self.assertIsNotNone(Notification)

    def test_advisory_groups(self):
        self.advisory_defaults["sensor"] = self.sensor
        a = Advisory.objects.create(**self.advisory_defaults)

        self.assertItemsEqual(a.sensor.groups, ['web', 'database'])


    def test_notification_creation(self):
        self.advisory_defaults["sensor"] = self.sensor
        a = Advisory.objects.create(**self.advisory_defaults)

        n = Notification.objects.filter(advisory=a).count()

        self.assertTrue(n > 0)

    def test_advisory_creation_from_proc_anomaly_payload(self):
        a = create_advisory_from_event_payload(self.proc_anomaly_payload)

        self.assertIsInstance(a, Advisory)
        self.assertEqual(a.title, "Abnormal process behavior (783)")

    def test_advisory_creation_from_package_anomaly_payload(self):
        a = create_advisory_from_event_payload(self.package_anomaly_payload)

        self.assertIsInstance(a, Advisory)
        self.assertEqual(a.title, "Abnormal package installed (supervisor)")

    def test_advisory_creation_from_malicious_file_payload(self):
        a = create_advisory_from_event_payload(self.malicious_file_payload)

        self.assertIsInstance(a, Advisory)
        self.assertEqual(a.title, "Malicious file (/etc/gshadow)detected")

    def test_advisory_creation_from_unregistered_sensor(self):
        self.proc_anomaly_payload["sensor"] = "12345678-aaaa-bbbb-cccc-123456789012"
        a = create_advisory_from_event_payload(self.proc_anomaly_payload)
        self.assertIsNone(a)
