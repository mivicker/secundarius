# Generated by Django 3.2.6 on 2021-11-09 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counts', '0010_alter_warehouse_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warehouse',
            name='date',
            field=models.DateField(blank=True, editable=False),
        ),
    ]
