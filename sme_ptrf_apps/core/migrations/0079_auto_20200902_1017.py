# Generated by Django 2.2.10 on 2020-09-02 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0078_remove_prestacaoconta_motivo_reabertura'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='prestacaoconta',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='prestacaoconta',
            name='conta_associacao',
        ),
    ]
