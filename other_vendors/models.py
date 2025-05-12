from django.db import models
from django.db.models.signals import post_save
from django.db.models import Sum
from django.conf import settings
from django.contrib.auth import get_user_model

from store.models import OrderItem, Order

class Country(models.Model):
    name=models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name
    
class Division(models.Model):
    name=models.CharField(max_length=100)
    country=models.ForeignKey(Country,on_delete=models.CASCADE, related_name='divisions')
    
    def __str__(self):
        return self.name
    
class District(models.Model):
    name=models.CharField(max_length=100)
    division=models.ForeignKey(Division,on_delete=models.CASCADE, related_name='districts')
    
    def __str__(self):
        return self.name
    
class SubDistrict(models.Model):
    name=models.CharField(max_length=100)
    district=models.ForeignKey(District,on_delete=models.CASCADE, related_name='subdistricts')
    
    class Meta:
        verbose_name = 'Sub District'
        verbose_name_plural = 'Sub Districts'
    
    def __str__(self):
        return self.name
    

class VendorInformation(models.Model):
    ID_TYPE = [
        ('NID','NID'), 
        ('Passport', 'Passport'), 
        ('Driving Licence', 'Driving Licence')
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vendorinformation")
    store_id = models.CharField(max_length=300, blank=True,null=True)
    phone1 = models.CharField(
        verbose_name='Mobile Banking Phone Number (e.g., Bkash, Nagad, Rocket, or others)',
        max_length=15,
        blank=True, 
        null=True,
        help_text='Enter your mobile banking phone number for Bkash, Nagad, Rocket, or any other service'
    )
    phone2 = models.CharField(
        verbose_name='Mobile Banking Phone Number (e.g., Bkash, Nagad, Rocket, or others)', 
        max_length=15, 
        blank=True, 
        null=True,
        help_text='Enter your mobile banking phone number for Bkash, Nagad, Rocket, or any other service'
    )
    id_type = models.CharField(max_length=20, choices=ID_TYPE, default='NID')
    vendor_image = models.ImageField(upload_to='vendor_image/',default='no_img.png', blank=True, null=True)
    Nid_number = models.CharField(max_length=20)
    NID_copy_1 = models.FileField()
    NID_copy_2 = models.FileField()
    
    shop_name = models.CharField(max_length=120)
    address = models.CharField(max_length=300)
    country = models.CharField(max_length=20)
    division = models.CharField(max_length=20)
    district = models.CharField(max_length=20)
    upazila = models.CharField(max_length=20)
    
    warehouse_address = models.BooleanField(default=True)   
    w_address = models.CharField(max_length=300, blank=True,null=True)
    w_division = models.CharField(max_length=20,blank=True,null=True)
    w_district = models.CharField(max_length=20,blank=True,null=True)
    w_upazila = models.CharField(max_length=20,blank=True,null=True)
    
    return_address = models.BooleanField(default=True)
    r_address = models.CharField(max_length=300, blank=True,null=True)
    r_division = models.CharField(max_length=20,blank=True,null=True)
    r_district = models.CharField(max_length=20,blank=True,null=True)
    r_upazila = models.CharField(max_length=20,blank=True,null=True)
    
    account_title = models.CharField(max_length=30)
    account_number = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=30)
    bank_branch_name = models.CharField(max_length=30)
    routing_number = models.CharField(max_length=30)
    cheque_copy = models.FileField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def max_order(self, *args, **kwargs):
        orders = Order.objects.filter(ordered=True).prefetch_related('items__item__user')
        return orders.filter(items__item__user=self.user).count()

    def total_sales(self, *args, **kwargs):
        order_items = OrderItem.objects.filter(ordered=True).prefetch_related('item__user')
        total_sales = sum(item.vendor_total_price() for item in order_items if item.item.user == self.user)
        return total_sales


    class Meta:
        verbose_name_plural = "Vendor Profile"
        ordering = ("user__email",)

    def __str__(self):
        return self.user.email


def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_vendor == True:
        VendorInformation.objects.create(user=instance)

user = get_user_model()
post_save.connect(create_profile, sender=user)



class VendorPayment(models.Model):
    STATUS = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Complete', 'Complete'),
        ('Cancel', 'Cancel')
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ManyToManyField(OrderItem)
    message = models.TextField(max_length=100)
    status = models.CharField(max_length=150, choices= STATUS, default='Pending')
    remark = models.TextField(null=True, blank=True)
    document_file = models.FileField(upload_to="vendor-payment/document",blank=True, null=True)
    image = models.ImageField(upload_to="vendor-payment/images",blank=True, null=True)
    transaction_informations = models.TextField(blank=True, null=True)
    request_date = models.DateTimeField(auto_now_add=True)
    complete_date = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_amount(self):
        total = 0
        for i in self.product.all():
            if i.item.discount_price:
                total += i.item.discount_price
            else:
                total += i.item.price
        return total

    def get_commission(self):
        total = 0
        for i in self.product.all():
            if i.item.categoris.commission:
                total += i.item.categoris.commission
        return total
    
    def after_commision_total(self):
        commision = self.get_amount() * (self.get_commission() / 100)
        print(commision)
        total =  float(self.get_amount()) - float(commision)
        print(total)
        return total
    
    def order_items(self):
        items = list(self.product.all())
        return ',<br>'.join([str(item) for item in items])
    
    def order_ids(self):
        products = self.product.prefetch_related('order').all()
        orders = set()
        for product in products:
            for order in product.order.all():
                orders.add(str(order.id))
        return ',<br>'.join(sorted(orders))



        