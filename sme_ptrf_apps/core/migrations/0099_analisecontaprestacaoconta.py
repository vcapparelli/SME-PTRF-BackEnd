# Generated by Django 2.2.10 on 2020-10-01 09:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0098_merge_20200930_1637'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnaliseContaPrestacaoConta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('data_extrato', models.DateField(blank=True, null=True, verbose_name='data doe extrato')),
                ('saldo_extrato', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='saldo do extrato')),
                ('conta_associacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='analises_de_conta_da_conta', to='core.ContaAssociacao')),
                ('prestacao_conta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analises_de_conta_da_prestacao', to='core.PrestacaoConta')),
            ],
            options={
                'verbose_name': 'Análise de conta de prestação de contas',
                'verbose_name_plural': '09.8) Análises de contas de prestações de contas',
            },
        ),
    ]
