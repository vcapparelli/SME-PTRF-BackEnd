# Generated by Django 2.2.10 on 2021-09-02 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_remove_user_tipo_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='visoes_log',
            field=models.TextField(blank=True, help_text='Visões do usuário (audtilog)'),
        ),
    ]
