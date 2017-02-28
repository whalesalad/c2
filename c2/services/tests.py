import json
import pprint

from django.test import TestCase
from django.contrib.auth import get_user_model

import boto.ec2

from c2.services import TokenService, AmazonInfoService, SSLCertificateService

User = get_user_model()

class TokenServiceTests(TestCase):
    fixtures = [ 'base' ]

    def setUp(self):
        self.service = TokenService()
        self.user = User.objects.create(email='jwt_user@example.com',
                                        first_name='JSON',
                                        last_name='Token')

        self.token = self.service.token_for_user(self.user)

    def test_getting_a_token_for_user(self):
        self.assertIsInstance(self.token, basestring, msg="Token is not a string.")

    def test_token_payload_has_expected_properties(self):
        payload = self.service.payload_for_token(self.token)
        self.assertItemsEqual(payload.keys(), ['iat', 'uid', 'email'])

    def test_get_user_for_token(self):
        payload = self.service.payload_for_token(self.token)
        self.assertEqual(payload['uid'], self.user.id)
        self.assertEqual(payload['email'], self.user.email)


class AmazonInfoServiceTests(TestCase):
    fixtures = [ 'base' ]

    def setUp(self):
        params = {
            "access_key": "AKIAJSXERGARNRFMZCOQ",
            "secret_key": "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",
            "regions":    ['us-west-2']
        }

        self.svc = AmazonInfoService(**params)

    def test_connections(self):
        self.assertTrue(self.svc.is_connected)

    def test_getting_raw_instances(self):
        instances = self.svc.get_instances()
        self.assertIsInstance(instances, list)

        for i in instances:
            self.assertIsInstance(i, boto.ec2.instance.Instance)

    def test_parsed_instances(self):
        instances = self.svc.instances
        self.assertIsInstance(instances, dict)

        required = ('id', 'instance_type', 'ip_address', 'private_dns_name',
                    'private_ip_address', 'public_dns_name', 'state', 'tags',
                    'groups', )

        for instance_id, instance in instances.iteritems():
            keys = instance.keys()
            for key in required:
                self.assertIn(key, keys)

    def test_serialization(self):
        payload = json.dumps(self.svc.to_dict())
        original = json.loads(payload)

        self.assertTrue('instances' in original)
        self.assertTrue('groups' in original)


# class SSLCertificateServiceTests(TestCase):
#     def setUp(self):
#         self.svc = SSLCertificateService()

#     def test_validate_accepts_list_of_ips_as_single_arg(self):
#         load_balancers = ('54.213.119.231', '54.200.119.226', )
#         certificates = self.svc.validate(load_balancers)
#         pprint.pprint(certificates)

#     # def test_validate_against_non_ssl(self):
#     #     non_ssl = ('54.187.178.112', )
#     #     certificates = self.svc.validate(non_ssl)
#     #     pprint.pprint(certificates)
