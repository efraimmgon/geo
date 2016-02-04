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
                ('name', models.CharField(max_length=256, verbose_name='Nome', unique=True, default='')),
                ('description', models.TextField(default='', verbose_name='Descrição')),
                ('url', models.URLField()),
                ('views', models.IntegerField(default=0, verbose_name='Acessos')),
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
                ('name', models.CharField(max_length=256, verbose_name='Nome', unique=True)),
                ('description', models.TextField(default='', verbose_name='Descrição')),
            ],
            options={
                'verbose_name': 'Marcadores',
            },
        ),
        migrations.AddField(
            model_name='externalsource',
            name='tags',
            field=models.ManyToManyField(verbose_name='Etiquetas', to='principal.Tag'),
        ),
    ]
