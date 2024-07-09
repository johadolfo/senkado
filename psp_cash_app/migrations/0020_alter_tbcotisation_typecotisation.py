# Generated by Django 5.0.3 on 2024-04-01 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psp_cash_app', '0019_tbconfiguration_alter_membre_sexep_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbcotisation',
            name='typecotisation',
            field=models.CharField(blank=True, choices=[('Fonds Urgences', 'Fonds Urgences'), ('Fonds de Credit', 'Fonds de Credit'), ('Fonds de Fonctionnement', 'Fonds de Fonctionnement')], max_length=50, null=True, verbose_name='Type de Cotisation'),
        ),
    ]
