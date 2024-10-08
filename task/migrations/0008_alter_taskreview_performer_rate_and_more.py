# Generated by Django 4.2.15 on 2024-08-21 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0007_alter_taskreview_performer_rate_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskreview',
            name='performer_rate',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0),
        ),
        migrations.AlterField(
            model_name='taskreview',
            name='provider_rate',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0),
        ),
    ]
