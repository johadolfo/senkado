# Generated by Django 5.0.3 on 2024-03-25 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psp_cash_app', '0011_alter_membre_sexep_alter_tbcotisation_typecotisation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbcotisation',
            name='typecotisation',
            field=models.CharField(blank=True, choices=[('Fonds de Credit', 'Fonds de Credit'), ('Fonds Urgences', 'Fonds Urgences'), ('Fonds de Fonctionnement', 'Fonds de Fonctionnement')], max_length=50, null=True, verbose_name='Type de Cotisation'),
        ),
        migrations.DeleteModel(
            name='tbemploye',
        ),
    ]
