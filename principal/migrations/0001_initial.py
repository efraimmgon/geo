# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalSource',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, verbose_name='Nome', default='', max_length=256)),
                ('description', models.TextField(verbose_name='Descrição', default='')),
                ('link', models.URLField()),
            ],
            options={
                'verbose_name_plural': 'Fontes externas',
                'verbose_name': 'Fonte externa',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, verbose_name='Nome', max_length=256)),
                ('description', models.TextField(verbose_name='Descrição', default='')),
            ],
            options={
                'verbose_name': 'Etiqueta',
            },
        ),
        migrations.AddField(
            model_name='externalsource',
            name='tags',
            field=models.ManyToManyField(to='principal.Tag', verbose_name='Etiquetas'),
        ),
    ]
