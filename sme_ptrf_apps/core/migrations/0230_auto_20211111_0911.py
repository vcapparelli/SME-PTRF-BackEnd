# Generated by Django 2.2.10 on 2021-11-11 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0229_merge_20211109_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='associacao',
            name='cargo_substituto_presidente_ausente',
            field=models.CharField(blank=True, choices=[('PRESIDENTE_DIRETORIA_EXECUTIVA', 'Presidente da diretoria executiva'), ('VICE_PRESIDENTE_DIRETORIA_EXECUTIVA', 'Vice-Presidente da diretoria executiva'), ('SECRETARIO', 'Secretário'), ('TESOUREIRO', 'Tesoureiro'), ('VOGAL_1', 'Vogal 1'), ('VOGAL_2', 'Vogal 2'), ('VOGAL_3', 'Vogal 3'), ('VOGAL_4', 'Vogal 4'), ('VOGAL_5', 'Vogal 5')], default=None, max_length=65, null=True, verbose_name='Cargo substituto do presidente ausente'),
        ),
        migrations.AlterField(
            model_name='membroassociacao',
            name='cargo_associacao',
            field=models.CharField(blank=True, choices=[('PRESIDENTE_DIRETORIA_EXECUTIVA', 'Presidente da diretoria executiva'), ('VICE_PRESIDENTE_DIRETORIA_EXECUTIVA', 'Vice-Presidente da diretoria executiva'), ('SECRETARIO', 'Secretário'), ('TESOUREIRO', 'Tesoureiro'), ('VOGAL_1', 'Vogal 1'), ('VOGAL_2', 'Vogal 2'), ('VOGAL_3', 'Vogal 3'), ('VOGAL_4', 'Vogal 4'), ('VOGAL_5', 'Vogal 5'), ('PRESIDENTE_CONSELHO_FISCAL', 'Presidente do conselho fiscal'), ('CONSELHEIRO_1', 'Conselheiro 1'), ('CONSELHEIRO_2', 'Conselheiro 2'), ('CONSELHEIRO_3', 'Conselheiro 3'), ('CONSELHEIRO_4', 'Conselheiro 4')], default='Presidente da diretoria executiva', max_length=65, null=True, verbose_name='Cargo Associação'),
        ),
    ]
