# Generated by Django 3.2.22 on 2024-10-03 06:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0007_auto_20241002_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_remark',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='staff_role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='staff_role_orders', to=settings.AUTH_USER_MODEL),
        ),
    ]
