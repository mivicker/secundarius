# Generated by Django 3.2.6 on 2021-11-09 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counts', '0009_auto_20211108_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='date',
            field=models.DateField(blank=True),
        ),
    ]
