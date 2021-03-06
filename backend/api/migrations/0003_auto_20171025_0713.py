# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-10-25 07:13
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_carmodel_make'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='car_models',
            field=models.ManyToManyField(related_name='models', related_query_name='model', to='api.CarModel'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='model',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.CarModel'),
        ),
    ]
