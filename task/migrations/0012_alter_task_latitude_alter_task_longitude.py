# Generated by Django 4.2.15 on 2024-08-31 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0011_alter_task_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='latitude',
            field=models.FloatField(default=13.336115),
        ),
        migrations.AlterField(
            model_name='task',
            name='longitude',
            field=models.FloatField(default=123.3302702),
        ),
    ]
