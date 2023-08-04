# Generated by Django 3.1.14 on 2023-08-04 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0345_auto_20230801_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='solicitacaoencerramentocontaassociacao',
            name='data_aprovacao',
            field=models.DateField(blank=True, null=True, verbose_name='Data de aprovação'),
        ),
        migrations.AddField(
            model_name='solicitacaoencerramentocontaassociacao',
            name='motivos_reprovacao',
            field=models.ManyToManyField(blank=True, to='core.MotivoRejeicaoEncerramentoContaAssociacao'),
        ),
    ]
