# Generated by Django 5.0.3 on 2024-04-06 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_tax'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tax',
            options={'verbose_name_plural': 'tax'},
        ),
        migrations.AddField(
            model_name='tax',
            name='tax_value',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=4),
        ),
        migrations.AlterField(
            model_name='tax',
            name='tax_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, verbose_name='Tax Percentage (%)'),
        ),
    ]