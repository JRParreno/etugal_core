# Generated by Django 4.2.15 on 2024-09-09 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_remove_userprofile_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='verification_status',
            field=models.CharField(choices=[('PROCESSING_APPLICATION', 'PROCESSING APPLICATION'), ('VERIFIED', 'VERIFIED'), ('REJECTED', 'REJECTED'), ('UNVERIFIED', 'UNVERIFIED')], default='UNVERIFIED', max_length=100),
        ),
    ]
