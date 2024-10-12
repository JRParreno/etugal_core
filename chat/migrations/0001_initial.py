# Generated by Django 4.2.15 on 2024-09-29 08:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_profile', '0004_alter_userprofile_verification_status'),
        ('task', '0020_alter_taskreview_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('room_name', models.CharField(max_length=255)),
                ('performer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions_performer', to='user_profile.userprofile')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_sessions_provider', to='user_profile.userprofile')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_task', to='task.task')),
            ],
            options={
                'ordering': ['-updated_at'],
                'unique_together': {('task', 'provider', 'performer')},
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chat_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatsession')),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user_profile.userprofile')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]