# Generated by Django 3.2.6 on 2021-10-20 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('routes', '0002_visit_driver'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationshipcache',
            name='driver',
            field=models.CharField(default='', max_length=50),
        ),
    ]