# Generated by Django 5.0.3 on 2024-04-05 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0002_openinghour'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='openinghour',
            options={'ordering': ('day', '-from_hour')},
        ),
    ]
