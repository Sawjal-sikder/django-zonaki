from django.db import models
import string
import random
from django.db import IntegrityError
from django.shortcuts import reverse
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.conf import settings
from django.core.validators import MaxValueValidator
from paymentApp.models import *
from django.utils import timezone
from PIL import Image
from userapp.models import User
from django.utils.text import slugify
from unidecode import unidecode
from datetime import timedelta


# Create your models here.
class WebsiteInformation(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='websiteLogo')
    bkash_number = models.CharField(max_length=15, null=True, blank=True)
    nagad_number = models.CharField(max_length=15, null=True, blank=True)
    rocket_number = models.CharField(max_length=15, null=True, blank=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Website Information"
        verbose_name_plural = "Website Informations"

    def __str__(self):
        return self.name


class PhoneNumber(models.Model):
    website = models.ForeignKey(
        WebsiteInformation, on_delete=models.CASCADE, related_name='phones')
    phone = models.CharField(max_length=15)


class EmailAddress(models.Model):
    website = models.ForeignKey(
        WebsiteInformation, on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField()


class CompanyAddress(models.Model):
    website = models.ForeignKey(
        WebsiteInformation, on_delete=models.CASCADE, related_name='addresses')
    address = models.CharField(max_length=255)


class ProductCategory(models.Model):
    category_name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    img = models.ImageField(upload_to='CategoryImg', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    commission = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    sl_no = models.PositiveIntegerField(default=0, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def get_parent_categories():
        """Retrieves only parent categories (those without a parent)."""
        parent_categories = ProductCategory.objects.filter(parent__isnull=True)
        return parent_categories

    def get_category_update_url(self):
        return reverse('category-update', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.category_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='brandImg')
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'

    def __str__(self):
        return self.name

    def get_brand_update_url(self):
        return reverse('brand-update', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Banner(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='bannerImg')
    http_url_link = models.URLField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Banner'
        verbose_name_plural = 'Banners'

    def __str__(self):
        return self.title


class PriceRange(models.Model):
    price_range = models.CharField(max_length=100, unique=True)
    ordering = models.IntegerField()

    class Meta:
        ordering = ['ordering']
        verbose_name = 'Price Range'
        verbose_name_plural = 'Price Range'

    def __str__(self):
        return self.price_range


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(Color, self).save(*args, **kwargs)


class Size(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name.upper()


class Product(models.Model):
    RETURN_TYPES = [
        ('', '-- Select Return Type --'),
        ('no_return', 'No Return'),
        ('7_days', '7 Days Return'),
        ('15_days', '15 Days Return'),
        ('30_days', '30 Days Return'),
        ('60_days', '60 Days Return'),
    ]

    WARRANTY_TYPES = [
        ('', '-- Select Warranty Type --'),
        ('no_warranty', 'No Warranty'),
        ('3_months', '3 Months Warranty'),
        ('6_months', '6 Months Warranty'),
        ('1_year', '1 Year Warranty'),
        ('2_years', '2 Years Warranty'),
        ('3_years', '3 Years Warranty'),
        ('lifetime', 'Lifetime Warranty'),
    ]
    user = models.ForeignKey(
        User, related_name='products_models', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    parent_code = models.CharField(max_length=150)
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, default=0.001)
    slug = models.SlugField(max_length=100, blank=True, null=True, unique=True)
    categoris = models.ForeignKey(
        ProductCategory, verbose_name='Product Category', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='ProductImg',
                              default='ProductImg/noimg.jpg')
    hover_image = models.ImageField(
        upload_to='ProductImg', default='noimg.jpg', blank=True, null=True)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    product_purchase_price = models.IntegerField()
    sort_discription = RichTextUploadingField(blank=True, null=True)
    discription = RichTextUploadingField()
    aditional_discription = RichTextUploadingField(blank=True, null=True)
    # flash_sale_add_and_expire_date = models.DateTimeField(
    #     blank=True, null=True)
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, blank=True, null=True)
    price_range = models.ForeignKey(
        PriceRange, on_delete=models.CASCADE, blank=True, null=True)
    meta_title = models.CharField(blank=True, null=True, max_length=100)
    meta_keyword = models.CharField(blank=True, null=True, max_length=100)
    return_type = models.CharField(
        max_length=20, choices=RETURN_TYPES, default='no_return')
    warranty_type = models.CharField(
        max_length=20, choices=WARRANTY_TYPES, default='no_warranty')
    
    free_delivery = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def saving_price(self):
        return self.price - self.discount_price

    def saving_percent(self):
        return self.saving_price() / self.price * 100

    def total_price(self):
        flashsale_product = self.flashsale_products.first()
        if flashsale_product and flashsale_product.flashsale_price:
            return flashsale_product.flashsale_price
        elif self.discount_price:
            return self.discount_price
        else:
            return self.price

    def get_product_reveneu(self):
        return self.total_price() - self.product_purchase_price

    def save(self, *args, **kwargs):
        try:
            self.slug = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(49))
            super().save(*args, **kwargs)
            img = Image.open(self.image.path)
            if img.height > 630 or img.width > 1300:
                new_img = (700, 700)
                img.thumbnail(new_img)
                img.save(self.image.path)
        except IntegrityError:
            self.save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def calculate_commission(self):
        if self.categoris and self.categoris.commission is not None:
            if self.discount_price:
                commission = self.discount_price * \
                    (self.categoris.commission/100)
            else:
                commission = self.price * (self.categoris.commission/100)
            return commission
        return 0

    def get_product_update_url(self):
        return reverse('product-update', kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse('remove_form_cart', kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', kwargs={'slug': self.slug})

    def get_buy_now_url(self):
        return reverse('buy_now', kwargs={'slug': self.slug})

    def get_review_list(self):
        reviews = ProductReview.objects.filter(
            product=self, approve_status=True)
        return reviews

    def get_avg_rating(self):
        reviews = ProductReview.objects.filter(
            product=self, approve_status=True)
        count = len(reviews)
        sum = 0
        for rvw in reviews:
            sum += rvw.rating
        if count != 0:
            return (sum*20/count)

    def get_rating_count(self):
        reviews = ProductReview.objects.filter(
            product=self, approve_status=True)
        count = len(reviews)
        return count

    @property
    def stock_quantity(self):
        total_quantity = self.variation_set.aggregate(
            total_quantity=models.Sum('quantity'))['total_quantity']
        return total_quantity if total_quantity is not None else 0

    @stock_quantity.setter
    def stock_quantity(self, value):
        if value < 0:
            raise ValueError("Stock quantity cannot be negative")
        # You can distribute the stock quantity across the variations
        variations = self.variation_set.all()
        total_variations = variations.count()
        if total_variations == 0:
            raise ValueError(
                "No variations available to set the stock quantity")
        # Calculate the quantity to set for each variation
        quantity_per_variation = value // total_variations
        remainder = value % total_variations
        for variation in variations:
            variation.quantity = quantity_per_variation
            variation.save()
        # Distribute any remaining quantity
        for i, variation in enumerate(variations):
            if i < remainder:
                variation.quantity += 1
                variation.save()

    def get_sizes(self):
        sizes = self.variation_set.exclude(size__isnull=True).values_list(
            'size__name', flat=True).distinct()
        return list(sizes)

    def get_colors(self):
        colors = self.variation_set.exclude(color__isnull=True).values_list(
            'color__name', flat=True).distinct()
        return list(colors)


    def __str__(self):
        return self.product_name
    
    class Meta:
        ordering = ['product_name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class ProductImgGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.FileField(upload_to='ProductImgGallery')

    def __str__(self):
        return self.product.slug


class VariationManager(models.Manager):
    def all(self):
        return super(VariationManager, self).filter(is_active=True)

    def sizes(self):
        return self.all().filter(category='size')

    def colors(self):
        return self.all().filter(category='color')


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    color = models.ForeignKey(
        Color, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(
        Size, on_delete=models.SET_NULL, null=True, blank=True)
    variation_code = models.CharField(max_length=120, null=True, blank=True)
    image_for_color = models.ImageField(
        upload_to='ColorImage', blank=True, null=True)
    video_url = models.URLField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.variation_code:
            if self.color and self.size and self.product.parent_code:
                self.variation_code = f"{self.product.parent_code}-{self.size.name}-{self.color.name}"
            elif self.size and self.product.parent_code:
                self.variation_code = f"{self.product.parent_code}-{self.size.name}"
            elif self.color and self.product.parent_code:
                self.variation_code = f"{self.product.parent_code}-{self.color.name}"
            else:
                self.variation_code = self.product.product_name
        super().save(*args, **kwargs)

    def __str__(self):
        if self.color and self.size:
            return f"Size -{self.size.name} and Color -{self.color.name}"
        else:
            return self.product.product_name


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    coupon = models.ForeignKey('Coupon', on_delete=models.CASCADE, blank=True, null=True)
    product_new_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    variation = models.ManyToManyField(Variation)
    flashsale = models.ForeignKey('FlashSaleProduct', on_delete=models.CASCADE, null=True, blank=True)
    # pathao start
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pathao_consignment_id = models.CharField(max_length=150, blank=True, null=True)
    pathao_status = models.CharField(max_length=150, blank=True, null=True)
    # pathao end

    def saving_price(self):
        if self.product_new_price:
            if self.item.discount_price:
                return (self.product_new_price * self.quantity) - (self.item.discount_price * self.quantity)
            else:
                return (self.item.price * self.quantity) - (self.product_new_price * self.quantity)
        else:
            return (self.item.price * self.quantity) - (self.item.discount_price * self.quantity)
        
    def saving_percent(self):
        if self.product_new_price :
            return (self.saving_price()) / (self.item.discount_price * self.quantity) * 100
        else:
            return (self.saving_price()) / (self.item.price * self.quantity) * 100

    """Using for pathao percel amount {paymentApp views:(create_pathao_order)} and many more places """
    def get_subtotal(self):
        if self.product_new_price:
                return self.product_new_price * self.quantity
        elif self.flashsale:
            return self.flashsale.flashsale_price * self.quantity
        elif self.item.discount_price:
            return self.item.discount_price * self.quantity
        else:
            return self.item.price * self.quantity
        
    def get_item_price(self):
        if self.product_new_price:
                return self.product_new_price
        elif self.flashsale:
            return self.flashsale.flashsale_price
        else:
            return self.item.total_price()

    """ {Dashboard app html(order-detail)} """
    def get_subtotal_with_shipping_charge(self):
        if self.item.free_delivery:
            return self.get_subtotal()
        else:
            return self.shipping_charge + self.get_subtotal()

    def vendor_total_price(self):
        if self.product_new_price:
            return self.product_new_price * self.quantity
        elif self.item.discount_price:
            return self.item.discount_price * self.quantity
        else:
            return self.item.price * self.quantity

    def get_purchase_price_subtotal(self):
        return self.item.product_purchase_price * self.quantity

    def __str__(self):
        return f"{self.quantity} of {self.item.product_name}"

    class Meta:
        ordering = ['-id']
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


class VendorOrderItems(models.QuerySet):
    def vendor_items(self, id=None):
        """Group order items by users, optionally filtering by order ID."""
        items_list = {}

        # Filter by specific order ID if provided, otherwise use all orders
        orders = self.filter(id=id) if id else self

        # Iterate over the filtered orders
        for order in orders:
            for item in order.items.all():
                user = item.item.user

                # Initialize the user's entry if not already present
                if user not in items_list:
                    items_list[user] = {
                        'items': [],
                        'total_item_count': 0
                    }

                # Add the item to the user's list and update the total count
                items_list[user]['items'].append({
                    'item_id': item.id,
                    'item': item,
                })
                items_list[user]['total_item_count'] += 1
        return items_list



class Order(models.Model):
    ORDER_STATUS = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('On the way', 'On the way'),
        ('Complete', 'Complete'),
        ('Return', 'Return'),
        ('Cancel', 'Cancel')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    staff_role = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='staff_role_orders')
    staff_roled_date= models.DateTimeField(blank=True, null=True)
    items = models.ManyToManyField(OrderItem, related_name='order')
    order_status = models.CharField(max_length=150, choices=ORDER_STATUS, default='Pending')
    total_order_amount = models.CharField(max_length=150, blank=True, null=True) # for amount my senior made charfield not (Decimel or Integer)
    paid_amount = models.CharField(max_length=150, default=0) # for amount my senior made charfield not (Decimel or Integer)
    due_amount = models.CharField(max_length=150, default=0) # for amount my senior made charfield not (Decimel or Integer)
    ordered = models.BooleanField(default=False)
    orderId = models.CharField(max_length=150, blank=True, null=True)
    paymentId = models.CharField(max_length=150, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(ShipingAddress, on_delete=models.CASCADE, blank=True, null=True)
    total_shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_option = models.CharField(max_length=150)
    
    # pathao start
    pathao_order_status = models.CharField(max_length=200, blank=True, null=True, default='Pending')
    merchant_order_id = models.CharField(max_length=150, blank=True, null=True)
    consignment_id = models.CharField(max_length=150, blank=True, null=True)
    # pathao end
    
    # redx_percel_traking_number = models.CharField(
    #     max_length=150, blank=True, null=True)
    # others_transport_trakink_url = models.URLField(
    #     max_length=200, blank=True, null=True)
    
    order_remark = models.TextField(blank=True, null=True)
    order_read_status = models.BooleanField(default=False)
    ordered_date = models.DateTimeField(auto_now_add=True)
    order_complate_date = models.DateTimeField(auto_now=True)

    objects = VendorOrderItems.as_manager()

    def get_purchase_price_total(self):
        total = 0
        for i in self.items.all():
            total += i.get_purchase_price_subtotal()
        return total

    def get_total(self):
        total = 0
        for i in self.items.all():
            total += i.get_subtotal()
        return total

    def get_total_sale(self):
        total = 0
        for i in self.items.all():
            total += i.get_subtotal()
        return total

    def get_total_weight_in_grams(self):
        total_weight_grams = 0
        for item in self.items.all():
            total_weight_grams += item.item.weight * item.quantity * 1000
        return total_weight_grams

    # def only_shiping_charge_payment(self):
    #     if self.shipping_address.shiping_area == 'Inside Chittagong':
    #         if self.get_total_weight_in_grams() <= 150:
    #             return 50
    #         elif 200 <= self.get_total_weight_in_grams() <= 500:
    #             return 60
    #         elif 500 < self.get_total_weight_in_grams() <= 1000:
    #             return 70
    #         else:
    #             charge = 120
    #             additional_weight = self.get_total_weight_in_grams() - 1000
    #             additional_charge = ((additional_weight - 1) // 1000 + 1) * 20
    #             return charge + additional_charge
    #     else:
    #         if self.get_total_weight_in_grams() <= 150:
    #             return 150
    #         elif 200 <= self.get_total_weight_in_grams() <= 1000:
    #             return 170
    #         else:
    #             charge = 150
    #             additional_weight = self.get_total_weight_in_grams() - 1000
    #             additional_charge = ((additional_weight - 1) // 1000 + 1) * 20
    #             return charge + additional_charge
    
    """ using in methods: (get_delivery_amount) """
    def get_free_delivery_amount(self):
        total = 0
        for i in self.items.all():
            if i.item.free_delivery:
                total += i.shipping_charge
        return total
    
    """ {store app html:(checkout)} """
    def get_delivery_amount(self):
        return self.total_shipping_amount - self.get_free_delivery_amount()
    
    def coupon_without_shipingcharge(self):
        total = 0
        for i in self.items.all():
            total += i.get_subtotal()
        if self.coupon:
            if self.coupon.coupon_type == 'Percentage':
                discount = (self.coupon.amount_or_percentage / 100) * total
                total -= discount
            elif self.coupon.coupon_type == 'Amount':
                total -= self.coupon.amount_or_percentage
        return max(total, 0)

    def coupon_saving_price(self):
        total_saving = 0
        if self.coupon_without_shipingcharge():
            for i in self.items.all():
                if i.item.discount_price:
                    total_saving += (self.coupon_without_shipingcharge() * i.quantity) - (i.item.discount_price * i.quantity)
        return total_saving

    """Using this into pathao order parcel create paymentApp views:(create_pathao_order)"""
    def coupon_price(self):
        if self.coupon:
            if self.coupon.coupon_type == "Amount":
                return self.coupon.amount_or_percentage
            else:
                total = 0
                for i in self.items.all():
                    total += i.get_subtotal()
                return (self.coupon.amount_or_percentage / 100) * total
        else:
            return 0

    def order_coupon_saving_percent(self):
        total_saving = self.coupon_saving_price() 
        total_price = 0  
        for i in self.items.all():
            total_price += i.item.discount_price * i.quantity if i.item.discount_price else i.item.price * i.quantity
        if total_price > 0: 
            return (total_saving / total_price) * 100
        return 0
    
    """ using in methods: (total) """
    def get_total_with_coupon(self):
        total = 0
        for i in self.items.all():
            total += i.get_subtotal()
        if self.coupon:
            if self.coupon.coupon_type == 'Percentage':
                discount = (self.coupon.amount_or_percentage / 100) * total
                total -= discount
            elif self.coupon.coupon_type == 'Amount':
                total -= self.coupon.amount_or_percentage
        total += self.get_delivery_amount()
        return max(total, 0)
    
    """ using in methods: (total) """
    def get_total_with_shiping_charge(self):
        total = 0
        for i in self.items.all():
            total += i.get_subtotal()
        total += self.get_delivery_amount()
        return total
    
    """{store app html:(checkout)}"""
    def total(self):
        if self.coupon:
            return self.get_total_with_coupon()
        else:
            return self.get_total_with_shiping_charge()

    def total_paid_amount(self):
        return self.total() - int(self.paid_amount)

    def calculate_return_duration(self):
        RETURN_TYPES = {
            'no_return': timedelta(days=0),
            '7_days': timedelta(days=7),
            '15_days': timedelta(days=15),
            '30_days': timedelta(days=30),
            '60_days': timedelta(days=60)
        }
        return_duration = timedelta(days=0)
        for order_item in self.items.all():
            product = order_item.item
            return_type = product.return_type
            if return_type in RETURN_TYPES:
                return_duration = max(
                    return_duration, RETURN_TYPES[return_type])
        current_date = timezone.now().date()
        order_completion_date = self.order_complate_date.date()
        days_since_completion = (current_date - order_completion_date).days
        remaining_return_days = max(
            timedelta(days=0), return_duration - timedelta(days=days_since_completion))
        return remaining_return_days.days

    def __str__(self):
        return f"Order #{self.id} - {self.user.phone} - {self.user.email}"
     
    class Meta:
        ordering = ['-id']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class Coupon(models.Model):
    COUPON_TYPE = (
        ('Percentage', 'Percentage'),
        ('Amount', 'Amount')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPE, blank=True, null=True)
    code = models.CharField(max_length=15)
    amount_or_percentage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now)
    max_value = models.IntegerField(validators=[MaxValueValidator(100)], verbose_name='Coupon Quantity', null=True)
    minimum_price_range = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    used = models.IntegerField(default=0)
    coupon_user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='coupons', blank=True)
    product = models.ManyToManyField(Product, related_name='coupons', blank=True)
    is_verified = models.BooleanField(default=False)


    def _str_(self):
        return self.code

    def get_coupon_update_url(self):
        return reverse('coupon-update', kwargs={'pk': self.pk})
    
    def coupon_types(self):
        if self.coupon_type == "Percentage":
            return f"{int(self.amount_or_percentage)}%"
        else:
            return f"{int(self.amount_or_percentage)}Tk"



class PathaoParcel(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='pathaoparcels')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='pathaoparcels', null=True)
    consignment_id = models.CharField(max_length=150, blank=True, null=True)
    place_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class WhishLIst(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    wish_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    slug = models.CharField(max_length=100, unique=True, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlist'

    def __str__(self):
        return self.user.email + ' ' + self.wish_product.product_name

    def save(self, *args, **kwargs):
        try:
            self.slug = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(49))
            super().save(*args, **kwargs)
        except IntegrityError:
            self.save(*args, **kwargs)


# class FlashSale(models.Model):
#     title = models.CharField(max_length=150)
#     FlashSaleOn_date = models.DateTimeField(default=timezone.now)
#     FlashSale_expire_date = models.DateTimeField()

#     class Meta:
#         verbose_name = 'FlashSale'
#         verbose_name_plural = 'FlashSales'

#     def __str__(self):
#         return str(self.FlashSale_expire_date)

class FlashSale(models.Model):
    title = models.CharField(max_length=150)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    # def save(self, *args, **kwargs):
    #     if self.start_time <= timezone.now() <= self.end_time:
    #         self.is_active = True
    #     else:
    #         self.is_active = False
    #     super().save(*args, **kwargs)

    def expired_date_check(self):
        return False if self.start_time <= timezone.now() <= self.end_time else True
    
    class Meta:
        verbose_name = 'FlashSale'
        verbose_name_plural = 'FlashSales'

    def __str__(self):
        return str(self.end_time)


class FlashSaleProduct(models.Model):
    flash_sale = models.ForeignKey(
        FlashSale, related_name='flashsale_products', on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(
        Product, related_name='flashsale_products', on_delete=models.CASCADE, blank=True, null=True)
    variation = models.ForeignKey(
        Variation, related_name='flashsale_products', on_delete=models.CASCADE, blank=True, null=True)
    flashsale_price = models.PositiveIntegerField(null=True, blank=True)
    stock = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)

    def available_stock(self):
        return self.stock - self.sold

    def __str__(self):
        return f"{self.flash_sale.title}"
    
    def get_product_price(self):
        return self.product.discount_price if self.product.discount_price else self.product.price

    def sale_saving_price(self):
        if self.product.discount_price:
            total = self.product.discount_price - self.flashsale_price
        else:
            total = self.product.price - self.flashsale_price
        return total

    def sale_saving_percent(self):
        return (self.sale_saving_price() / self.get_product_price()) * 100


class Campaign(models.Model):
    campaign_name = models.CharField(max_length=150)
    img = models.ImageField(upload_to="campain-img" ,blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    role_no = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.campaign_name))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Campaign Category'
        verbose_name_plural = 'Campaign Categories'

    def __str__(self):
        return self.campaign_name


class CampaignProduct(models.Model):
    campaign_category = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Campaign Product'
        verbose_name_plural = 'Campaign Products'

    def __str__(self):
        return self.campaign_category.campaign_name + " / " + self.product.product_name


class DealOfTheDayProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Deal Of The Day'
        verbose_name_plural = 'Deal Of The Days'

    def __str__(self):
        return self.product.product_name


class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    RATING = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    rating = models.IntegerField(choices=RATING, default=5)
    review = models.TextField()
    image = models.ImageField(upload_to='ReviewImg', blank=True, null=True)
    approve_status = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Product Review'
        verbose_name_plural = 'Product Reviews'

    def __str__(self):
        return self.user.email


class ConductData(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.IntegerField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    view_status = models.BooleanField(default=False)

    def __str__(self):
        return self.name + ' /' + self.email

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['-id']


class PrivacyPolicy(models.Model):
    all_information = RichTextField()

    class Meta:
        verbose_name = 'Privacy Policy'
        verbose_name_plural = 'Privacy Policy'

    def __str__(self):
        return 'Privacy Policy'


class TermsAndConditions(models.Model):
    all_information = RichTextField()

    class Meta:
        verbose_name = 'Terms & Conditions'
        verbose_name_plural = 'Terms & Conditions'

    def __str__(self):
        return 'Terms & Conditions'


class Mission(models.Model):
    all_information = RichTextField()

    def __str__(self):
        return 'Mission'


class Vision(models.Model):
    all_information = RichTextField()

    def __str__(self):
        return 'Vision'


class Returns_Policy(models.Model):
    all_information = RichTextField()

    class Meta:
        verbose_name = 'Returns Policy'
        verbose_name_plural = 'Returns Policy'

    def __str__(self):
        return 'Returns Policy'


class ShippingAndDelivery(models.Model):
    all_information = RichTextField()

    class Meta:
        verbose_name = 'Shipping & Delivery'
        verbose_name_plural = 'Shipping & Delivery'

    def __str__(self):
        return 'Shipping And Delivery'


class AboutUs(models.Model):
    all_information = RichTextField()

    class Meta:
        verbose_name = 'About Us'
        verbose_name_plural = 'About Us'

    def __str__(self):
        return 'About-us'


class ImageGallery(models.Model):
    title = models.CharField(max_length=150)
    image = models.FileField(upload_to='gallery')

    class Meta:
        verbose_name = 'Image Gallery'
        verbose_name_plural = 'Image Galleries'

    def __str__(self):
        return self.title


class VideoGallery(models.Model):
    title = models.CharField(max_length=150)
    video_embed_link = models.URLField(max_length=500)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-id']
        verbose_name = 'Video Gallery'
        verbose_name_plural = 'Video Galleries'


class ProductPercel(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=150, blank=True, null=True)
    customer_phone = models.CharField(max_length=150, blank=True, null=True)
    customer_address = models.CharField(max_length=150, blank=True, null=True)
    order_note = models.TextField(blank=True, null=True)
    merchant_invoice_id = models.CharField(
        max_length=150, blank=True, null=True)
    cash_collection_amount = models.CharField(max_length=150)
    delivery_area = models.CharField(max_length=150, blank=True, null=True)
    delivery_area_id = models.CharField(max_length=150, blank=True, null=True)
    parcel_weight = models.CharField(max_length=150, blank=True, null=True)
    tracking_id = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.customer_name

    class Meta:
        verbose_name = 'Product Percel'
        verbose_name_plural = 'Product Percels'


class ReturnProduct(models.Model):
    RETURN_REASONS = [
        ('', '-- Select Reason --'),
        ('item_is_defective_or_not_working', 'Item is defective or not working'),
        ('component_or_accessory_is_missing_from_the_item',
         'Component or accessory is missing from the item'),
        ('item_has_missing_freebie', 'Item has missing freebie'),
        ('item_does_not_match_description_or_picture',
         'Item does not match description or picture'),
        ('i_did not_order_this_size', 'I did not order this size'),
        ('i_received_the_wrong_item', 'I received the wrong item'),
        ('item_does_not_fit_me', 'Item does not fit me'),
        ('do not_want_the_item_anymore', 'Do not want the item anymore'),
        ('item_is_damaged/broken/has_dent_or_scratches',
         'Item is damaged/broken/has dent or scratches'),
    ]
    RETURN_SHIPMENTS = [
        ('', '--  Drop off Locations --'),
        ('ecourier', 'eCourier'),
        ('pathao_courier', 'Pathao Courier'),
        ('delivery_tiger', 'Delivery Tiger'),
        ('karatoa_courier_service', 'Karatoa Courier Service'),
        ('janani_express_parcel_service', 'Janani Express Parcel Service'),
        ('sheba_delivery', 'Sheba Delivery'),
        ('sonar_courier', 'Sonar Courier'),
        ('sa_paribahan', 'SA Paribahan'),
        ('sundarban_courier_service', 'Sundarban Courier Service'),
    ]
    BANKS_TRANSFER = [
        ('', '--  Select Bank Transfer --'),
        ('bkash', 'BKASH Ltd'),
        ('nagad', 'NAGAD Ltd'),
        ('rocket', 'ROCKET Ltd'),
        ('upay', 'Upay Ltd'),
    ]
    RETURN_STATUS = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('On the way', 'On the way'),
        ('Complete', 'Complete'),
        ('Cancel', 'Cancel')
    ]
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, blank=True, null=True)
    return_request_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    return_charge = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    return_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True)
    return_reason = models.CharField(max_length=100, choices=RETURN_REASONS)
    status = models.CharField(
        max_length=150, choices=RETURN_STATUS, default='Pending')
    comment = models.TextField()
    return_shipment = models.CharField(
        max_length=100, choices=RETURN_SHIPMENTS)
    bank_transfer = models.CharField(max_length=100, choices=BANKS_TRANSFER)
    account_number = models.CharField(max_length=150)
    account_name = models.CharField(max_length=150)
    branch_name = models.CharField(max_length=150)
    remove_from_customer = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def total_order_item_price(self):
        return self.items.item.total_price()

    def save(self, *args, **kwargs):
        self.return_request_price = self.total_order_item_price()
        super(ReturnProduct, self).save(*args, **kwargs)


class ReturnProductImages(models.Model):
    return_product = models.ForeignKey(
        ReturnProduct, related_name='returnproductimages', on_delete=models.CASCADE)
    img = models.ImageField(upload_to='return-product-img', max_length=1000)
