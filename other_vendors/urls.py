from django.urls import path
from .views import *


urlpatterns = [
    path("vendor/registration", vendor_registration, name="vendor_registration"),
    path("vendor/profile/update", vendor_profile_update, name="vendor_full_info"),
    path('vendor/profile/verify-code', vendor_registaion_step_2, name="step_2"),
    path('vendor/vendor-payment', vendor_payment, name="vendor_payment"),

    # webhook for pathao
    path('webhook/delivery-status/', delivery_status_webhook, name='delivery_status_webhook'),
]
