from django.urls import path
from .views import *
from django.contrib.auth.decorators import login_required



#create urls here
urlpatterns = [
path('dashboard/home/', login_required(dashboard_home,login_url='/admin/login/'), name='dashboard-home'),

#pathao
path('dashboard/create/pathao/store/', admin_create_pathao_store, name='admin_create_pathao_store'),
path('dashboard/pathao/store/list', pathao_store_list, name='pathao_store_list'),

#products
path('dashboard/products/pending/', pending_product_list, name='pending_product_list'),
path('dashboard/products/published/', publish_product_list, name='publish_product_list'),
path('dashboard/product/add/', ProductCreate.as_view(), name='create_product'),
path('dashboard/product/detail/<int:pk>/', product_detail, name='product_detail'),
path('dashboard/product/delete/<int:pk>/', dashboard_product_delete, name='dashboard_product_delete'),
path('dashboard/product/update/<int:pk>/', ProductUpdate.as_view(), name='product-update'),
path('dashboard/product/verify', product_verify, name='product_verify'),
path('dashboard/product/delete', product_delete, name='product_delete'),

path('dashboard/delete-image/<int:pk>/', delete_image, name='delete_image'),
path('dashboard/delete-variant/<int:pk>/', delete_variant, name='delete_variant'),


#orders
path('dashboard/order/list', order_list, name='order_list'),

path('dashboard/unrole/order/list', unrole_order, name='unrole_order'),
path('dashboard/pending/order/list', pending_order, name='pending_order'),
path('dashboard/complete/order/list', complete_order, name='complete_order'),
path('dashboard/return/order/list', return_order, name='return_order'),
path('dashboard/cancel/order/list', cancel_order, name='cancel_order'),
path('dashboard/order/detail/<int:pk>', order_detail, name='order_detail'),
path('dashboard/order/status/<int:pk>', order_status_update, name='order_status_update'),
path('dashboard/order/update/<int:pk>', order_update, name='order_update'),
path('dashboard/order/delete/<int:pk>', order_delete, name='order_delete'),
path('dashboard/order/shipping-address/update/<int:pk>', shipping_address_update, name='shipping_address_update'),

#category
# path('dashboard/verified-category-list/', verified_category_list, name='verified_category_list'),
# path('dashboard/category-list', category_list, name='category_list'),
# path('dashboard/pending-category-list/', pending_category_list, name='pending_category_list'),
# path('dashboard/category/add', add_category, name='add_category'),
# path('dashboard/category/update/<str:slug>', category_update, name='category-update'),
# path('dashboard/category/delete/<str:slug>', category_delete, name='category-delete'),
# path('dashboard/category/verify/all', selected_category_verify, name='selected_category_verify'),
# path('dashboard/category/delete/all', selected_category_delete, name='selected_category_delete'),



path('dashboard/categories-data/', category_data, name='category_data'), # use
path('dashboard/categories/', category_list, name='category_list'),
path('dashboard/categories/create', category_create, name='category_create'), # use
path('dashboard/categories/<int:category_id>/update', category_update, name='category_update'),
path('dashboard/categories/<int:category_id>/delete', category_delete, name='category_delete'), # use
path('dashboard/categories/filter/', category_filter, name='category_filter'),
path('dashboard/category/verify/all', selected_category_verify, name='selected_category_verify'), # use
path('dashboard/category/delete/all', selected_category_delete, name='selected_category_delete'), # use


#brands
path('dashboard/brand-data/', brand_data, name='brand_data'), # use
path('dashboard/brands/', brand_list, name='brand_list'),
path('dashboard/brands/create', brand_create, name='brand_create'), # use
path('dashboard/brands/<slug>/update', brand_update, name='brand_update'),
path('dashboard/brands/<slug>/delete', brand_delete, name='brand_delete'), # use
path('dashboard/brands/filter/', brand_filter, name='brand_filter'),
path('dashboard/brand/verify/all', selected_brand_verify, name='selected_brand_verify'), # use
path('dashboard/brand/delete/all', selected_brand_delete, name='selected_brand_delete'), # use



# #brands
# path('dashboard/verified-brand-list/', verified_brand_list, name='verified_brand_list'),
# path('dashboard/pending-brand-list/', pending_brand_list, name='pending_brand_list'),
# path('dashboard/brand/add/', add_brand, name='add_brand'),
# path('dashboard/brand/update/<slug>/', brand_update, name='brand-update'),
# path('dashboard/brand/delete/<str:slug>/',brand_delete, name='brand-delete'),
# path('dashboard/brand/verify/all', selected_brand_verify, name='selected_brand_verify'),
# path('dashboard/brand/delete/all', selected_brand_delete, name='selected_brand_delete'),

#banners
path('dashboard/banner-data/', banner_data, name='banner_data'), # use
path('dashboard/banner-list', banner_list, name='banner-list'),
path('dashboard/banner-add', banner_add, name='banner-add'),
path('dashboard/banner-update/<int:pk>', banner_update, name='banner-update'),
path('dashboard/banner-delete/<int:pk>', banner_delete, name='banner-delete'), # use

#logos
path('dashboard/logo-list', logo_list, name='logo-list'),
path('dashboard/logo-add', logo_add, name='logo-add'),
path('dashboard/logo-update/<int:pk>', logo_update, name='logo-update'),
path('dashboard/logo-delete/<int:pk>', logo_delete, name='logo-delete'),

#users
path('dashboard/superuser-list/', superuser_list, name='superuser_list'),
path('dashboard/staff-list/', staff_list, name='staff_list'),
path('dashboard/customer-list/', customer_list, name='customer_list'),
path('dashboard/customer-filter-page-list/<int:pk>', customer_filter_page_list, name='customer_filter_page_list'),
# path('dashboard/vendor-list/', vendor_list, name='vendor_list'),
path('dashboard/user-detail/<int:pk>/', user_detail, name='user_detail'),
path('dashboard/user-add', user_add, name='user-add'),
path('dashboard/user-update/<int:pk>', user_update, name='user-update'),
path('dashboard/user-delete/<int:pk>', user_delete, name='user-delete'),

# vendor payment request
path('dashboard/vendor-payment-pending', vandor_payment_pending, name='vandor_payment_pending'),
path('dashboard/vendor-payment-complete', vandor_payment_complete, name='vandor_payment_complete'),
path('dashboard/vendor-payment-details/<int:pk>/', vandor_payment_details, name='vandor_payment_details'),

path('dashboard/vendor-payment-add-step-1', vandor_payment_add_1, name='vandor_payment_add_1'),
path('dashboard/vendor-payment-add-step-2/<int:pk>', vandor_payment_add_2, name='vandor_payment_add_2'),
path('dashboard/vendor-payment-update/<int:pk>/', vandor_payment_update, name='vandor_payment_update'),
path('dashboard/vendor-payment-delete/<int:pk>', vandor_payment_delete, name='vandor_payment_delete'),

#profiles
path('dashboard/profile-list', profile_list, name='profile-list'),
path('dashboard/profile-add', profile_add, name='profile-add'),
path('dashboard/profile-update/<int:pk>', profile_update, name='profile-update'),
path('dashboard/profile-update/<int:pk>', profile_update, name='profile-update1'),
path('dashboard/profile-delete/<int:pk>', profile_delete, name='profile-delete'),


#coupons
path('dashboard/coupon-list', coupon_list, name='coupon-list'),
path('dashboard/coupon-add', coupon_add, name='coupon-add'),
path('dashboard/coupon-update/<int:pk>', coupon_update, name='coupon-update'),
path('dashboard/coupon-add-2', coupon_add_2, name='coupon-add-2'),
path('dashboard/coupon-update-2/<int:pk>', coupon_update_2, name='coupon-update-2'),
path('dashboard/coupon-delete/<int:pk>', coupon_delete, name='coupon-delete'),


#free_delivery
path('dashboard/free-delivery-data/', free_delivery_data, name='free_delivery_data'), # use
path('dashboard/free_delivery/<slug>/remove', free_delivery_remove, name='free_delivery_remove'), # use
path('dashboard/free-delivery/verify/all', selected_free_delivery_verify, name='selected_free_delivery_verify'), # use
path('dashboard/free_delivery/remove/all', selected_free_delivery_remove, name='selected_free_delivery_remove'), # use

#flashsale
path('dashboard/flashsale-list', flashsale_list, name='flashsale-list'),
path('dashboard/flashsale-add', flashsale_add, name='flashsale-add'),
path('dashboard/flashsale-update/<int:pk>', flashsale_update, name='flashsale-update'),
path('dashboard/flashsale-variation/<int:pk>', product_vartions, name='product_vartions'),
path('dashboard/flashsale-delete/<int:product_id>/', flashsale_delete, name='flashsale-delete'),
path('dashboard/flashsale-product-delete/<int:product_id>/', flashsale_product_delete, name='flashsale_product_delete'),



#campaign-category
path('dashboard/campaign_category-list', campaign_category_list, name='campaign-category-list'),
path('dashboard/campaign_category-add', campaign_category_add, name='campaign-category-add'),
path('dashboard/campaign_category-update/<int:pk>', campaign_category_update, name='campaign-category-update'),
path('dashboard/campaign_category-delete/<int:pk>', campaign_category_delete, name='campaign-category-delete'),


#campaign-products
path('dashboard/campaign-product-list', campaign_product_list, name='campaign-product-list'),
path('dashboard/campaign-product-add', campaign_product_add, name='campaign-product-add'),
path('dashboard/campaign-product-update/<int:pk>', campaign_product_update, name='campaign-product-update'),
path('dashboard/campaign-product-delete/<int:pk>', campaign_product_delete, name='campaign-product-delete'),


#deal-of-the-day
path('dashboard/deal-of-the-day-product-data', deal_of_the_day_product_data, name='deal_of_the_day_product_data'),
path('dashboard/deal-of-the-day-product-list', deal_of_the_day_product_list, name='deal_of_the_day_product-list'),
path('dashboard/deal-of-the-day-product-add', deal_of_the_day_product_add, name='deal_of_the_day_product-add'),
path('dashboard/deal-of-the-day-product-update/<int:pk>', deal_of_the_day_product_update, name='deal_of_the_day_product-update'),
path('dashboard/deal-of-the-day-product-delete/<int:pk>', deal_of_the_day_product_delete, name='deal_of_the_day_product_delete'),


#rating
path('dashboard/rating-list', rating_list, name='rating-list'),
path('dashboard/rating-add', rating_add, name='rating-add'),
path('dashboard/rating-update/<int:pk>', rating_update, name='rating-update'),
path('dashboard/rating-delete/<int:pk>', rating_delete, name='rating-delete'),


#contacts
path('dashboard/contact-data-list', contact_data_list, name='contact-list'),
path('dashboard/contact-data-detail/<pk>', contact_data_detail, name='contact-detail'),
path('dashboard/contact-add', contact_add, name='contact-add'),
path('dashboard/contact-update/<int:pk>', contact_update, name='contact-update'),
path('dashboard/contact-delete/<int:pk>', contact_delete, name='contact-delete'),


#privacy-policy
path('dashboard/privacy_policy-list', privacy_policy_list, name='privacy_policy-list'),
path('dashboard/privacy_policy-add', privacy_policy_add, name='privacy_policy-add'),
path('dashboard/privacy_policy-update/<int:pk>', privacy_policy_update, name='privacy_policy-update'),
path('dashboard/privacy_policy-delete/<int:pk>', privacy_policy_delete, name='privacy_policy-delete'),


# return-product
path('dashboard/returns_product-list', returns_product_list, name='returns_product-list'),
path('dashboard/returns_product-details/<int:pk>', returns_product_details, name='returns_product-details'),
path('dashboard/returns_product-complete', returns_product_complete, name='returns_product-complete'),
path('dashboard/returns_product-cancel', returns_product_cancel, name='returns_product-cancel'),
path('dashboard/returns_product-add', returns_product_add, name='returns_product-add'),
path('dashboard/returns_product-update/<int:pk>', returns_product_update, name='returns_product-update'),
path('dashboard/returns_product-delete/<int:pk>', returns_product_delete, name='returns_product-delete'),

#terms-conditions
path('dashboard/terms-conditions/list/', terms_condition_list, name='terms_conditions_list'),
path('dashboard/terms-conditions/add/', terms_condition_add, name='terms_conditions_add'),
path('dashboard/terms-conditions/update/<int:pk>', terms_condition_update, name='terms_conditions_update'),
path('dashboard/terms-conditions/delete/<int:pk>', terms_condition_delete, name='terms_conditions_delete'),


#mission
path('dashboard/mission-list', mission_list, name='mission-list'),
path('dashboard/mission-add', mission_add, name='mission-add'),
path('dashboard/mission-update/<int:pk>', mission_update, name='mission-update'),
path('dashboard/mission-delete/<int:pk>', mission_delete, name='mission-delete'),


#vission
path('dashboard/vision-list', vision_list, name='vision-list'),
path('dashboard/vision-add', vision_add, name='vision-add'),
path('dashboard/vision-update/<int:pk>', vision_update, name='vision-update'),
path('dashboard/vision-delete/<int:pk>', vision_delete, name='vision-delete'),


# return-policy
path('dashboard/returns_policy-list', returns_policy_list, name='returns_policy-list'),
path('dashboard/returns_policy-add', returns_policy_add, name='returns_policy-add'),
path('dashboard/returns_policy-update/<int:pk>', returns_policy_update, name='returns_policy-update'),
path('dashboard/returns_policy-delete/<int:pk>', returns_policy_delete, name='returns_policy-delete'),


#returns-policy
path('dashboard/shipping_delivery-list', shipping_delivery_list, name='shipping_delivery-list'),
path('dashboard/shipping_delivery-add', shipping_delivery_add, name='shipping_delivery-add'),
path('dashboard/shipping_delivery-update/<int:pk>', shipping_delivery_update, name='shipping_delivery-update'),
path('dashboard/shipping_delivery-delete/<int:pk>', shipping_delivery_delete, name='shipping_delivery-delete'),


#about-us
path('dashboard/aboutus-list', aboutus_list, name='aboutus-list'),
path('dashboard/aboutus-add', aboutus_add, name='aboutus-add'),
path('dashboard/aboutus-update/<int:pk>', aboutus_update, name='aboutus-update'),
path('dashboard/aboutus-delete/<int:pk>', aboutus_delete, name='aboutus-delete'),


#images
path('dashboard/image-list', image_list, name='image-list'),
path('dashboard/image-add', image_add, name='image-add'),
path('dashboard/image-update/<int:pk>', image_update, name='image-update'),
path('dashboard/image-delete/<int:pk>', image_delete, name='image-delete'),


#videos
path('dashboard/video-list', video_list, name='video-list'),
path('dashboard/video-add', video_add, name='video-add'),
path('dashboard/video-update/<int:pk>', video_update, name='video-update'),
path('dashboard/video-delete/<int:pk>', video_delete, name='video-delete'),


#parcel
path('create-parcel/<int:pk>/', create_parcel, name='create_parcel'),


#vendor-profile
path('dashboard/vendor-request-list/', profile_unaccept_list, name='profile_unaccept_list'),
path('dashboard/verified-vendor-list/', profile_accept_list, name='profile_accept_list'),
path('dashboard/vendor-profile-update/<int:pk>', vendor_profile_update, name='profile-update'),
path('dashboard/vendor-profile-view/<int:pk>', vendor_profile_view, name='vendor_profile_view'),
path('dashboard/vendor-profile-verify/<int:pk>', vendor_profile_verify, name='vendor_profile_verify'),
path('dashboard/vendor-product-list/<int:pk>', vendor_product_list, name='vendor_product_list'),
path('dashboard/vendor-profile-delete/<int:pk>', vendor_profile_delete, name='profile-delete'),


#price-range
path('dashboard/price-range/data/', price_range_data, name='price_range_data'), # use
path('dashboard/price-range/list/', price_range_list, name='price_range_list'),
path('dashboard/price-range/create/', price_range_create, name='price_range_create'),
path('dashboard/price-range/update/<int:pk>/', price_range_update, name='price_range_update'),
path('dashboard/price-range/delete/<int:pk>/', price_range_delete, name='price_range_delete'), # use


#change-password
path('dashboard/change-password/', change_password, name='dashboard_change_password'),
path('dashboard/update/profile/',update_profile, name='update_profile'),


#website-informations
path('dashboard/website-information/', website_information_list, name='website_information_list'),
path('dashboard/website-information/<int:pk>/', website_information_detail, name='website_information_detail'),
path('dashboard/website-information/add/', website_information_create, name='website_information_add'),
path('dashboard/website-information/<int:pk>/update/', website_information_update, name='website_information_update'),
path('dashboard/website-information/<int:pk>/delete/', delete_website_info, name='delete_website_info'),
path('dashboard/website-information/phone/delete/', delete_phone_number, name='delete_phone_number'),
path('dashboard/website-information/email/delete/', delete_email_address, name='delete_email_address'),
path('dashboard/website-information/address/delete/', delete_company_address, name='delete_company_address'),



#colors
path('dashboard/color-data/', color_data, name="color_data"), # use
path('dashboard/color-add/', color_add, name="color_add"),
path('dashboard/colors-list/', colors_list, name="colors_list"),
path('dashboard/color-update/<int:pk>/', color_update, name="color_update"), 
path('dashboard/color-delete/<int:pk>/', color_delete, name="color_delete"), # use


#sizes
path('dashboard/size-data/', size_data, name="size_data"), # use
path('dashboard/size-add/', size_add, name="size_add"),
path('dashboard/sizes-list/', sizes_list, name="sizes_list"),
path('dashboard/size-update/<int:pk>/', size_update, name="size_update"),
path('dashboard/size-delete/<int:pk>/', size_delete, name="size_delete"), # use


path('dashboard/vendor/order/<int:pk>/', vendor_all_details, name="vendor_all_details"),
]
