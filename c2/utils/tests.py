import json
import pprint
import decimal
import unittest

from django.test import TestCase, Client

from c2.utils.helpers import fancy_list_join
from c2.utils.json_encoders import DecimalEncoder

class TestHelpers(unittest.TestCase):
    def setUp(self):
        self.list_two = ['alpha', 'bravo']
        self.list_many = ['zulu', 'yankee', 'x-ray', 'whiskey']

    def test_fancy_list_join_two(self):
        fancy = fancy_list_join(self.list_two)
        self.assertEqual(fancy, 'alpha and bravo')

    def test_fancy_list_join_many(self):
        fancy = fancy_list_join(self.list_many)
        self.assertEqual(fancy, 'zulu, yankee, x-ray and whiskey')


class UtilsViewTests(TestCase):
    def setUp(self):
        self.client = Client(HTTP_ACCEPT='application/json')

    def test_elb_health_ping(self):
        """
        Tests that /ping is returning a valid response for
        ELB health check ping probes.

        """
        response = self.client.get('/ping/')
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(payload, { 'bear': 'claw' })


class TestDecimalEncoder(unittest.TestCase):
    def test_encoding_decimal(self):
        """
        Test that a dict containing a Decimal number can be encoded.

        """
        payload = {
            'a': 1,
            'b': decimal.Decimal(10.12345)
        }

        encoded = json.dumps(payload, sort_keys=True, cls=DecimalEncoder)

        result = """{"a": 1, "b": "10.1234500000000000596855898038484156131744384765625"}"""

        self.assertEqual(encoded, result)
