# Generated by Django 4.2.15 on 2024-09-10 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0014_task_done_date_task_schedule_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_done_perform',
            field=models.BooleanField(default=False),
        ),
    ]
