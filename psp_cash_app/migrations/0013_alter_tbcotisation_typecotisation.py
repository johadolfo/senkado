# Generated by Django 5.0.3 on 2024-03-25 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psp_cash_app', '0012_alter_tbcotisation_typecotisation_delete_tbemploye'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tbcotisation',
            name='typecotisation',
            field=models.CharField(blank=True, choices=[('Fonds Urgences', 'Fonds Urgences'), ('Fonds de Fonctionnement', 'Fonds de Fonctionnement'), ('Fonds de Credit', 'Fonds de Credit')], max_length=50, null=True, verbose_name='Type de Cotisation'),
        ),
    ]
