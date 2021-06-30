# Generated by Django 2.2.10 on 2021-06-30 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('receitas', '0033_receita_saida_do_recurso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receita',
            name='saida_do_recurso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receitas_saida_do_recurso', to='despesas.Despesa', verbose_name='Saída do Recurso (Despesa)'),
        ),
    ]
