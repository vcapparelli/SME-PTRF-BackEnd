# Generated by Django 2.2.10 on 2021-03-23 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0160_auto_20210323_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demonstrativofinanceiro',
            name='versao',
            field=models.CharField(choices=[('FINAL', 'final'), ('PREVIA', 'prévio')], default='FINAL', max_length=20, verbose_name='versão'),
        ),
        migrations.AlterField(
            model_name='relacaobens',
            name='versao',
            field=models.CharField(choices=[('FINAL', 'final'), ('PREVIA', 'prévio')], default='FINAL', max_length=20, verbose_name='versão'),
        ),
    ]
