# Generated by Django 3.2.6 on 2021-11-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counts', '0006_auto_20211108_1241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='substitution',
            name='ratio',
            field=models.FloatField(),
        ),
    ]
