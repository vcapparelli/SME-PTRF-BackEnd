# Generated by Django 2.2.10 on 2021-12-03 08:20

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0233_analisevalorreprogramadoprestacaoconta'),
        ('dre', '0027_comissao'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembroComissao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('rf', models.CharField(max_length=10, verbose_name='RF')),
                ('nome', models.CharField(max_length=160, verbose_name='Nome')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='E-mail')),
                ('comissoes', models.ManyToManyField(related_name='membros', to='dre.Comissao', verbose_name='Comissões')),
                ('dre', models.ForeignKey(limit_choices_to={'tipo_unidade': 'DRE'}, on_delete=django.db.models.deletion.PROTECT, related_name='membros_de_comissoes', to='core.Unidade')),
            ],
            options={
                'verbose_name': 'Membro de Comissão',
                'verbose_name_plural': 'Membros de Comissões',
            },
        ),
    ]
