# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-26 08:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20171026_0217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='carmodel',
            name='predict_model',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]