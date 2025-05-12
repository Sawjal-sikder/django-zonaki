from webbrowser import register
from django.contrib import admin
from .models import *


# Register your models here.
class ProductImgGalleryAdmin(admin.StackedInline):
    model = ProductImgGallery
    min_num = 0
    extra = 1

class ProductVriationAdmin(admin.StackedInline):
    model = Variation
    min_num = 0
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImgGalleryAdmin,ProductVriationAdmin]


class PhoneNumberInline(admin.TabularInline):
    model = PhoneNumber
    extra = 1

class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    extra = 1

class CompanyAddressInline(admin.TabularInline):
    model = CompanyAddress
    extra = 1

@admin.register(WebsiteInformation)
class WebsiteInformationAdmin(admin.ModelAdmin):
    inlines = [PhoneNumberInline, EmailAddressInline, CompanyAddressInline]

 

class FlashSaleProductInline(admin.TabularInline):
    model = FlashSaleProduct
    extra = 1

class FlashSaleAdmin(admin.ModelAdmin):
    inlines = [FlashSaleProductInline]
    list_display = ('title', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active',)

class FlashSaleProductAdmin(admin.ModelAdmin):
    list_display = ('flash_sale', 'product', 'discount_price', 'stock', 'sold')

admin.site.register(FlashSale, FlashSaleAdmin)


admin.site.register(ProductCategory)
admin.site.register(Product, ProductAdmin)
admin.site.register(Banner)
admin.site.register(Brand)
admin.site.register(Variation)
admin.site.register(OrderItem)
admin.site.register(ProductReview)
admin.site.register(Order)
admin.site.register(Coupon)
admin.site.register(WhishLIst)
admin.site.register(VideoGallery)
admin.site.register(ImageGallery)
admin.site.register(ConductData)
class PathaoParcelAdmin(admin.ModelAdmin):
    list_display = ('order','consignment_id', 'created_at','updated_at')
admin.site.register(PathaoParcel, PathaoParcelAdmin)
# admin.site.register(FlashSale)


class ReturnProductImagesAdmin(admin.StackedInline):
    model = ReturnProductImages
    extra = 1
class ReturnProductAdmin(admin.ModelAdmin):
    inlines = [ReturnProductImagesAdmin]
admin.site.register(ReturnProduct, ReturnProductAdmin)
admin.site.register(ReturnProductImages)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('campaign_name',)}

admin.site.register(CampaignProduct)
admin.site.register(DealOfTheDayProduct)
# admin.site.register(WebsiteInformation, WebsiteInformationAdmin)
admin.site.register(PriceRange)
admin.site.register(PrivacyPolicy)
admin.site.register(TermsAndConditions)
admin.site.register(Returns_Policy)
admin.site.register(ShippingAndDelivery)
admin.site.register(ProductPercel)


admin.site.site_title = "Zonaki Admin"
admin.site.site_header = "Zonaki Administration"
admin.site.index_title = "Zonaki Site Management"

