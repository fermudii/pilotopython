# Generated by Django 3.1.7 on 2021-04-16 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_basic', '0007_courses_available'),
    ]

    operations = [
        migrations.AddField(
            model_name='courses',
            name='excelLoaded',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
