# Generated by Django 2.2.10 on 2020-10-22 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20201022_1906'),
    ]

    operations = [
        migrations.AddField(
            model_name='grupo',
            name='visoes',
            field=models.ManyToManyField(blank=True, to='users.Visao'),
        ),
    ]
