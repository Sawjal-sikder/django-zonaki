from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if not email and not phone:
            raise ValueError('The Email or Phone field must be set')
        if email:
            email = self.normalize_email(email)
            extra_fields.setdefault('email', email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email=email, phone=phone, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=30, null=True, blank=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def max_order(self, from_date=None, to_date=None, *args, **kwargs):
        orders = self.orders.filter(ordered=True)
        if from_date:
            orders = orders.filter(ordered_date__gte=from_date)
        if to_date:
            orders = orders.filter(ordered_date__lte=to_date)
        return orders.count()

    def total_buys(self, from_date=None, to_date=None, *args, **kwargs):
        orders = self.orders.filter(ordered=True).prefetch_related('items')
        if from_date:
            orders = orders.filter(ordered_date__gte=from_date)
        if to_date:
            orders = orders.filter(ordered_date__lte=to_date)

        total_sales = 0
        for order in orders:
            for item in order.items.all():
                total_sales += item.vendor_total_price()
        return total_sales

    def __str__(self):
        return self.full_name or self.email or self.phone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to="profilepicture", default='no_img.png')
    date_of_birthday = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    store_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.full_name or self.user.email or self.user.phone

    class Meta:
        verbose_name_plural = "Customer Profile"
        ordering = ("user__id","user__full_name")


def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_active:
        Profile.objects.create(user=instance)

User = get_user_model()
post_save.connect(create_profile, sender=User)
