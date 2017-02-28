# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import c2.sensors.utils.cluster_name
import c2.utils.models.mixins
import django_extensions.db.fields
import djorm_pgarray.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('uuid', django_extensions.db.fields.UUIDField(primary_key=True, serialize=False, editable=False, blank=True, verbose_name='UUID')),
                ('name', models.CharField(default=c2.sensors.utils.cluster_name.generate_cluster_name, max_length=250, verbose_name='Name')),
                ('is_user', models.BooleanField(default=False)),
                ('team', models.ForeignKey(related_name='clusters', to='accounts.Team')),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(c2.utils.models.mixins.JSONSerializable, models.Model),
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('uuid', django_extensions.db.fields.UUIDField(primary_key=True, serialize=False, editable=False, blank=True, verbose_name='UUID')),
                ('name', models.CharField(max_length=250, null=True, verbose_name='Name', blank=True)),
                ('groups', djorm_pgarray.fields.TextArrayField(dbtype=b'text')),
                ('active', models.BooleanField(default=True, verbose_name='Active')),
                ('cloud_key', models.CharField(max_length=250, null=True, verbose_name='Cloud Key', blank=True)),
                ('team', models.ForeignKey(related_name='sensors', to='accounts.Team')),
            ],
            options={
                'ordering': ('-created',),
                'get_latest_by': 'created',
            },
            bases=(c2.utils.models.mixins.JSONSerializable, models.Model),
        ),
    ]
