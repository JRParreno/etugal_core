# Generated by Django 4.2.15 on 2024-09-09 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0013_alter_task_latitude_alter_task_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='done_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='schedule_time',
            field=models.TimeField(null=True),
        ),
    ]
