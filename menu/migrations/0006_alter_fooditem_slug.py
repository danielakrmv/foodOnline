# Generated by Django 5.0.3 on 2024-04-10 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_alter_fooditem_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fooditem',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
    ]
