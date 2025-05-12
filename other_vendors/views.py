from django.shortcuts import get_object_or_404, render,redirect
import json
from .models import *
from store.models import Order
from django.contrib.auth import login
from .forms import *
from userapp.forms import *
from userapp.urls import *
from django.contrib import messages
from paymentApp.views import fetch_cities

def vendor_registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_vendor = True
            user.save()
            login(request, user, backend='userapp.backends.EmailOrPhoneBackend')
            messages.success(request, 'Vendor registered successfully')
            return redirect('dashboard-home')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, f"{error}")   
    else:
        form = RegisterForm()
    return render(request, 'vendor/registration.html', {'form': form})
    

def vendor_profile_update(request):
    fetch_city_data = fetch_cities()
    city_datas = fetch_city_data["data"]["data"]
    try:
        vendor_profile = VendorInformation.objects.get(user=request.user)
    except VendorInformation.DoesNotExist:
        vendor_profile = None

    if request.method == 'POST':
        if vendor_profile:
            form = VendorInformationForm(request.POST, request.FILES, instance=vendor_profile)
        else:
            form = VendorInformationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor_profile = form.save(commit=False)
            vendor_profile.user = request.user
            vendor_profile.save()
            messages.success(request, 'Profile Updated Successfully.')
            return redirect('dashboard-home')
    else:
        if vendor_profile:
            form = VendorInformationForm(instance=vendor_profile)
        else:
            form = VendorInformationForm()

    id_types = VendorInformation.ID_TYPE
    context = {
        'form': form,
        'id_types': id_types,
        'city_datas': city_datas,
    }
    return render(request, 'vendor/vendor_full_info.html', context)


def vendor_registaion_step_2(request):
    return render(request, 'other_vendors/vendor_re_step_2.html')



def vendor_address(request):
    country = Country.objects.all().order_by('name')
    country_list = list(country.values('name','id'))
    country_list = json.dumps(country_list)
    
    division = Division.objects.all().order_by('name')
    division_list = list(division.values('name','country__name','id'))
    division_list = json.dumps(division_list)
    
    district = District.objects.all().order_by('name')
    district_list = list(district.values('name','division__name','id'))
    district_list = json.dumps(district_list)
    
    subdistrict = SubDistrict.objects.all().order_by('name')
    subdistrict_list = list(subdistrict.values('name','district__name','id'))
    subdistrict_list = json.dumps(subdistrict_list)
    
    context ={
        'country_list': country_list,
        'division_list': division_list,
        'district_list': district_list,
        'subdistrict_list': subdistrict_list  
    }
    return render(request, 'other_vendors/vendor_address.html', context)


def vendor_pro_update(request):
    profile = get_object_or_404(VendorInformation)
    form = VendorInformationFormUpdate(request.POST, instance=request.profile) 
    if request.method == 'POST':
        form = VendorInformationFormUpdate(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated')
            return redirect('dashboard-home')  
    context = {
        'form': form,
    }
    return render(request, 'other_vendors/profile_update.html', context)


def vendor_payment(request):
    user_payments = VendorPayment.objects.filter(user=request.user).values_list('product__id', flat=True)

    orders = Order.objects.filter(
        items__item__user=request.user,
        ordered=True,
        order_status='Complete'
    )
    item_list = []
    for order in orders:
        for item in order.items.all():
            if not item.id in user_payments and item.item.user == request.user:
                item_list.append(item)
                
    if request.method == "POST":
        form = VendorPaymentForm(request.POST)
        if form.is_valid():
            products = form.cleaned_data['product']
            payment = form.save(commit=False)
            payment.user = request.user
            payment.save()
            payment.product.set(products)
            messages.success(request, 'Successfully requested.')
            return redirect('dashboard-home')
        else:
            messages.error(request, 'Payment request failed. Please check the form errors.')
    else:
        form = VendorPaymentForm()

    context = {
        'orders': orders,
        'item_list': item_list,
        'form': form,
    }
    return render(request, 'vendor/payment-form.html', context)






"""Pathao delivery status webhook for order status"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

WEBHOOK_SECRET = settings.WEBHOOK_SECRET
@csrf_exempt
def delivery_status_webhook(request):
    if request.method == "POST":
        try:
            # Extract headers and request body
            provided_signature = request.headers.get("X-PATHAO-Signature")
            request_body = request.body

            # Validate signature
            if provided_signature != WEBHOOK_SECRET:
                return JsonResponse({"error": "Invalid signature"}, status=403)

            # Parse payload
            payload = json.loads(request_body)
            consignment_id = payload.get("consignment_id")
            order_status = payload.get("order_status")
            item = get_object_or_404(OrderItem, pathao_consignment_id=consignment_id)
            item.pathao_status = order_status
            item.save()
            return JsonResponse({"message": "Delivery status webhook processed successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)

