# Generated by Django 2.2.10 on 2022-11-10 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0291_auto_20221110_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analiselancamentoprestacaoconta',
            name='status_realizacao',
            field=models.CharField(choices=[('PENDENTE', 'Pendente'), ('REALIZADO', 'Realizado'), ('JUSTIFICADO', 'Justificado'), ('REALIZADO_JUSTIFICADO', 'Realizado e justificado'), ('REALIZADO_PARCIALMENTE', 'Realizado parcialmente'), ('JUSTIFICADO_PARCIALMENTE', 'Justificado parcialmente'), ('REALIZADO_JUSTIFICADO_PARCIALMENTE', 'Realizado e justificado parcialmente')], default='PENDENTE', max_length=40, verbose_name='Status de realização'),
        ),
    ]
