import pprint
from jinja2 import Environment
from c2.sensors.models import Sensor

jinja_env = Environment()


class EventPresenter(object):
    TEMPLATES = {
        # Events
        "netlink_audit_network_create": "Network interface created ({{syscall}})",
        "netlink_audit_network_inbound": "Inbound connection ({{remote}})",
        "netlink_audit_network_outbound": "Outbound connection ({{remote}})",

        "proc_exit": "Process exited ({{pid}})",
        "proc_exec": "Process execution ({{pid}})",

        "user_logged_in": "({{name}}) logged in via {{terminal}}",
        "user_logged_out": "({{name}}) logged out",

        "listen_port_created": "Listen port created ({{id}})",
        "listen_port_closed": "Listen port closed ({{id}})",

        "netlink_audit_unknown": "{{operation}} for {{orig[operation].attrs.user}}",

        # Advisories
        "anomalous_process_behavior": "Abnormal process behavior ({{ value.process.pid }})",
        "anomalous_package": "Abnormal package installed ({{ feature.split(':')[1] }})",
        "unexpected_child_process": "Abnormal process behavior ({{ pid }})",
        "malicious_file": "Malicious file ({{ id }})detected",
    }

    def __init__(self, models):
        self.models = models

    def create_description(self, event):
        key = event.get("event", None)
        tmpl = self.TEMPLATES.get(key, None)

        if tmpl:
            template = jinja_env.from_string(tmpl)
            try:
                return template.render(event["value"]["message"])
            except:
                pass


        return "%s" % (key, )

    def assign_sensor(self, uuid, sensors):
        for sensor in sensors:
            if uuid == sensor.uuid:
                return sensor.name

        return None

    def assign_groups(self, uuid, sensors):
        for sensor in sensors:
            if uuid == sensor.uuid:
                return sensor.groups

    def transform_model(self, model):
        if not model:
            return None

        return {
            "event_id": model.get("id"),
            "event": model.get("event"),
            "occurred": model.get("ts"),
            "description": self.create_description(model),
            "team": model.get("team"),
            "sensor_uuid": model.get("sensor"),
            "sensor_name": self.assign_sensor(model.get("sensor", ""), self.sensors),
            "sensor_groups": self.assign_groups(model.get("sensor", ""), self.sensors),
            "value": model.get("value"),
        }

    def serialized(self, sensors):
        if not sensors:
            return []

        self.sensors = sensors
        return map(self.transform_model, self.models)

    @property
    def serialize(self):
        model = self.models

        return {
            "event_id": model.get("id"),
            "event": model.get("event"),
            "occurred": model.get("ts"),
            "description": self.create_description(model),
            "team": model.get("team"),
            "sensor_uuid": model.get("sensor"),
            "sensor_name": model.get("sensor_name"),
            "sensor_groups": model.get("sensor_groups", []),
            "value": model.get("value"),
        }
