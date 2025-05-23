# Generated by Django 3.2.22 on 2024-10-16 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0020_auto_20241016_1134'),
    ]

    operations = [
        migrations.CreateModel(
            name='PathaoParcel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consignment_id', models.CharField(blank=True, max_length=150, null=True)),
                ('place_date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pathaoparcels', to='store.order')),
            ],
        ),
    ]
