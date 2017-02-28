import pprint
import jwt
import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from c2.accounts.models import Team
from c2.accounts.auth.backends import TokenAuthBackend
from c2.services import TokenService

User = get_user_model()


class TokenAuthBackendTests(TestCase):
    fixtures = ['base']

    def setUp(self):
        self.service = TokenService()
        self.user = User.objects.create(email='johndoe@example.com',
                                        first_name='John',
                                        last_name='Doe')

        self.bad_token = jwt.encode({
            "iat": time.time() - 24 * 60 * 60 * 8,
            "uid": self.user.id,
            "email": self.user.email,
            }, settings.SECRET_KEY, "HS512")

    def test_valid_user_from_backend(self):
        token = self.service.token_for_user(self.user)
        user = TokenAuthBackend().authenticate(token)

        self.assertEqual(user, self.user)
        self.assertEqual(user.email, 'johndoe@example.com')

    def test_no_user_for_invalid_token(self):
        user = TokenAuthBackend().authenticate('crap-this-is-not-real')
        self.assertEqual(user, None)

    def test_no_user_for_invalid_token(self):
        user = TokenAuthBackend().authenticate('crap-this-is-not-real')
        self.assertEqual(user, None)

    def test_no_user_for_expired_token(self):
        user = TokenAuthBackend().authenticate(self.bad_token)
        self.assertEqual(user, None)


class UserAccountTests(TestCase):
    fixtures = ['base']

    def setUp(self):
        self.user = User.objects.create(email='johndoe@example.com',
                                        first_name='John',
                                        last_name='Doe')

    def test_full_name(self):
        self.user.full_name = 'Serena van Der Woodsen'
        self.assertEqual(self.user.first_name, 'Serena')
        self.assertEqual(self.user.last_name, 'van Der Woodsen')

        self.user.full_name = 'Joe Dirt'
        self.assertEqual(self.user.first_name, 'Joe')
        self.assertEqual(self.user.last_name, 'Dirt')

        self.user.full_name = ''
        self.assertEqual(self.user.first_name, '')
        self.assertEqual(self.user.last_name, '')


    def test_user_gets_default_team(self):
        self.assertEqual(self.user.team_set.count(), 1)

    def test_user_is_admin_of_their_default_team(self):
        membership = self.user.memberships.all()[0]
        self.assertTrue(membership.is_admin)

    def test_user_only_gets_one_default_team(self):
        """
        Test for a bug where a user would get multiple default teams on
        each save. We modify the user, save, modify user, save, and should
        still only have one team.

        """
        self.user.first_name = 'Johnny'
        self.user.save()
        self.user.last_name = 'Smith'
        self.user.save()
        self.assertEqual(self.user.team_set.count(), 1)


class TeamTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name='Crunchy Pandas')
        self.team_two = Team.objects.create(name='Crunchy Pandas')
        self.team_three = Team.objects.create(name='Horny Rhino\'s #3')
        self.team_four = Team.objects.create(name='Horny Rhino\'s #3')

    def test_new_teams_get_api_key(self):
        self.assertEqual(self.team.keys.count(), 1)

    def test_team_has_identifier(self):
        self.assertEqual(self.team.identifier, 'crunchy-pandas')

    def test_all_teams_have_unique_identifiers(self):
        self.assertNotEqual(self.team.identifier,
                            self.team_two.identifier)

        self.assertNotEqual(self.team_three.identifier,
                            self.team_four.identifier)

    def test_team_slug_does_not_change_after_save(self):
        self.team_two.name = 'Crunchy Pandas Reborn'
        self.team_two.save()
        self.assertEqual(self.team_two.identifier, 'crunchy-pandas-1')


# class SyncWithAWSTaskTests(TestCase):
#     """
#     Tests the Celery task for syncing with AWS

#     """

#     def test_sync
