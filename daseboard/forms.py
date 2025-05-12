from django import forms
from store.models import *
from paymentApp.models import *
from django.forms import inlineformset_factory
from ckeditor_uploader.widgets import CKEditorUploadingWidget 
from django.forms import ModelChoiceField
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from other_vendors.models import VendorPayment

class UserForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'phone', 'groups', 'user_permissions', 'is_active', 'is_customer', 'is_vendor', 'is_staff', 'is_superuser']


# product add inline formset
class ProductForm(forms.ModelForm):
    price_range = forms.ModelChoiceField(queryset=PriceRange.objects.all(), empty_label="-- Select Price Range --")
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), empty_label="-- Select Brand --")
    categoris = forms.ModelChoiceField(queryset=ProductCategory.objects.all(), empty_label="-- Select Category --")
    sort_discription = forms.CharField(
        required=False, 
        widget=CKEditorUploadingWidget(attrs={'class': 'form-control p-20', 'rows': "4"})
    )
    aditional_discription = forms.CharField(
        required=False, 
        widget=CKEditorUploadingWidget(attrs={'class': 'form-control p-20', 'rows': "4"})
    )
    discription = forms.CharField(
        widget=CKEditorUploadingWidget(attrs={'class': 'form-control p-20', 'rows': "4"})
    )
    
    class Meta:
        model = Product
        exclude = ['user', 'stock_quantity', 'slug']


class ImageForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = ProductImgGallery
        fields = '__all__'


class VariantForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = '__all__'

# Formsets
VariantFormSet = inlineformset_factory(
    Product, Variation, form=VariantForm,
    extra=1, can_delete=True, can_delete_extra=True
)

ImageFormSet = inlineformset_factory(
    Product, ProductImgGallery, form=ImageForm,
    extra=1, can_delete=True, can_delete_extra=True
)


class ProductCategoryForm(forms.ModelForm):
    category_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder':'Categorie name'}))
    parent = ModelChoiceField(required=False,queryset=ProductCategory.objects.all(),empty_label="-- Select Parent Category --", widget=forms.Select(attrs={'class':'form-control'}))
    class Meta:
        model = ProductCategory
        fields = ['category_name', 'parent', 'img', 'commission', 'sl_no', 'is_verified']


class BrandAddForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields =['name', 'image', 'is_verified']


class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields ='__all__'


class CouponProductAddForm(forms.ModelForm):
    valid_from = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    valid_to = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    class Meta:
        model = Coupon
        fields = ['code', 'coupon_type','amount_or_percentage', 'minimum_price_range', 'valid_from', 'valid_to', 'max_value', 'product', 'is_verified']

class CouponUserAddForm(forms.ModelForm):
    valid_from = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    valid_to = forms.DateTimeField(required=True, disabled=False,
                                          widget=forms.DateTimeInput(attrs={'type':'datetime-local'}),
                                          error_messages={'required': "This field is required."})
    class Meta:
        model = Coupon
        fields = ['code', 'coupon_type','amount_or_percentage', 'minimum_price_range', 'valid_from', 'valid_to', 'max_value', 'coupon_user', 'is_verified']


class FlashsaleForm(forms.ModelForm):
    class Meta:
        model = FlashSale
        fields = '__all__'
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type':'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type':'datetime-local'}),
        }
        
class FlashsaleProductForm(forms.ModelForm):
    class Meta:
        model = FlashSaleProduct
        fields = '__all__'
FlashSaleProductFormset = inlineformset_factory(
    FlashSale, FlashSaleProduct,form = FlashsaleProductForm, extra=0, can_delete=True, can_delete_extra=True
)        

# class OrderupdateForm(forms.ModelForm):
#     order_complate_date = forms.DateTimeField(required=False, disabled=False, widget=forms.DateTimeInput(attrs={'type':'date', "class":"form-control"}), error_messages={'required': "This field is required."})

#     class Meta:
#         model = Order
#         fields = '__all__'


class OrderupdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'order_status',
            'total_order_amount',
            'paid_amount',
            'due_amount',
            'ordered',
            'orderId',
            'paymentId',
            'coupon',
            'shipping_address',
            'payment_option',
            'order_read_status',
            'merchant_order_id',
            'consignment_id',
            # 'redx_percel_traking_number',
            # 'others_transport_trakink_url',
        ]


class OrderShippingAddressUpdateForm(forms.ModelForm): 
    full_address = forms.CharField(required=False,widget=forms.Textarea(attrs={'class':'form-control p-20', 'rows':"4"}))
    order_note = forms.CharField(required=False,widget=forms.Textarea(attrs={'class':'form-control p-20', 'rows':"4"}))
    
    class Meta:
        model = ShipingAddress
        fields = '__all__'


class CampaignCategoryForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = '__all__'


class CampaignProductForm(forms.ModelForm):
    class Meta:
        model = CampaignProduct
        fields = '__all__'


class DealOfTheDayProductForm(forms.ModelForm):
    class Meta:
        model = DealOfTheDayProduct
        fields = '__all__'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = '__all__'


class ContactForm(forms.ModelForm):
    class Meta:
        model = ConductData
        fields = '__all__'


class PrivacyPolicyForm(forms.ModelForm):
    all_information =forms.CharField(label="Privacy Policy", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))
    class Meta:
        model = PrivacyPolicy
        fields = '__all__'


class TermsAndConditionsForm(forms.ModelForm):
    all_information =forms.CharField(label="Terms & Conditions", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))
    class Meta:
        model = TermsAndConditions
        fields = '__all__'

class MissionForm(forms.ModelForm):
    all_information =forms.CharField(label="Our Mission", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))    
    class Meta:
        model = Mission
        fields = '__all__'

class VisionForm(forms.ModelForm):
    all_information =forms.CharField(label="Our Vision", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))    
    class Meta:
        model = Vision
        fields = '__all__'

class Returns_PolicyForm(forms.ModelForm):
    all_information =forms.CharField(label="Return Policy", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))    
    class Meta:
        model = Returns_Policy
        fields = '__all__'

class ShippingAndDeliveryForm(forms.ModelForm):
    all_information =forms.CharField(label="Shipping & Delivery", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))    
    class Meta:
        model = ShippingAndDelivery
        fields = '__all__'


class AboutUsForm(forms.ModelForm):
    all_information =forms.CharField(label="About Us", widget=CKEditorUploadingWidget(attrs={'class':'form-control p-20', 'rows':"4"}))    
    class Meta:
        model = AboutUs
        fields = '__all__'


class ImageAddForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput(attrs={'id':"upload"}))
    class Meta:
        model = ImageGallery
        fields = ['title','image']

class VideoAddForm(forms.ModelForm):
    class Meta:
        model = VideoGallery
        fields = '__all__'

class PercelForm(forms.ModelForm):
    parcel_weight = forms.CharField(required=False, widget=forms.NumberInput)
    class Meta:
        model = ProductPercel
        fields = ['delivery_area','parcel_weight']


class PriceRangeForm(forms.ModelForm):
    class Meta:
        model = PriceRange
        fields = ['price_range', 'ordering']


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label='Current Password', widget=forms.PasswordInput)
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)


class WebsiteInformationForm(forms.ModelForm):
    class Meta:
        model = WebsiteInformation
        fields = '__all__'

class PhoneNumberForm(forms.ModelForm):
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = PhoneNumber
        fields = ['phone']


class EmailAddressForm(forms.ModelForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model = EmailAddress
        fields = ['email']


class CompanyAddressForm(forms.ModelForm):
    address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = CompanyAddress
        fields = ['address']


PhoneNumberFormSet = inlineformset_factory(WebsiteInformation, PhoneNumber, form=PhoneNumberForm, extra=1, can_delete=True)
EmailAddressFormSet = inlineformset_factory(WebsiteInformation, EmailAddress, form=EmailAddressForm, extra=1, can_delete=True)
CompanyAddressFormSet = inlineformset_factory(WebsiteInformation, CompanyAddress, form=CompanyAddressForm, extra=1, can_delete=True)


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ['name']

    
class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name']
        
        
        
class DashReturnProductForm(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = '__all__'                


class DashVendorPaymentForm(forms.ModelForm):
    class Meta:
        model = VendorPayment
        fields = '__all__'            


