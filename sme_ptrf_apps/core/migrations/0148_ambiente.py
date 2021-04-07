# Generated by Django 2.2.10 on 2021-03-08 14:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0147_auto_20210219_1110'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ambiente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('prefixo', models.CharField(blank=True, max_length=50, null=True)),
                ('nome', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name': 'Ambiente',
                'verbose_name_plural': '14.0) Ambientes',
                'unique_together': {('prefixo', 'nome')},
            },
        ),
    ]
