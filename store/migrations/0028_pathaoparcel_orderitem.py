# Generated by Django 3.2.22 on 2024-11-23 08:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_orderitem_pathao_consignment_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='pathaoparcel',
            name='orderItem',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pathaoparcels', to='store.orderitem'),
        ),
    ]
