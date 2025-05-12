from django import forms
# from django.contrib.auth.models import User
from .models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'phone', 'password1', 'password2']

    # def __init__(self, *args, **kwargs):
    #     super(RegisterForm, self).__init__(*args, **kwargs)
    #     self.fields['phone'].widget.attrs.pop("autofocus", None)


class UpdateRegisterForm(forms.ModelForm):
    class Meta:
        model=User
        fields =['full_name', 'email', 'phone']


class UpdateProfileForm(forms.ModelForm):
    date_of_birthday = forms.DateField(required=False,widget=forms.TextInput( attrs={ "type":"date",}))
    
    class Meta:
        model = Profile
        fields = ['image', 'date_of_birthday', 'address']




# class UserLoginForm(AuthenticationForm):
#     class Meta:
#         model = User
#         fields = ('email', 'password')
    