# Generated by Django 3.1.7 on 2021-05-14 22:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_basic', '0010_ppr'),
    ]

    operations = [
        migrations.AddField(
            model_name='ppr',
            name='runs',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]