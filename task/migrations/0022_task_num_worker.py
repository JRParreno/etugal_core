# Generated by Django 4.2.13 on 2024-12-05 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0021_alter_task_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='num_worker',
            field=models.IntegerField(default=1),
        ),
    ]