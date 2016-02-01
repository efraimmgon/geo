# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('principal', '0003_auto_20160201_2016'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField(verbose_name='Descrição', default='')),
            ],
            options={
                'verbose_name': 'Etiqueta',
            },
        ),
        migrations.AlterField(
            model_name='externalsource',
            name='name',
            field=models.CharField(verbose_name='Nome', max_length=256, unique=True),
        ),
        migrations.AddField(
            model_name='externalsource',
            name='tags',
            field=models.ManyToManyField(verbose_name='Etiquetas', to='principal.Tag'),
        ),
    ]
