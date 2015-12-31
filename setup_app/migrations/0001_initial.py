# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ocorrencia',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('data', models.DateField(default=None, null=True)),
                ('local', models.CharField(max_length=200)),
                ('latitude', models.FloatField(default=0)),
                ('longitude', models.FloatField(default=0)),
                ('natureza', models.CharField(max_length=200)),
                ('hora', models.TimeField(default=None, null=True)),
            ],
        ),
    ]
