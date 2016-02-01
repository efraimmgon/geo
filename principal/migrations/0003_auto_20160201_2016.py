# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('principal', '0002_auto_20160201_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalsource',
            name='description',
            field=models.TextField(default='', verbose_name='Descrição'),
        ),
        migrations.AlterField(
            model_name='externalsource',
            name='name',
            field=models.CharField(verbose_name='Nome', max_length=256),
        ),
    ]
