# Generated by Django 2.2.10 on 2021-05-10 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0169_auto_20210510_1057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unidade',
            name='tipo_unidade',
            field=models.CharField(choices=[('ADM', 'ADM'), ('DRE', 'DRE'), ('IFSP', 'IFSP'), ('CMCT', 'CMCT'), ('CECI', 'CECI'), ('CEI', 'CEI'), ('CEMEI', 'CEMEI'), ('CIEJA', 'CIEJA'), ('EMEBS', 'EMEBS'), ('EMEF', 'EMEF'), ('EMEFM', 'EMEFM'), ('EMEI', 'EMEI'), ('CEU', 'CEU'), ('CEU CEI', 'CEU CEI'), ('CEU EMEF', 'CEU EMEF'), ('CEU EMEI', 'CEU EMEI'), ('CEU CEMEI', 'CEU CEMEI'), ('CEI DIRET', 'CEI DIRET')], default='ADM', max_length=10),
        ),
    ]
