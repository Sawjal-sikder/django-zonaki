# Generated by Django 3.2.22 on 2024-10-16 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='store_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
