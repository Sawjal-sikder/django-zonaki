from email.mime import image
from django import forms
from .models import *
from .models import ConductData
from django.forms import inlineformset_factory

class CouponCodeForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder':"coupon code"
    }))

class ProductReviewForm(forms.ModelForm):
    RATING =(
        ('1','1'),
        ('2','2'),
        ('3','3'),
        ('4','4'),
        ('5','5')
    )
    rating  = forms.ChoiceField(choices = RATING,widget=forms.RadioSelect(attrs={
    }))
    image = forms.ImageField(required=False)
    review = forms.CharField(
        widget=forms.Textarea(attrs={
            "class":"form-control",
            "placeholder":"Comment",
            'rows':2
        })
        )
    class Meta:
        model = ProductReview
        fields = ['rating','review','image']


class Contact_Form(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Your Email'}))
    phone = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Your Phone'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Your Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Your Message', 'rows': 4}))
    
    class Meta:
        model = ConductData
        fields = '__all__'





class ReturnProductForm(forms.ModelForm):
    class Meta:
        model = ReturnProduct
        fields = ['items','return_reason', 'comment', 'return_shipment', 'bank_transfer', 'account_number', 'account_name', 'branch_name']

class ReturnProductImagesForm(forms.ModelForm):  
    class Meta:
        model = ReturnProductImages
        fields = '__all__'



ReturnProductImagesFormSet = inlineformset_factory(
    ReturnProduct, ReturnProductImages, form=ReturnProductImagesForm,
    extra=1, can_delete=True, can_delete_extra=True
)