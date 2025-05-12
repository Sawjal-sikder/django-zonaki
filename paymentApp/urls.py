from django.urls import path
from paymentApp.views import * 
from paymentApp.utils import fetch_stores


urlpatterns = [
    path("checkout", CheckOutView.as_view(), name="Check-Out"),
    path("address", ShippingAdressView.as_view(), name="address"),
    path('initiate/payment', initiate_payment, name='initiate_payment'),
    path('bkash/payment', create_bkash_payment, name='bkash-payment'),
    path('execute_bkash_url', execute_bkash_callbackurl, name='execute_bkash_url'),
    path('bkash/payment/list', bkash_payment_list, name='bkash_payment_list'),
    path('bkash_search_transaction/<str:trxID>/', bkash_search_transaction, name='bkash_search_transaction'),
    path('bkash_payment_query/<str:paymentID>/', bkash_payment_query, name='bkash_payment_query'),
    path('bkash_payment_refund/<str:paymentID>/', bkash_payment_refund, name='bkash_payment_refund'),
    path('bkash_payment_refund_list/', bkash_payment_refund_list, name='bkash_payment_refund_list'),

    path('create/single/order/<int:id>', create_pathao_order, name='create_pathao_order'),
    path('create/orders/<int:id>', create_bulk_orders, name='create_bulk_orders'),
    path('fetch-zones/', fetch_zones, name='fetch_zones'),
    path('fetch-areas/', fetch_areas, name='fetch_areas'),
    path('fetch-stores/', fetch_stores, name='fetch_stores'),
]
