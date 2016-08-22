# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setup_app', '0003_auto_20160111_1317'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cidade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, default='unknown')),
            ],
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='natureza',
            field=models.CharField(max_length=200, null=True, default=None),
        ),
        migrations.AddField(
            model_name='ocorrencia',
            name='cidade',
            field=models.ForeignKey(related_name='cidade', to='setup_app.Cidade', null=True, default=None),
        ),
    ]
