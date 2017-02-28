import os
import ujson as json

from django.conf import settings

FIXTURE_PATH = os.path.join(settings.BASE_DIR, 'fixtures')

def json_from_fixture(path):
    file_path = "%s/%s" % (FIXTURE_PATH, path, )

    with open(file_path, 'r') as f:
        payload = json.loads(f.read())

    return payload

def advisory_messages():
    """
    Returns an iterator of advisory messages to be used during testing

    """
    file_path = "%s/advisory_messages.json" % FIXTURE_PATH

    with open(file_path, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                f.close()
                break

            yield line


def fake_snapshot_payload():
    fake_payload = """
    {
        "uuid": "1234",
        "identifier": "example",
        "advisories": [],
        "fields": [
            {
                "key": "hostname",
                "ts": 1389735233,
                "value": {
                    "longname": "devnull.local",
                    "shortname": "devnull"
                }
            },
            {
                "key": "version",
                "ts": 1389734415,
                "value": {
                    "author": "example",
                    "buildepoch": {
                        "avg": 1385479630.0,
                        "count": 1,
                        "first": 1385479630.0,
                        "last": 1385479630.0,
                        "max": 1385479630.0,
                        "min": 1385479630.0
                    },
                    "buildtime": "2013-11-26 10:27:10",
                    "version": "e939e995d21b004132ce369e5580ff4e7c85ede7"
                }
            }
        ]
    }
    """

    return json.loads(fake_payload.replace('\n', '').strip())
