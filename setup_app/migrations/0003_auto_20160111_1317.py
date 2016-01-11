# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup_app', '0002_auto_20160104_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ocorrencia',
            name='latitude',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='local',
            field=models.CharField(null=True, default=None, max_length=200),
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='longitude',
            field=models.FloatField(default=0, null=True),
        ),
    ]
