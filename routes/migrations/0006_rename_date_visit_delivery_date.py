# Generated by Django 3.2.6 on 2021-10-21 00:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0005_alter_lastcachedate_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='visit',
            old_name='date',
            new_name='delivery_date',
        ),
    ]
