# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-26 08:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20171026_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='predict_info',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
