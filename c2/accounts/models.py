import os
import binascii

from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.conf import settings

from c2.accounts.managers import UserManager
from c2.services import TokenService
from c2.utils.models import TimestampedMixin, ActiveOnlyManager, enum_choices


class User(AbstractBaseUser):
    email       = models.EmailField(u'Email Address', unique=True, max_length=254)
    first_name  = models.CharField(u'First Name', max_length=30, blank=True)
    last_name   = models.CharField(u'Last Name', max_length=30, blank=True)
    is_staff    = models.BooleanField(u'Staff Status', default=False)
    created     = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        get_latest_by = 'created'
        verbose_name = u'user'
        verbose_name_plural = u'users'

    def __unicode__(self):
        return self.full_name or self.email

    @property
    def full_name(self):
        return (u'%s %s' % (self.first_name, self.last_name, )).strip()

    @full_name.setter
    def full_name(self, value):
        name_parts = value.strip().split(' ')
        self.first_name = name_parts[0]
        self.last_name = ' '.join(name_parts[1:])

    def get_short_name(self):
        return self.first_name

    def get_full_name(self):
        return self.full_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def team(self):
        teams = self.team_set.all()

        if teams:
            return teams[0]

        return None

    def is_part_of(self, team):
        return team in self.team_set.all()

    @property
    def fresh_token(self):
        return TokenService().token_for_user(self)

class Team(models.Model):
    name        = models.CharField(u'Team Name', max_length=120)
    identifier  = models.SlugField(unique=True)
    account_id  = models.CharField(u'Account ID', max_length=120, blank=True, null=True)

    members     = models.ManyToManyField(User, through='Membership')
    is_hidden   = models.BooleanField(default=True)

    # Billing Related Fields
    is_active   = models.BooleanField(default=True)
    max_sensors = models.IntegerField(default=0)

    def __unicode__(self):
        return u'Team %s' % (self.name, )


class Membership(TimestampedMixin, models.Model):
    """
    Represents a User -> Team membership. Holds details such as when
    the relationship was created, whether or not the user is an admin, etc...

    """


    ROLES = enum_choices(
        ADMIN = ('A', 'Administrator'),
        USER  = ('U', 'User')
    )

    user = models.ForeignKey(User, related_name='memberships')
    team = models.ForeignKey(Team, related_name='memberships')
    role = models.CharField(u'User Role', default=ROLES.USER, choices=ROLES, max_length=10)

    class Meta:
        unique_together = ("user", "team")

    def __unicode__(self):
        return u'%s in %s' % (self.user, self.team, )

    @property
    def is_admin(self):
        return self.role == self.ROLES.ADMIN

    def make_admin(self):
        self.role = self.ROLES.ADMIN

    @property
    def is_user(self):
        return self.role == self.ROLES.USER

    def make_user(self):
        self.role == self.ROLES.USER


def make_access_key():
    return binascii.b2a_hex(os.urandom(10)).upper()

def make_secret_key():
    return binascii.b2a_hex(os.urandom(20))


class APIKey(TimestampedMixin, models.Model):
    team        = models.ForeignKey(Team, related_name='keys')
    name        = models.CharField(u'Nickname', max_length=256, blank=True)
    access_key  = models.CharField(max_length=20, default=make_access_key)
    secret_key  = models.CharField(max_length=40, default=make_secret_key)
    is_active   = models.BooleanField(u'Active', default=True)

    objects = ActiveOnlyManager()
    unscoped = models.Manager()

    class Meta:
        get_latest_by = 'created'
        ordering = ('-created', )
        verbose_name = u'API key'
        verbose_name_plural = u'API keys'

    def __unicode__(self):
        return u'%s: %s' % (self.team, self.access_key, )

    @property
    def credentials(self):
        return {
            'access_key': self.access_key,
            'secret_key': self.secret_key
        }
