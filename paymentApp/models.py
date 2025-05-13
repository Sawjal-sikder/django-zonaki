from django.db import models
from django_countries.fields import CountryField
from django.conf import settings


# Create your models here.
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=50, blank=True, null=True)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    city = models.CharField(max_length = 150)
    state = models.CharField(max_length = 150) 
    zip =models.CharField(max_length=100)
    phone =models.CharField(max_length=11)
    email = models.EmailField()
    order_note = models.TextField()     
    
    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = 'Billing Address'
        verbose_name_plural = 'Billing Address'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name

class ShipingAddress(models.Model):
    SHIPPING_AREA =(
        ('Inside Chittagong','Inside Chittagong'),
        ('Outside Chittagong','Outside Chittagong'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    shiping_area = models.CharField(max_length=100, choices=SHIPPING_AREA)
    delivery_type = models.CharField(max_length=15, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    city_name = models.CharField(max_length=200, blank=True, null=True)
    zone = models.CharField(max_length=15, blank=True, null=True)
    zone_name = models.CharField(max_length=200, blank=True, null=True)
    area = models.CharField(max_length=15, blank=True, null=True)
    area_name = models.CharField(max_length=200, blank=True, null=True)
    full_address = models.TextField()     
    order_note = models.TextField(blank=True, null=True) 

    class Meta:
        verbose_name = 'Shiping Address'
        verbose_name_plural = 'Shiping Address'    
    
    def __str__(self):
        return self.full_name


class BkashPayment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    paymentID  = models.CharField(max_length = 150)
    createTime = models.CharField(max_length=150)
    orgName  = models.CharField(max_length = 150)
    transactionStatus  = models.CharField(max_length = 150)
    amount = models.CharField(max_length = 150)
    currency = models.CharField(max_length = 150)
    intent = models.CharField(max_length = 150)
    merchantInvoiceNumber = models.CharField(max_length = 150)
    
    class Meta:
        verbose_name = 'Bkash Payment'
        verbose_name_plural = 'Bkash Payments'

    def __str__(self):
        return self.paymentID

class BkashPaymentExecute(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    paymentID  = models.CharField(max_length = 150)
    createTime  = models.CharField(max_length = 150)
    updateTime  = models.CharField(max_length = 150)
    trxID  = models.CharField(max_length = 150)
    transactionStatus  = models.CharField(max_length = 150)
    amount  = models.CharField(max_length = 150)
    currency  = models.CharField(max_length = 150)
    intent  = models.CharField(max_length = 150)
    merchantInvoiceNumber  = models.CharField(max_length = 150)
    customerMsisdn  = models.CharField(max_length = 150)
    

    class Meta:
        verbose_name = 'Bkash Payment Execute'
        verbose_name_plural = 'Bkash Payment Execute'

    def __str__(self):
        return  self.paymentID

class BkashPaymentRefund(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    originalTrxID = models.CharField(max_length = 150)
    refundTrxID = models.CharField(max_length = 150)
    transactionStatus = models.CharField(max_length = 150)
    amount = models.CharField(max_length = 150)
    completedTime = models.CharField(max_length = 150)
    currency = models.CharField(max_length = 150)
    charge = models.CharField(max_length = 150)

    class Meta:
        verbose_name = 'Bkash Payment Refund'
        verbose_name_plural = 'Bkash Payment Refund'

    def __str__(self):
        return self.originalTrxID
    

class BkashApi(models.Model):
    api_key = models.TextField()
    secret_key = models.TextField()
    class Meta:
        verbose_name = 'Bkash Api'
        verbose_name_plural = 'Bkash Api'

    def __str__(self):
        return self.api_key 





from django.utils import timezone

class PathaoToken(models.Model):
    access_token = models.CharField(max_length=1255)
    refresh_token = models.CharField(max_length=1255, blank=True, null=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        """Check if the access token has expired."""
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"PathaoToken(access_token={self.access_token[:10]}, expires_at={self.expires_at})"


class PathaoStores(models.Model):
    store_id = models.IntegerField(unique=True)
    store_name = models.CharField(max_length=255)
    zone_id = models.IntegerField()
    store_address = models.TextField()
    city_id = models.IntegerField()
    hub_id = models.IntegerField()
    is_active = models.BooleanField()
    is_default_return_store = models.BooleanField()
    is_default_store = models.BooleanField()

    def __str__(self):
        return self.store_name