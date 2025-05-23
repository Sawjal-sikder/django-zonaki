# Generated by Django 3.2.22 on 2024-10-01 04:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_orderitem_flashsale'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returnproduct',
            name='product_image',
        ),
        migrations.AddField(
            model_name='returnproduct',
            name='remove_from_customer',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='returnproduct',
            name='return_charge',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='returnproduct',
            name='return_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='returnproduct',
            name='return_request_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.RemoveField(
            model_name='returnproduct',
            name='items',
        ),
        migrations.AddField(
            model_name='returnproduct',
            name='items',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.orderitem'),
        ),
        migrations.AlterField(
            model_name='returnproduct',
            name='return_reason',
            field=models.CharField(choices=[('', '-- Select Reason --'), ('item_is_defective_or_not_working', 'Item is defective or not working'), ('component_or_accessory_is_missing_from_the_item', 'Component or accessory is missing from the item'), ('item_has_missing_freebie', 'Item has missing freebie'), ('item_does_not_match_description_or_picture', 'Item does not match description or picture'), ('i_did not_order_this_size', 'I did not order this size'), ('i_received_the_wrong_item', 'I received the wrong item'), ('item_does_not_fit_me', 'Item does not fit me'), ('do not_want_the_item_anymore', 'Do not want the item anymore'), ('item_is_damaged/broken/has_dent_or_scratches', 'Item is damaged/broken/has dent or scratches')], max_length=100),
        ),
        migrations.CreateModel(
            name='ReturnProductImages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(max_length=1000, upload_to='return-product-img')),
                ('return_product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='returnproductimages', to='store.returnproduct')),
            ],
        ),
    ]
