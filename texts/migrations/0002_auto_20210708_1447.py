# Generated by Django 3.1.12 on 2021-07-08 18:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('texts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='log',
            options={'ordering': ['-created']},
        ),
    ]
