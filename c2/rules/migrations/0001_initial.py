# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djorm_pgarray.fields
import c2.utils.models.mixins
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('public', models.BooleanField(default=True, verbose_name=b'Whether or not this rule is exposed to the user.')),
                ('category', models.CharField(max_length=25, null=True, verbose_name='Category', choices=[(b'system', 'System'), (b'network', 'Network'), (b'auth', 'Authentication'), (b'security', 'Security'), (b'malware', 'Malware'), (b'config', 'Configuration')])),
                ('configuration', django_extensions.db.fields.json.JSONField(null=True, blank=True)),
            ],
            options={
            },
            bases=(c2.utils.models.mixins.JSONSerializable, models.Model),
        ),
        migrations.CreateModel(
            name='RuleConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('enabled', models.BooleanField(default=True, verbose_name='Enabled for Team')),
                ('exclude', djorm_pgarray.fields.TextArrayField(dbtype=b'text')),
                ('configuration', django_extensions.db.fields.json.JSONField(null=True, blank=True)),
                ('rule', models.ForeignKey(related_name='configurations', to='rules.Rule')),
                ('team', models.ForeignKey(related_name='configurations', to='accounts.Team')),
            ],
            options={
                'get_latest_by': 'created',
            },
            bases=(c2.utils.models.mixins.JSONSerializable, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='ruleconfiguration',
            unique_together=set([('rule', 'team')]),
        ),
    ]
