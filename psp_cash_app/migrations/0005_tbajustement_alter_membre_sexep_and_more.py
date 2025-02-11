# Generated by Django 5.0.3 on 2024-03-23 17:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psp_cash_app', '0004_tbcompagnie_alter_tbcotisation_typecotisation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='tbajustement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_ajustement', models.DateTimeField(verbose_name='Date Ajustement (YYYY-MM-DD)')),
                ('memo', models.TextField()),
                ('recu_par', models.CharField(blank=True, max_length=50, null=True, verbose_name='Recu Par')),
            ],
        ),
        migrations.AlterField(
            model_name='membre',
            name='sexep',
            field=models.CharField(blank=True, choices=[('M', 'Masculin'), ('F', 'Feminin')], max_length=50, null=True, verbose_name='SEXE MEMBRE '),
        ),
        migrations.AlterField(
            model_name='tbarticle',
            name='date_expiration',
            field=models.DateTimeField(verbose_name='Date Expiration (YYYY-MM-DD)'),
        ),
        migrations.CreateModel(
            name='tbajustementarticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anc_quantite', models.FloatField(blank=True, default='0.0', null=True, verbose_name='Ancienne Quantite')),
                ('nouv_quantite', models.FloatField(blank=True, default='0.0', null=True, verbose_name='Nouvelle Quantite')),
                ('anc_cout', models.FloatField(blank=True, default='0.0', null=True, verbose_name='Ancien Cout')),
                ('nouv_cout', models.FloatField(blank=True, default='0.0', null=True, verbose_name='Nouveau Cout')),
                ('anc_prix', models.FloatField(blank=True, default='0.0', null=True, verbose_name='Ancien Prix')),
                ('nouv_prix', models.FloatField(blank=True, default='0.0', null=True, verbose_name='Nouveau Prix')),
                ('memo', models.TextField()),
                ('code_ajustement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psp_cash_app.tbajustement')),
                ('code_article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psp_cash_app.tbarticle')),
            ],
        ),
    ]
