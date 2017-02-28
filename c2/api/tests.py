import pprint
import mock
import json
import itertools

from c2.accounts.auth.backends import TokenAuthBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import check_password
from django.test import TestCase, Client

from c2.accounts.models import Team
from c2.sensors.models import Sensor
from c2.utils.test_utils import json_from_fixture

User = get_user_model()

# XXX this improves the speed of tests dramatically, avoids looking to coyote
# Snapshot.fetch = mock.PropertyMock(return_value=lambda x,y: json_from_fixture('snapshots/zookeeper-1.json'))

class BaseAuthenticatedUserTestCase(TestCase):
    """
    A base class that is ready to make API calls as an authenticated user.

    """
    fixtures = ['base']

    def setUp(self):
        self.user = User.objects.create(email='salad@example.com',
                                        first_name='Michael',
                                        last_name='Whalen')

        self.client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.user.fresh_token,
                             HTTP_ACCEPT='application/json')

        self.bad_client = Client()


class UserAuthenticationTest(TestCase):
    """
    Tests for logging-in and getting a json web token
    POST /api/authenticate/

    """
    fixtures = ['base']

    def setUp(self):
        user = User.objects.create(email='johndoe@example.com',
                                   first_name='John',
                                   last_name='Doe')

        user.set_password('who_am_i')
        user.save()

        self.client = Client(HTTP_ACCEPT='application/json')

    def test_get_auth_token_with_username(self):
        post_dict = dict(username='johndoe@example.com', password='who_am_i')
        response = self.client.post('/api/authenticate', post_dict)
        payload = json.loads(response.content)

        self.assertTrue('token' in payload)
        self.assertTrue('uid' in payload)

    def test_auth_token_is_valid_when_decoded(self):
        # NOTE: above test uses 'username', this test uses 'email'
        # we kill two birds with one stone
        post_dict = dict(email='johndoe@example.com', password='who_am_i')
        response = self.client.post('/api/authenticate', post_dict)
        payload = json.loads(response.content)

        backend = TokenAuthBackend()
        user = backend.authenticate(token=payload['token'])

        self.assertEqual(user.id, payload['uid'])


class UserRegistrationTest(TestCase):
    fixtures = ['base']

    def setUp(self):
        self.client = Client(HTTP_ACCEPT='application/json')

    def test_valid_response(self):
        post_dict = dict(full_name='Sally Susan',
                         email='example@example.com',
                         password='who_am_i')

        response = self.client.post('/api/users', content_type='application/json',
                                                  data=json.dumps(post_dict))

        payload = json.loads(response.content)

        expected_keys = ('team', 'first_name', 'last_name', 'email', 'created',
                         'token', 'is_staff', 'full_name')

        self.assertItemsEqual(expected_keys, payload.keys())
        self.assertEqual(payload['first_name'], 'Sally')
        self.assertEqual(payload['last_name'], 'Susan')


class UserDetailTest(TestCase):
    """
    Tests for grabbing a user's profile
    GET /api/user

    """
    fixtures = ['base']

    def setUp(self):
        self.user = User.objects.create(email='salad@example.com',
                                        first_name='Michael',
                                        last_name='Whalen')

        client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.user.fresh_token,
                        HTTP_ACCEPT='application/json')

        self.response = client.get('/api/user/')
        self.payload = json.loads(self.response.content)

    def test_responds_with_required_attributes(self):
        expected_keys = ('team', 'first_name', 'last_name', 'email', 'created', 'is_staff', 'full_name')
        self.assertItemsEqual(expected_keys, self.payload.keys())

    def test_responds_with_correct_attributes(self):
        self.assertEqual(self.payload['email'], 'salad@example.com')
        self.assertEqual(self.payload['first_name'], 'Michael')
        self.assertEqual(self.payload['last_name'], 'Whalen')


class UpdateUserTest(TestCase):
    """
    Test POSTing to a user to update name, email, password, etc...

    """
    fixtures = ['base']

    def setUp(self):
        self.user = User.objects.create(email='salad@example.com',
                                        first_name='Michael',
                                        last_name='Whalen')

        self.user.set_password('elephant')
        self.user.save()

        self.client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.user.fresh_token,
                             HTTP_ACCEPT='application/json')

        self.initial = json.loads(self.client.get('/api/user').content)


    def test_change_name(self):
        self.assertEqual(self.initial['first_name'], 'Michael')
        self.assertEqual(self.initial['last_name'], 'Whalen')
        self.assertEqual(self.initial['full_name'], 'Michael Whalen')
        self.assertEqual(self.initial['email'], 'salad@example.com')

        post_data = { 'full_name': 'Eleanor Roosevelt' }
        post = self.client.post('/api/user', post_data)
        response = json.loads(post.content)

        self.assertEqual(response['first_name'], 'Eleanor')
        self.assertEqual(response['last_name'], 'Roosevelt')
        self.assertEqual(response['full_name'], 'Eleanor Roosevelt')
        self.assertEqual(response['email'], 'salad@example.com')

    def test_change_email(self):
        self.assertEqual(self.initial['full_name'], 'Michael Whalen')
        self.assertEqual(self.initial['email'], 'salad@example.com')

        post_data = { 'email': 'random@example.com' }
        post = self.client.post('/api/user', post_data)
        response = json.loads(post.content)


        self.assertEqual(response['full_name'], 'Michael Whalen')
        self.assertEqual(response['email'], 'random@example.com')


class ChangePasswordTest(TestCase):
    fixtures = ['base']

    def setUp(self):
        self.user = User.objects.create(email='salad@example.com',
                                        first_name='Michael',
                                        last_name='Whalen')

        self.user.set_password('elephant999')
        self.user.save()

        self.client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.user.fresh_token,
                             HTTP_ACCEPT='application/json')

    def test_initial_password(self):
        valid_password = self.user.check_password('elephant999')
        self.assertTrue(valid_password)

    def test_change_password(self):
        post_data = {
            'password': 'this is seven characters long',
            'password_confirm': 'this is seven characters long'
        }

        post = self.client.post('/api/user/password', content_type='application/json',
                                                      data=json.dumps(post_data))

        response = json.loads(post.content)

        user = User.objects.get(email='salad@example.com')
        valid = user.check_password('this is seven characters long')

        self.assertTrue(valid, msg="User password was not updated properly.")


    def test_change_password_with_mismatch_passwords(self):
        post_data = {
            'password': 'this is seven characters long',
            'password_confirm': 'NOTmusic7'
        }

        post = self.client.post('/api/user/password', content_type='application/json',
                                                      data=json.dumps(post_data))

        response = json.loads(post.content)

        self.assertItemsEqual(response, {'error': 'The two passwords provided do not match.'})

        user = User.objects.get(email='salad@example.com')

        # Since the user submitted mismatching passwords, the user should
        # still have their original password
        valid = user.check_password('elephant999')

        self.assertTrue(valid, msg="User's password was changed despite mismatched passwords")


    def test_password_with_password_that_is_too_short(self):
        post_data = {
            'password': 'short',
            'password_confirm': 'short'
        }

        post = self.client.post('/api/user/password', content_type='application/json',
                                                      data=json.dumps(post_data))

        response = json.loads(post.content)

        self.assertItemsEqual(response, {'error': 'Your password must be at least 7 characters long, you entered 5.'})


    def test_change_password_with_no_post_data(self):
        post_data = {}

        post = self.client.post('/api/user/password', content_type='application/json',
                                                      data=json.dumps(post_data))

        response = json.loads(post.content)

        self.assertItemsEqual(response, {'error': 'Enter your new password, then verify it one more time confirmation field.'})



# class SensorListTest(TestCase):
#     """
#     Tests for URLs beginning with /api/sensors

#     """
#     fixtures = ['base']

#     def setUp(self):
#         self.user = User.objects.create(email='salad@example.com',
#                                         first_name='Michael',
#                                         last_name='Whalen')

#         Sensor.snapshot = mock.PropertyMock(return_value=lambda x,y: json_from_fixture('fixtures/snapshot.json'))

#         self.sensor_two = Sensor.objects.create(name='alpha.example.com',
#                                                 team=self.user.team,
#                                                 group='web')

#         self.sensor_two = Sensor.objects.create(name='bravo.example.com',
#                                                 team=self.user.team,
#                                                 group='db')

#         self.client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.user.fresh_token,
#                              HTTP_ACCEPT='application/json')

#         self.response = self.client.get('/api/sensors/')
#         self.payload = json.loads(self.response.content)

#     def test_list_requires_auth(self):
#         client = Client()
#         response = client.get('/api/sensors/')
#         payload = json.loads(response.content)

#         self.assertEqual(response.status_code, 403)
#         self.assertTrue('error' in payload)

#     def test_list_sensors_for_user(self):
#         self.assertEqual(self.response.status_code, 200)

#     def test_hostnames_are_valid(self):
#         hostnames = [s['name'] for s in self.payload]
#         self.assertIn('alpha.example.com', hostnames)
#         self.assertIn('bravo.example.com', hostnames)

#     def test_groups_are_valid(self):
#         pass

class SensorDetailTest(TestCase):
    """
    Tests for URLs beginning with /api/sensors/<uuid>
    Including sub-urls like /advisories, /snapshot, etc...

    """
    fixtures = ['base']

    def setUp(self):
        user = User.objects.create(email='sallysusan@example.com',
                                   first_name='Sally',
                                   last_name='Susan')

        Sensor.snapshot = mock.PropertyMock(return_value=json_from_fixture('snapshot.json'))

        Sensor.objects.create(uuid='b57f3245-2362-4082-b994-297eadaad765',
                              name='alpha.example.com',
                              team=user.team)

        self.client = Client(HTTP_AUTHORIZATION='Bearer %s' % user.fresh_token,
                             HTTP_ACCEPT='application/json')

    def test_get_sensor_by_uuid(self):
        # PASS until vermont gets stubbed out
        pass
        # response = self.client.get('/api/sensors/b57f3245-2362-4082-b994-297eadaad765/')
        # payload = json.loads(response.content)
        # self.assertEqual(payload['name'], 'alpha.example.com')

class AdvisoryListTest(TestCase):
    fixtures = ['base']

    def test_list_requires_auth(self):
        client = Client()
        response = client.get('/api/advisories/')
        payload = json.loads(response.content)

        self.assertEqual(response.status_code, 403)
        self.assertTrue('error' in payload)


class TeamTest(TestCase):
    fixtures = ['base']

    def setUp(self):
        self.user = User.objects.get(email='c2@example.com')

        self.client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.user.fresh_token,
                             HTTP_ACCEPT='application/json')

        self.assertTrue(Team.objects.first().name, 'example')

    def test_listing_teams(self):
        response = self.client.get('/api/teams')
        payload = json.loads(response.content)

        team = payload[0]

        self.assertTrue('membership' in team)
        self.assertEqual(team['name'], 'example')

    def test_getting_a_specific_team(self):
        response = self.client.get('/api/teams/example')
        payload = json.loads(response.content)

        self.assertTrue('membership' in payload)
        self.assertTrue('keys' in payload)
        self.assertEqual(payload['name'], 'example')

    def test_getting_a_hyphenated_team_name(self):
        team = Team.objects.create(name="Purple Kangaroos", identifier="purple-kangaroos")
        membership = self.user.memberships.create(team=team)
        membership.make_admin()
        membership.save()

        response = self.client.get('/api/teams/purple-kangaroos')
        payload = json.loads(response.content)

        self.assertTrue('membership' in payload)
        self.assertTrue('keys' in payload)
        self.assertEqual(payload['name'], 'Purple Kangaroos')


class InternalEndpointTest(TestCase):
    fixtures = ['base']

    def setUp(self):
        self.client = Client(HTTP_ACCEPT='application/json')

        team = Team.objects.get(identifier='example')
        self.api_key = team.keys.create()

    def test_verify_access_key(self):
        response = self.client.post('/internal/verify/%s' % (self.api_key.access_key))
        payload = json.loads(response.content)

        self.assertEqual(payload['identifier'], 'example')
        self.assertEqual(payload['secret_key'], self.api_key.secret_key)

