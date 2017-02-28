# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sensors', '0001_initial'),
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rules', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advisory',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('title', models.TextField(verbose_name='Title')),
                ('uuid', django_extensions.db.fields.UUIDField(primary_key=True, serialize=False, editable=False, blank=True, verbose_name='UUID')),
                ('rule', models.ForeignKey(related_name='advisories', to='rules.Rule')),
                ('sensor', models.ForeignKey(related_name='advisories', to='sensors.Sensor')),
                ('team', models.ForeignKey(related_name='advisories', to='accounts.Team')),
            ],
            options={
                'ordering': ('-created',),
                'get_latest_by': 'created',
                'verbose_name_plural': 'advisories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('unread', models.BooleanField(default=True)),
                ('advisory', models.ForeignKey(to='advisories.Advisory')),
                ('user', models.ForeignKey(related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
