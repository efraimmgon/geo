# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ocorrencia',
            name='bairro',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='ocorrencia',
            name='numero',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='ocorrencia',
            name='via',
            field=models.CharField(default=None, max_length=200, null=True),
        ),
    ]
