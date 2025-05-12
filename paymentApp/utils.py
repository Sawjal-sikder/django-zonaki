from django.shortcuts import redirect
from django.conf import settings
from django.db.models import Prefetch
from django.utils import timezone
import requests
import datetime

from store.models import Order, OrderItem
from .models import PathaoStores, PathaoToken


def get_existing_token():
    """Fetch the existing token from the database."""
    try:
        return PathaoToken.objects.first()
    except PathaoToken.DoesNotExist:
        return None

def issue_access_token():
    """
    Issues a new access token using client credentials and user credentials.
    """
    url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/issue-token"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }
    payload = {
        "client_id": settings.PATHAO_API_CLIENT_ID,
        "client_secret": settings.PATHAO_API_CLIENT_SECRET,
        "username": settings.PATHAO_API_USERNAME,
        "password": settings.PATHAO_API_PASSWORD,
        "grant_type": settings.PATHAO_API_GRANT_TYPE,
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        expires_in_seconds = data.get('expires_in', 0)
        expires_at = timezone.now() + datetime.timedelta(seconds=expires_in_seconds)

        # Save token in the database
        token, created = PathaoToken.objects.update_or_create(
            id=1,
            defaults={
                'access_token': data.get('access_token'),
                'refresh_token': data.get('refresh_token'),
                'expires_at': expires_at
            }
        )
        return token.access_token
    else:
        raise Exception(f"Error issuing token: {response.json()}")

def refresh_access_token():
    """
    Refreshes the access token using the stored refresh token.
    """
    token = get_existing_token()
    if not token or not token.refresh_token:
        raise Exception("No refresh token available")

    url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/issue-token"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }
    payload = {
        "client_id": settings.PATHAO_API_CLIENT_ID,
        "client_secret": settings.PATHAO_API_CLIENT_SECRET,
        "refresh_token": token.refresh_token,
        "grant_type": "refresh_token",
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        expires_in_seconds = data.get('expires_in', 0)
        expires_at = timezone.now() + datetime.timedelta(seconds=expires_in_seconds)

        # Update token in the database
        token.access_token = data.get('access_token')
        token.expires_at = expires_at
        token.save()
        return token.access_token
    else:
        raise Exception(f"Error refreshing token: {response.json()}")

def get_access_token():
    """Retrieve a valid access token, refreshing it if necessary."""
    token = get_existing_token()

    # If token is expired or not present, refresh or issue a new one
    if not token or token.is_expired():
        if token and token.refresh_token:
            return refresh_access_token()
        else:
            return issue_access_token()
    return token.access_token



def fetch_cities(): # using
    access_token = get_access_token()
    url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/city-list"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    json_string = response.json()
    # print(f'====================================================')
    # print('called fetch_cities')
    # print(f'====================================================')
    return json_string

from decimal import Decimal
def fetch_shipping_amount(pk): # using
    # Prefetch related objects to optimize the query
    order = (
        Order.objects
        .select_related('shipping_address')
        .prefetch_related(
            Prefetch('items__item')
        )
        .get(id=pk)
    )
    # print(f'====================================================')
    # print(f'called fetch_shipping_amount {order = }')
    total_charge = 0
    vendor_items = Order.objects.vendor_items(pk)
    # print(f'called fetch_shipping_amount-1 = {total_charge = }')
    # print(f'called fetch_shipping_amount {vendor_items = }')

    # Print out the grouped items by user
    for user, data in vendor_items.items():
        store_id = user.vendorinformation.store_id if user.is_vendor else user.profile.store_id or 241231
        # print(f'called fetch_shipping_amount {store_id = }')
        # 129913 # it is admins store id
        item_weight = sum(
            Decimal(item_dict['item'].item.weight) * Decimal(item_dict['item'].quantity)
            for item_dict in data['items']
        )
        
        access_token = get_access_token()
        # print(f'called fetch_shipping_amount {access_token = }')
        url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/merchant/price-plan"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "store_id": store_id,
            "item_type": 2,
            "delivery_type": order.shipping_address.delivery_type,
            "item_weight": float(item_weight),
            "recipient_city": order.shipping_address.city,
            "recipient_zone": order.shipping_address.zone,
        }
        # Send request to Pathao API
        response = requests.post(url, json=payload, headers=headers)
        res = response.json()
        # print(f'called fetch_shipping_amount {res = }')
        if response.status_code == 200:
            # Extract shipping charge from API response
            charge = res["data"]["final_price"]
            # print(f'called fetch_shipping_amount {charge = }')
            total_charge += charge
            # print(f'called fetch_shipping_amount {total_charge = }')
            for item_dict in data['items']:
                # print(f'called fetch_shipping_amount {item_dict = }')
                single_charge = charge / int(data['total_item_count'])
                item_dict['item'].shipping_charge = single_charge
                # print(f'called fetch_shipping_amount-2 = {single_charge = }')
                item_dict['item'].save()
        else:
            return redirect('address')

    # Update the total shipping amount for the order
    order.total_shipping_amount = total_charge
    # print(f'called fetch_shipping_amount-2 = {total_charge = }')
    # print(f'====================================================')
    order.save()
    return redirect('Check-Out')


def fetch_consignment(order_items_ids):
    access_token = get_access_token()  # Getting the access token for authentication
    items = OrderItem.objects.filter(id__in=order_items_ids)  # Retrieving the order items by their IDs
    for item in items:
        url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/orders/{item.pathao_consignment_id}/info"
        headers = {
            "Authorization": f"Bearer {access_token}",  # Authorization header with the access token
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        # Sending the GET request to Pathao API to fetch consignment info
        response = requests.get(url, headers=headers)
        res = response.json()  # Parsing the JSON response from the API
        status = res['data']['order_status']  # Extracting order status from the response
        # print(f'====================================================')
        # print(f'called fetch_consignment = {status = }')
        # print(f'====================================================')
        item.pathao_status = status  # Updating the order item's Pathao status
        item.save()  # Saving the item to the database
        continue



def fetch_stores(request):
    access_token = get_access_token()  # Getting the access token for authentication
    url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/stores"
    headers = {
        "Authorization": f"Bearer {access_token}",  # Authorization header with the access token
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers)
    res = response.json()  # Parsing the JSON response from the API
    if response.status_code == 200:
        datas = res["data"]["data"]
        for i in datas:
            store_id = i["store_id"]
            store_name = i["store_name"]
            zone_id = i["zone_id"]
            store_address = i["store_address"]
            city_id = i["city_id"]
            hub_id = i["hub_id"]
            is_active = i["is_active"]
            is_default_return_store = i["is_default_return_store"]
            is_default_store = i["is_default_store"]

            store, created = PathaoStores.objects.update_or_create(
                store_id=store_id,
                defaults={
                    'store_name': store_name,
                    'zone_id': zone_id,
                    'store_address': store_address,
                    'city_id': city_id,
                    'hub_id': hub_id,
                    'is_active': is_active,
                    'is_default_return_store': is_default_return_store,
                    'is_default_store': is_default_store,
                }
            )

    return redirect('pathao_store_list')

