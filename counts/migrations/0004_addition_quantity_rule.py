# Generated by Django 3.2.6 on 2021-11-08 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counts', '0003_auto_20211028_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='addition',
            name='quantity_rule',
            field=models.CharField(default='111', max_length=3),
        ),
    ]