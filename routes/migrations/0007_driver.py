# Generated by Django 3.2.6 on 2021-10-28 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0006_rename_date_visit_delivery_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(max_length=50)),
                ('active', models.BooleanField()),
            ],
        ),
    ]