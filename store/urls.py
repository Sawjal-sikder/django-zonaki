from django.urls import path
from store.views import *
from django.contrib.auth.decorators import login_required


urlpatterns =[
    path('', index, name='home'),
    path('product/detail/<slug>/', product_detail, name='product_detail'),
    path('flashsale/detail/<slug>/', flashsale_detail, name='flashsale_detail'),
    path('product/category/<slug>/', product_category_filtering, name='category'),
    path('product/brand/<slug>/', brandfiltering, name='brand'),
    path('product/shop/', shop, name='shop'),
    path('flash-sale/product/', flash_sale, name='flashsale'),
    path('deal-of-the-day/product/', deal_of_the_day, name='deal-of-the-day'),
    path('contact-us/', contact_us, name='contact'),
    path('video/gallery/', videogallery, name='video_gallery'),
    path('image/gallery/', imagegallery, name='image_gallery'),
    path('product/search/', product_search, name='search'),
    path('products/price-range-filtering/<pk>/', price_range_filtering, name='price_range_filtering'),
    path('add-to-cart/<str:slug>/', login_required(add_to_cart, login_url='/login/'), name='add_to_cart'),
    path('buy-now/<slug>/', login_required(buy_now,login_url='/login/') , name='buy_now'),
    path('remove-form-cart/<slug>/', remove_from_cart, name='remove_form_cart'),
    path("wishlist", login_required(wish_list,login_url='/login/'), name="wishlist"),
    path('add-to-wishlist/<slug>', login_required(add_to_wishlist,login_url='/login/'), name='add_to_wishlist'),
    path('delete-wish-list/<slug>', delete_wish_list, name='delete_wish_list'),
    path('add-coupon/', add_coupon, name='add_coupon'),
    path("cart-summary",login_required(cart_summary, login_url='/login/'), name="cart_summary"),
    path("my-review", login_required(myreview,login_url='/login/'), name="my_review"),
    path('ordered/product/review/<int:pk>/', review, name='order_item_review'),
    path("order-summary", login_required(order_summary, login_url='/login/'), name="order_summary"),
    path("product/order/detail/<int:pk>", product_order_detail, name="product_order_detail"),
    path('order/product/detail/<int:pk>/', order_item_detail, name='order_item_detail'),
    path("product/quantity/increment/<str:slug>", product_quantity_increment, name="product_quantity_increment"),
    path("product/quantity/decrement/<str:slug>", product_quantity_decrement, name="product_quantity_decrement"),
    

    #Pathao order Status
    path('pathao-order-status/<int:pk>/', pathao_order_status, name='pathao_order_status'),

    #Percel Tracking
    path('order-tracking/<str:tracking_code>/', order_tracking, name='order_tracking'),
    
    path('campaign/products/<str:slug>/', campaign_product_filtering, name='campaign-product'),
    path('order_pdf_view/<pk>/',render_order_pdf_view, name='render-order-pdf-view'),
    path('customer/return-product', return_product, name='return-product'),
    path('customer/return-product/status', returns_product_status, name='return-status'),

    path('privacy-policy/', privacy_policy,name='privacy-policy'),
    path('terms-conditions/', terms_conditions,name='terms_conditions'),
    path('shipping-delivery/', shipping_delivery,name='shipping_delivery'),
    path('return-policy/', returns_policy,name='returns_policy'),
    path('mission/', mission,name='mission'),
    path('vision/', vision,name='vision'),
    path('about-us/', about_us,name='about_us'),
]
