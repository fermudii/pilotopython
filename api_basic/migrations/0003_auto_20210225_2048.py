# Generated by Django 3.1.7 on 2021-02-25 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_basic', '0002_piloto'),
    ]

    operations = [
        migrations.AddField(
            model_name='piloto',
            name='laoep',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='laovc',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='lfpl',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='lnor',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='lpoce',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='saoep',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='saovc',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='sfpl',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='snor',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='spoce',
            field=models.CharField(default='empty', max_length=100),
        ),
        migrations.AddField(
            model_name='piloto',
            name='vehicle',
            field=models.CharField(default='empty', max_length=100),
        ),
    ]
