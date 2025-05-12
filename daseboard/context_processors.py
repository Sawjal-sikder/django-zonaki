from store.models import *
from other_vendors.models import *
from datetime import datetime


def order_count(request):
    order_count = Order.objects.filter(ordered=True, order_read_status=False).count()
    context = {
        'order_count': order_count
    }
    return context


def unverified_vendor_count(request):
    unverified_vendor_count = VendorInformation.objects.filter(
        is_verified=False).count()
    unverified_vendor_profile = VendorInformation.objects.filter(
        is_verified=False)

    context = {
        'unverified_vendor_count': unverified_vendor_count,
        'unverified_vendor_profile': unverified_vendor_profile,
    }
    return context


def order_list(request):
    user = request.user
    order_list = Order.objects.filter(ordered=True, order_read_status=False)
    context = {
        'order_list': order_list
    }
    return context


def contact_data_count(request):
    contact_data_count = ConductData.objects.filter(view_status=False).count()
    context = {
        'contact_data_count': contact_data_count
    }
    return context


def contact_data_list(request):
    contact_data_list = ConductData.objects.filter(view_status=False)
    context = {
        'contact_data_list': contact_data_list
    }
    return context


def rating_list_view(request):
    rating_review = ProductReview.objects.filter(approve_status=False)
    context = {
        'rating_review': rating_review
    }
    return context


def order_information(request):
    total_revenue = 0
    user_total_revenue = 0

    # Fetch all completed orders with prefetching to optimize related queries
    order_information = Order.objects.filter(ordered=True).prefetch_related('items__item__user')

    for order in order_information:
        for item in order.items.all():
            if not item.pathao_consignment_id or item.pathao_status != "Delivered":
                continue
            total_revenue += item.item.get_product_reveneu()
            if request.user == item.item.user:
                user_total_revenue += item.item.get_product_reveneu()

    context = {
        'total_revenue': total_revenue,
        'user_total_revenue': user_total_revenue,
    }
    return context


# def order_information(request):
#     order_information = Order.objects.filter(order_status='Complete')
#     total_sale = 0
#     total_purchase_price = 0
#     for x in order_information:
#         total_sale += x.get_total()
#         total_purchase_price += x.get_purchase_price_total()

#     total_revenue = total_sale - total_purchase_price
#     context = {
#         'order_information': order_information,
#         'total_sale': total_sale,
#         'total_revenue': total_revenue
#     }
#     return context

def website_logo(request):
    return {'logo':WebsiteInformation.objects.all()}


def greeting(request):
    # Get the current time in the Asia/Dhaka time zone
    current_time = timezone.localtime(timezone.now())

    if current_time.hour < 12:
        greeting = "Good morning"
    elif 12 <= current_time.hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    return {'greeting': greeting}
