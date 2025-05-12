from django import forms
from django.contrib.auth.forms import UserChangeForm
from userapp.models import User
from .models import *


class RegistrationForm(UserChangeForm):
    class meta:
        models = User
        fields = ['phone', 'password1', 'password2']
        
class VendorInformationForm(forms.ModelForm):
    class Meta:
        model = VendorInformation
        exclude = ['user','is_verified']
        
class VendorInformationFormUpdate(forms.ModelForm):
    class Meta:
        model = VendorInformation
        exclude = ['user']
    
    # def __init__(self, *args, **kwargs):
    #     super(VendorInformationFormUpdate, self).__init__(*args, **kwargs)
    #     self.fields['store_id'].widget.attrs['readonly'] = True
        
            
class VendorPaymentForm(forms.ModelForm):
    class Meta:
        model = VendorPayment
        exclude = ['user','status']
    

        