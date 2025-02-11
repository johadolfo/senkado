# Generated by Django 5.0.3 on 2024-03-24 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psp_cash_app', '0005_tbajustement_alter_membre_sexep_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tbcompagnie',
            name='couleur_preferee',
            field=models.CharField(blank=True, default='#2471A3', max_length=50, verbose_name='Couleur Preferee '),
        ),
        migrations.AddField(
            model_name='tbcompagnie',
            name='couleur_text_menu',
            field=models.CharField(blank=True, default='#2471A3', max_length=50, verbose_name='Couleur Preferee '),
        ),
        migrations.AddField(
            model_name='tbcompagnie',
            name='taux_interet',
            field=models.FloatField(blank=True, default='0.0', null=True, verbose_name='Taux Interet'),
        ),
        migrations.AlterField(
            model_name='tbcotisation',
            name='typecotisation',
            field=models.CharField(blank=True, choices=[('Fonds Urgences', 'Fonds Urgences'), ('Fonds de Credit', 'Fonds de Credit'), ('Fonds de Fonctionnement', 'Fonds de Fonctionnement')], max_length=50, null=True, verbose_name='Type de Cotisation'),
        ),
    ]
