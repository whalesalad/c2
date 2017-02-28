# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import c2.accounts.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('email', models.EmailField(unique=True, max_length=254, verbose_name='Email Address')),
                ('first_name', models.CharField(max_length=30, verbose_name='First Name', blank=True)),
                ('last_name', models.CharField(max_length=30, verbose_name='Last Name', blank=True)),
                ('is_staff', models.BooleanField(default=False, verbose_name='Staff Status')),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'get_latest_by': 'created',
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256, verbose_name='Nickname', blank=True)),
                ('access_key', models.CharField(default=c2.accounts.models.make_access_key, max_length=20)),
                ('secret_key', models.CharField(default=c2.accounts.models.make_secret_key, max_length=40)),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
            ],
            options={
                'ordering': ('-created',),
                'get_latest_by': 'created',
                'verbose_name': 'API key',
                'verbose_name_plural': 'API keys',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('role', models.CharField(default=b'U', max_length=10, verbose_name='User Role', choices=[(b'A', b'Administrator'), (b'U', b'User')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=120, verbose_name='Team Name')),
                ('identifier', models.SlugField(unique=True)),
                ('account_id', models.CharField(max_length=120, null=True, verbose_name='Account ID', blank=True)),
                ('is_hidden', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('max_sensors', models.IntegerField(default=0)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='accounts.Membership')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='membership',
            name='team',
            field=models.ForeignKey(related_name='memberships', to='accounts.Team'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(related_name='memberships', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('user', 'team')]),
        ),
        migrations.AddField(
            model_name='apikey',
            name='team',
            field=models.ForeignKey(related_name='keys', to='accounts.Team'),
            preserve_default=True,
        ),
    ]
