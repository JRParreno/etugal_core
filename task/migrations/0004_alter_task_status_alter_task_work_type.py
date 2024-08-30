# Generated by Django 4.2.15 on 2024-08-21 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_alter_task_performer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('IN_PERSON', 'Pending'), ('ONLINE', 'In Progress'), ('ACCEPTED', 'Accepted'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled'), ('REJECTED', 'Rejected')], default='IN_PERSON', max_length=10, verbose_name='Task Status'),
        ),
        migrations.AlterField(
            model_name='task',
            name='work_type',
            field=models.CharField(choices=[('IN_PERSON', 'In Person'), ('ONLINE', 'Online')], default='ONLINE', max_length=10, verbose_name='Work Type'),
        ),
    ]
