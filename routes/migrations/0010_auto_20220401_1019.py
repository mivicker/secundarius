# Generated by Django 3.2.6 on 2022-04-01 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0009_alter_depot_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='depot',
            name='active_drivers',
            field=models.ManyToManyField(blank=True, to='routes.Driver'),
        ),
        migrations.AlterField(
            model_name='depot',
            name='date',
            field=models.DateField(blank=True, editable=False),
        ),
    ]
