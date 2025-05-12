from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
import requests
import json
from django.core.cache import cache

from .forms import *
from .models import *
from paymentApp.models import *
from paymentApp.utils import fetch_consignment


def index(request):
    banner = Banner.objects.all()
    logo = WebsiteInformation.objects.last()
    # it is all products ids which don't have any vendor or admin store_id for pathao api integration
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())
    flashsale = FlashSale.objects.filter(is_active=True, end_time__gt=timezone.now()).last()
    product_flashsales = list(FlashSaleProduct.objects.filter(flash_sale=flashsale).values_list('product__id', flat=True).distinct())

    deal_product = DealOfTheDayProduct.objects.exclude(product__id__in=no_store_id_product_id_list).order_by('?')
    
    if flashsale:
        flashsale_products = FlashSaleProduct.objects.filter(flash_sale=flashsale, stock__gt = F('sold')).exclude(id__in=product_flashsales).order_by("?")
    else:
        flashsale_products = None
 
    exclude_ids = list(set(no_store_id_product_id_list + product_flashsales))
    all_product = Product.objects.filter(is_verified=True).exclude(id__in=exclude_ids).order_by("?")
    free_delivery_product = Product.objects.filter(is_verified=True, free_delivery=True).exclude(id__in=no_store_id_product_id_list).order_by("?")

    # Cache product category
    # product_category =ProductCategory.objects.filter(sl_no__gt=0).order_by('sl_no')[:16]
    product_category = cache.get('product_category')
    if not product_category:
        product_category = ProductCategory.objects.filter(sl_no__gt=0).order_by('sl_no')[:16]
        cache.set('product_category', product_category, timeout=3600)

    context = {
        'banner': banner,
        'all_product': all_product,
        'free_delivery_product': free_delivery_product,
        'flashsale': flashsale,
        'flashsale_products': flashsale_products,
        'deal_product': deal_product,
        'logo': logo,
        'product_category':product_category,
    }
    return render(request, 'store/index.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    img = ProductImgGallery.objects.filter(product=product.id)
    related_product = Product.objects.filter(categoris=product.categoris).exclude(slug=slug).order_by('?')
    
    context = {
        'product': product,
        'img': img,
        'related_product': related_product
    }
    return render(request, 'store/product_detail.html', context)


def flashsale_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    img = ProductImgGallery.objects.filter(product=product.id)
    related_product = Product.objects.filter(categoris=product.categoris).exclude(slug=slug).order_by('?')
    flashsale_product = FlashSaleProduct.objects.filter(product=product)
    flashsale_product_data = list(flashsale_product.values())
    flashsale_varitions_data = list(flashsale_product.values('variation__id', 'variation__size__name', 'variation__color__name', 'flashsale_price'))
    unique_sizes = set()
    unique_colors = set()
    for f in flashsale_product:
        if f.variation:
            if f.variation.size and f.stock > f.sold:
                unique_sizes.add(f.variation.size.name)
            if f.variation.color and f.stock > f.sold:
                unique_colors.add(f.variation.color.name)
    unique_sizes_list = sorted(unique_sizes)
    unique_colors_list = sorted(unique_colors)

    context = {
        'product': product,
        'unique_sizes_list': unique_sizes_list,
        'unique_colors_list': unique_colors_list,
        'flashsale_products': json.dumps(flashsale_product_data),
        'products_variations': json.dumps(flashsale_varitions_data),
        'flashsale_product': flashsale_product,
        'img': img,
        'related_product': related_product,
    }
    return render(request, 'store/flashsale_detail.html', context)


def product_search(request):
    query = request.GET.get('q', '')
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    products = Product.objects.filter(
        Q(product_name__icontains=query) | Q(price__icontains=query) | 
        Q(categoris__category_name__icontains=query) | Q(brand__name__icontains=query)
        ,is_verified=True).exclude(id__in=no_store_id_product_id_list).order_by('?')
    return render(request, 'store/search_product.html', {'products': products})


def product_category_filtering(request, slug):
    cate = get_object_or_404(ProductCategory, slug=slug)
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    products = Product.objects.filter(
        Q(categoris=cate.id) | 
        Q(categoris__parent=cate.id),
        is_verified=True
    ).exclude(id__in=no_store_id_product_id_list).order_by('?')
    context = {
        'products': products,
        'cate': cate,
    }
    return render(request, 'store/category.html', context)


def brandfiltering(request, slug):
    brands = get_object_or_404(Brand, slug=slug)
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    products_brands = Product.objects.filter(is_verified=True, brand=brands.id).exclude(id__in=no_store_id_product_id_list).order_by('?')
    context = {
        'products_brands': products_brands,
        'brands': brands
    }
    return render(request, 'store/brand.html', context)


def price_range_filtering(request, pk):
    price_ranges = get_object_or_404(PriceRange, pk=pk)
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    products = Product.objects.filter(is_verified=True, price_range=price_ranges.id).exclude(id__in=no_store_id_product_id_list)
    context = {
        'products': products,
        'price_ranges': price_ranges,
    }
    return render(request, 'store/products_price_range.html', context)


def campaign_product_filtering(request, slug):
    campaign_cat = get_object_or_404(Campaign, slug=slug)
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    campaign_product = CampaignProduct.objects.filter(
        campaign_category=campaign_cat.id).exclude(product__id__in=no_store_id_product_id_list).order_by('?')
    context = {
        'campaign_product': campaign_product,
        'campaign_cat': campaign_cat
    }
    return render(request, 'store/campaign-product.html', context)


def shop(request):
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    products = Product.objects.filter(is_verified=True).exclude(id__in=no_store_id_product_id_list).order_by('?')
    context = {
        'products': products
    }
    return render(request, 'store/shop.html', context)


def flash_sale(request):
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())

    products = Product.objects.filter(is_verified=True).exclude(id__in=no_store_id_product_id_list).order_by('?')
    context = {
        'products': products
    }
    return render(request, 'store/flash-sale-product.html', context)


def deal_of_the_day(request):
    no_store_id_product_id_list = list(Product.objects.filter(
        Q(user__is_vendor=True, user__vendorinformation__store_id__isnull=True) | 
        Q(user__is_vendor=False, user__profile__store_id__isnull=True),
        is_verified=True
    ).values_list('id', flat=True).distinct())
    deal_product = DealOfTheDayProduct.objects.all().exclude(product__id__in=no_store_id_product_id_list).order_by('?')

    context = {
        'deal_product': deal_product
    }
    return render(request, 'store/deal-of-the-day.html', context)


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item_qs = OrderItem.objects.filter(item=item, user=request.user, ordered=False)
    item_var = []
    # if request.method == 'GET':
    #     return render(request, 'store/product_detail.html', {'item': item})
    if request.method == 'POST':
        flashsale= request.POST.get('flashsale')
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 0))
        referer_url = request.META.get('HTTP_REFERER')
        try:
            if flashsale:
                flash_sales = FlashSaleProduct.objects.filter(product=item)
                for f in flash_sales:
                    if size and color:
                        if f.variation.size.name == size and f.variation.color.name == color:
                            variation = f.variation
                            vid = f.id
                    elif size:
                        if f.variation.size.name == size:
                            variation = f.variation
                            vid = f.id
                    elif color:
                        if f.variation.color.name == color:
                            variation = f.variation
                            vid = f.id
                    else:
                        variation = f.variation
                        vid = f.id
                flash_sale = FlashSaleProduct.objects.get(id=vid)
            else:
                if size and color:
                    variation = Variation.objects.get(product=item, size__name=size, color__name=color)
                elif size:
                    variation = Variation.objects.get(product=item, size__name=size)
                elif color:
                    variation = Variation.objects.get(product=item, color__name=color)
                else:
                    variation = Variation.objects.get(product=item)

            item_var.append(variation)
            
            if len(item_var) > 0:
                for items in item_var:
                    order_item_qs = order_item_qs.filter(variation__exact=items)
            
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                get_product_stock_quantity = Product.objects.get(id=order_item.item.id)
                
                if order_item.flashsale:
                    discounted_price = order_item.flashsale.flashsale_price
                else:
                    discounted_price = order_item.item.discount_price or order_item.item.price
                
                if order_item.quantity < get_product_stock_quantity.stock_quantity:
                    if quantity:
                        order_item.quantity += quantity
                    order_item.save()
                else:
                    messages.info(request, "Stock Quantity Not Available")
                    return redirect("cart-summary")
            else:
                try:
                    flash_sale_value = flash_sale 
                except NameError:
                    flash_sale_value = None 
                order_item = OrderItem.objects.create(
                    item=item,
                    user=request.user,
                    ordered=False,
                    flashsale = flash_sale_value
                )
                
                if quantity:
                    order_item.quantity = quantity
                    order_item.variation.add(*item_var)
                    order_item.save()
                else:
                    return redirect(referer_url)
                
            order_qs = Order.objects.filter(user=request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                if not order.items.filter(item__id=order_item.id).exists():
                    order.items.add(order_item)
                    messages.success(request, "Thank you! Item successfully added to your cart.")
                    return redirect(referer_url)
            else:
                ordered_date = timezone.now()
                order = Order.objects.create(
                    user=request.user, ordered_date=ordered_date)
                order.items.add(order_item)
                messages.info(request, "Item added to cart.")
                
        except Variation.DoesNotExist:
            messages.error(request, f"Variation not available for {size} {color if color else ''}.")
        return redirect(referer_url)


@login_required
def buy_now(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item_qs = OrderItem.objects.filter(
        item=item, user=request.user, ordered=False)
    item_var = []  # item variation
    if request.method == 'POST':
        flashsale= request.POST.get('flashsale')
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 0))
        try:
            if flashsale:
                flash_sales = FlashSaleProduct.objects.filter(product=item)
                for f in flash_sales:
                    if size and color:
                        if f.variation.size.name == size and f.variation.color.name == color:
                            variation = f.variation
                            vid = f.id
                    elif size:
                        if f.variation.size.name == size:
                            variation = f.variation
                            vid = f.id
                    elif color:
                        if f.variation.color.name == color:
                            variation = f.variation
                            vid = f.id
                    else:
                        variation = f.variation
                        vid = f.id
                flash_sale = FlashSaleProduct.objects.get(id=vid)
            else:
                if size and color:
                    variation = Variation.objects.get(product=item, size__name=size, color__name=color)
                elif size:
                    variation = Variation.objects.get(product=item, size__name=size)
                elif color:
                    variation = Variation.objects.get(product=item, color__name=color)
                else:
                    variation = Variation.objects.get(product=item)
                
            item_var.append(variation)

            if len(item_var) > 0:
                for items in item_var:
                    order_item_qs = order_item_qs.filter(
                        variation__exact=items,
                    )
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                get_product_stock_quantity = Product.objects.get(id=order_item.item.id)

                if order_item.flashsale:
                    discounted_price = order_item.flashsale.flashsale_price
                else:
                    discounted_price = order_item.item.discount_price or order_item.item.price

                if order_item.quantity < get_product_stock_quantity.stock_quantity:
                    quantity = request.POST.get('quantity')
                    if quantity != None:
                        if quantity:
                            order_item.quantity += int(quantity)
                        else:
                            order_item.quantity = int(quantity)
                    else:
                        return redirect('address')
                    order_item.save()
                else:
                    messages.info(request, "Stock Quantity Not avalable")
                    return redirect("address")
            else:
                # Create a new OrderItem
                try:
                    flash_sale_value = flash_sale 
                except NameError:
                    flash_sale_value = None 
                order_item = OrderItem.objects.create(
                    item=item,
                    user=request.user,
                    ordered=False,
                    flashsale=flash_sale_value
                )
                quantity = request.POST.get('quantity')
                if quantity != None:
                    order_item.quantity = int(quantity)
                    order_item.variation.add(*item_var)
                    order_item.save()
                else:
                    return redirect('address')

            order_qs = Order.objects.filter(user=request.user, ordered=False)
            if order_qs.exists():
                order = order_qs[0]
                # check if the order item is in the order
                if not order.items.filter(item__id=order_item.id).exists():
                    order.items.add(order_item)
                    messages.success(request, "Thank You successfully add")
                    return redirect('address')
            else:
                ordered_date = timezone.now()
                order = Order.objects.create(
                    user=request.user, ordered_date=ordered_date)
                order.items.add(order_item)
        except Variation.DoesNotExist:
            messages.error(request, f"Variation not available for {size} {color if color else ''}.")
        messages.info(request, "This item was added to cart.")
        return redirect('address')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.filter(item__slug=item.slug)[0]
            order_item.delete()
            messages.info(request, 'This item was removed from the cart.')
            return redirect('cart_summary')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect('cart_summary')
    else:
        messages.info(request, 'You do not have an active order.')
        return redirect('/')


@login_required
def cart_summary(request):
    try:
        now = timezone.now()
        order = Order.objects.get(user=request.user, ordered=False)
        if order.coupon:
            if order.coupon.is_verified != True or order.coupon.used >= order.coupon.max_value or order.coupon.valid_from > now or order.coupon.valid_to < now:
                messages.info(request, f"This {order.coupon.code} coupon isn't available now!")
                order.coupon = None
                order.save()

        out_of_stock = any(item.item.stock_quantity <= 0 for item in order.items.all())
        form = CouponCodeForm(request.POST or None)
        coupons = Coupon.objects.filter(
                valid_from__lte=now,
                valid_to__gte=now,
                is_verified = True,
                max_value__gte = 1,
                coupon_user__in=[request.user]
            )
        products_ids = list(OrderItem.objects.filter(user=request.user, ordered=False).values_list('item__id', flat=True).distinct())
        coupon_with_product = Coupon.objects.filter(product__id__in=products_ids).values_list('product__id', flat=True).distinct()

        if request.method == "POST":
            code = request.POST.get('code')
            order_item_id = request.POST.get('order_item_id')
            order_item = OrderItem.objects.get(id=order_item_id)
            coupon = Coupon.objects.filter(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                is_verified=True,
                max_value__gte=1,
                product=order_item.item
            ).exclude(max_value__lte=F('used')).first()
            if coupon:
                if coupon.minimum_price_range <= order_item.get_subtotal():
                    if coupon.coupon_type == 'Percentage':
                        if order_item.item.discount_price:
                            discount = (coupon.amount_or_percentage / 100) * order_item.item.discount_price
                            order_item.product_new_price = order_item.item.discount_price - discount
                        else:
                            discount = (coupon.amount_or_percentage / 100) * order_item.item.price
                            order_item.product_new_price = order_item.item.price - discount
                    else:
                        if order_item.item.discount_price:
                            order_item.product_new_price = max(order_item.item.discount_price - coupon.amount_or_percentage, 0)
                        else:
                            order_item.product_new_price = max(order_item.item.price - coupon.amount_or_percentage, 0)
                            
                    order_item.coupon = coupon
                    order_item.save()
                    messages.success(request, "Coupon applied successfully!")
                    return redirect('cart_summary')
                else:
                    messages.error(request, f"Minimum price must be {coupon.minimum_price_range}TK")
                    return redirect('cart_summary')
            else:
                messages.error(request, "Coupon does not exit")
                return redirect('cart_summary')

        context = {
            'order': order,
            'form': form,
            'out_of_stock': out_of_stock,
            'coupons':coupons,
            'coupon_with_product':coupon_with_product
            
        }
        return render(request, 'store/cart_summary.html', context)
    except ObjectDoesNotExist:
        return redirect('/')


from django.core.paginator import Paginator
@login_required
def order_summary(request):
    try:
        order_list = Order.objects.filter(user=request.user, ordered=True)
        paginator = Paginator(order_list, 6)
        page_number = request.GET.get("page")
        query = paginator.get_page(page_number)
        return render(request, 'store/order_summary.html', {'query': query})
    except ObjectDoesNotExist:
        return redirect('/')


@login_required
def product_order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    order_items = OrderItem.objects.filter(order=order)
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/order_details.html', context)



@login_required
def pathao_order_status(request, pk):
    order = Order.objects.get(pk=pk)
    order_items = OrderItem.objects.filter(order=order)
    order_items_ids = list(order_items.values_list('id',flat=True).distinct())
    fetch_consignment(order_items_ids)
    # print(f'====================================================')
    # print(f'called pathao_order_status = {order_items_ids = }')
    # print(f'====================================================')
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'store/pathao_order_status.html', context)


@login_required
def render_order_pdf_view(request, *args, **kwargs):
    pk = kwargs.get('pk')
    order = get_object_or_404(Order, pk=pk)
    logo = WebsiteInformation.objects.all().first()
    template_path = 'store/order-report.html'
    context = {
        'order': order,
        'logo': logo,
    }
    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'filename="eranian_order_invoice.pdf"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(
        html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


@login_required
def order_item_detail(request, pk):
    try:
        cart_items = OrderItem.objects.get(pk=pk, user=request.user, ordered=True)
        # user_review = ProductReview.objects.filter(user=request.user,product=cartitems.item)
        form = ProductReviewForm(request.POST, request.FILES)
        if request.method == 'POST':
            form = ProductReviewForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.product = cart_items.item
                form.rating = request.POST.get('rating')
                form.image = request.POST.get('image')
                form.save()
                messages.success(request, "Successful Save")
                return redirect('order_summary')
            else:
                messages.error(request, 'Please correct the error below.')
        context = {
            'cartitems': cart_items,
            'form': form,
            # 'user_review':user_review
        }
        return render(request, 'store/order_item_details.html', context)
    except ObjectDoesNotExist:
        return redirect('/')


@login_required
def add_coupon(request):
    now = timezone.now()
    if request.method == 'POST':
        form = CouponCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            order = Order.objects.get(user=request.user, ordered=False)
            coupon = Coupon.objects.filter(
                code__iexact=code,
                valid_from__lte=now,
                valid_to__gte=now,
                is_verified = True,
                coupon_user = request.user
            ).exclude(order__user=request.user, max_value__lte=F('used')).first()

            if not coupon:
                messages.error(request, 'You can\'t use the same coupon again, or the coupon does not exist')
                return redirect('cart_summary')
            else:
                try:
                    coupon.used += 1
                    coupon.save()
                    order.coupon = coupon
                    order.save()
                    messages.success(request, "Successfully added coupon.")
                except:
                    messages.error(request, "Max level exceeded for coupon")
                return redirect('cart_summary')
    else:
        return redirect('cart_summary')


@login_required
def product_quantity_increment(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            get_product_stock_quantity = Product.objects.get(id=order_item.item.id)
            if order_item.quantity >= 1:
                if order_item.quantity < get_product_stock_quantity.stock_quantity:
                    order_item.quantity += 1
                    order_item.save()
                    return redirect("cart_summary")
                else:
                    messages.info(request, "Stock Quantity Not available")
                    return redirect("cart_summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart_summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart_summary", slug=slug)


@login_required
def product_quantity_decrement(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                return redirect("cart_summary")
            else:
                order_item.delete()
                messages.info(request, "This product was deleted from your cart")
            return redirect("cart_summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("cart_summary", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("cart_summary", slug=slug)


# WishList
@login_required
def add_to_wishlist(request, slug):
    products = get_object_or_404(Product, slug=slug)
    wish_product, created = WhishLIst.objects.get_or_create(
        wish_product=products, slug=products.slug, user=request.user)
    messages.info(request, "This Product add your wish list")
    return redirect('home')


@login_required
def wish_list(request):
    wish_product = WhishLIst.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wish_product': wish_product})


@login_required
def delete_wish_list(request, slug):
    wish_product = WhishLIst.objects.filter(user=request.user, slug=slug)
    wish_product.delete()
    messages.info(request, "This product delete from your wishlist.")
    return redirect('wishlist')


@login_required
def myreview(request):
    cartitems = OrderItem.objects.filter(user=request.user, ordered=True).order_by('-id')
    return render(request, 'store/my-review.html', {'cartitems': cartitems})


@login_required
def review(request, pk):
    try:
        cartitems = OrderItem.objects.get(pk=pk, user=request.user, ordered=True)
        form = ProductReviewForm(request.POST, request.FILES)
        if request.method == 'POST':
            form = ProductReviewForm(request.POST, request.FILES)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.product = cartitems.item
                form.rating = request.POST.get('rating')
                form.image = request.POST.get('image')
                form.save()
                messages.success(request, "Successful Save")
                return redirect('my-review')
            else:
                messages.error(request, 'Please correct the error below.')
        context = {
            'cartitems': cartitems,
            'form': form,
        }
        return render(request, 'store/review.html', context)
    except ObjectDoesNotExist:
        return redirect('/')


def contact_us(request):
    form = Contact_Form(request.POST)
    if request.method == 'POST':
        form = Contact_Form(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')

            submit = ConductData(
                name=name,
                phone=phone,
                email=email,
                subject=subject,
                message=message
            )
            submit.save()
            messages.success(request, 'Successfully Submit')
            return redirect('home')
    else:
        form = Contact_Form()
    context = {
        'form': form
    }
    return render(request, 'store/contact.html', context)


# Privacy Policy
# Terms and conditions
# Our Mission & Vision
# Returns Policy
# Shipping and Delivery

def privacy_policy(request):
    texts = PrivacyPolicy.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/privacy-policy.html', context)


def terms_conditions(request):
    texts = TermsAndConditions.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/terms-conditions.html', context)


def vision(request):
    texts = Vision.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/mission-vision.html', context)


def mission(request):
    texts = Mission.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/mission-vision.html', context)


def returns_policy(request):
    texts = Returns_Policy.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/returns-policy.html', context)


def shipping_delivery(request):
    texts = ShippingAndDelivery.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/shipping-delivery.html', context)


def about_us(request):
    texts = AboutUs.objects.all().last()
    context = {
        'texts': texts
    }
    return render(request, 'store/about-us.html', context)


def videogallery(request):
    videos = VideoGallery.objects.all()

    context = {
        'videos': videos
    }
    return render(request, 'store/videogallery.html', context)


def imagegallery(request):
    img = ImageGallery.objects.all()

    context = {
        'img': img
    }
    return render(request, 'store/imagegallery.html', context)


def order_tracking(request, tracking_code):
    # Dictionary mapping delivery status names to descriptions
    DELIVERY_STATUS_DESCRIPTIONS = {
        "pending": "Consignment is not delivered or cancelled yet.",
        "delivered_approval_pending": "Consignment is delivered but waiting for admin approval.",
        "partial_delivered_approval_pending": "Consignment is delivered partially and waiting for admin approval.",
        "cancelled_approval_pending": "Consignment is cancelled and waiting for admin approval.",
        "unknown_approval_pending": "Unknown Pending status. Need contact with the support team.",
        "delivered": "Consignment is delivered and balance added.",
        "partial_delivered": "Consignment is partially delivered and balance added.",
        "cancelled": "Consignment is cancelled and balance updated.",
        "hold": "Consignment is held.",
        "in_review": "Order is placed and waiting to be reviewed.",
        "unknown": "Unknown status. Need contact with the support team."
    }
    Api_Key = 'lcajvcs30r3kjei7uh4koit3dw1y6fq9'
    Secret_Key = 'sfrpkpdrdg9buwtu5tb9lpqw'
    url = f'https://portal.steadfast.com.bd/api/v1//status_by_trackingcode/{tracking_code}/'
    headers = {
        "Api-Key": Api_Key,
        "Secret-Key": Secret_Key,
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    delivery_status = response.json().get("delivery_status", "unknown")
    status = ""
    for x, y in DELIVERY_STATUS_DESCRIPTIONS.items():
        if x == delivery_status:
            status = y
            break
    return render(request, 'store/order_status.html', {'response': status})


# @login_required
# def return_product(request):
#     order_items = OrderItem.objects.filter(user=request.user, ordered=True)
   
#     item_price = ReturnProduct.objects.filter(customer=request.user)
#     if request.method == 'POST':
#         form = ReturnProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             return_product_instance = form.save(commit=False)
#             return_product_instance.customer = request.user
#             return_product_instance.save()
#             form.save_m2m()

#             return redirect('return-product')
#     else:
#         form = ReturnProductForm()
#         form.fields['items'].queryset = order_items
   
#     return render(request, 'store/return-product.html', {'form': form, 'order_items': order_items, 'item_price': item_price})




from django.db.models import Subquery

# @login_required
# def return_product(request):
#     return_product_items = ReturnProduct.objects.filter(customer=request.user).values('items__id')
#     if return_product_items:
#         order_items = Order.objects.filter(
#             user=request.user,
#             ordered=True,
#             order_status='Complete'
#         ).exclude(items_id_in=Subquery(return_product_items))
#     else:
#         order_items = Order.objects.filter(
#             user=request.user,
#             ordered=True,
#             order_status='Complete'
#         )
#     if request.method == 'POST':
#         form = ReturnProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             return_product_instance = form.save(commit=False)
#             return_product_instance.customer = request.user
#             return_product_instance.save()
#             form.save_m2m()
#             return redirect('return-status')
#     else:
#         form = ReturnProductForm()
#         form.fields['items'].queryset = order_items
#     return render(request, 'store/return-product.html', {'form': form, 'order_items': order_items})


# @login_required
# def return_product(request):
#     return_product_items = ReturnProduct.objects.filter(customer=request.user).values('items__id')
    
#     if return_product_items.exists():
#         order_items = Order.objects.filter(
#             user=request.user,
#             ordered=True,
#             order_status='Complete'
#         ).exclude(items__id__in=Subquery(return_product_items))
#     else:
#         order_items = Order.objects.filter(
#             user=request.user,
#             ordered=True,
#             order_status='Complete'
#         )
    
#     if request.method == 'POST':
#         form = ReturnProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             return_product_instance = form.save(commit=False)
#             return_product_instance.customer = request.user
#             return_product_instance.save()
#             form.save_m2m()
#             return redirect('return-status')
#     else:
#         form = ReturnProductForm()
#         form.fields['items'].queryset = order_items

#     return render(request, 'store/return-product.html', {'form': form, 'order_items': order_items})



# @login_required
# def return_product(request):
#     return_product_items = ReturnProduct.objects.filter(customer=request.user).values('items__id')
    
#     orders = Order.objects.filter(user=request.user, ordered=True,
#             order_status='Complete').exclude(items__id__in=Subquery(return_product_items))
#     for order in orders:
#             remaining_return_days = order.calculate_return_duration()
#             order.remaining_return_days = remaining_return_days
            
#             print(f"Order Item ID: {order.id}, Remaining Return Days: {remaining_return_days}")
            
#     if return_product_items.exists() and remaining_return_days > 0:
#         order_items = Order.objects.filter(
#             user=request.user,
#             ordered=True,
#             order_status='Complete'
#         ).exclude(items__id__in=Subquery(return_product_items))
#     else:
#         order_items = Order.objects.filter(
#             user=request.user,
#             ordered=True,
#             order_status='Complete'
#         )
    
        
#     if request.method == 'POST':
#         form = ReturnProductForm(request.POST, request.FILES)
#         if form.is_valid():
#             return_product_instance = form.save(commit=False)
#             return_product_instance.customer = request.user
#             return_product_instance.save()
#             form.save_m2m()
#             return redirect('return-status')
#     else:
#         form = ReturnProductForm()
#         form.fields['items'].queryset = order_items

#     return render(request, 'store/return-product.html', {'form': form, 'order_items': order_items})

@login_required
def return_product(request):
    if request.method == 'POST':
        form = ReturnProductForm(request.POST, request.FILES)
        ImgesFormSet = ReturnProductImagesFormSet(request.POST, request.FILES, prefix='images')

        if form.is_valid() and ImgesFormSet.is_valid():
            
            return_product_instance = form.save(commit=False)
            return_product_instance.customer = request.user
            return_product_instance.save()
            for image_form in ImgesFormSet:
                image_instance = image_form.save(commit=False)
                image_instance.return_product = return_product_instance 
                image_instance.save()
            return redirect('return-status')
    else:
        form = ReturnProductForm()
        ImgesFormSet = ReturnProductImagesFormSet(prefix='images')

    return render(request, 'store/return-product.html', {'form': form,'ImgesFormSet':ImgesFormSet})


@login_required
def returns_product_status(request):
    return_products = ReturnProduct.objects.filter(customer=request.user, remove_from_customer=False)
    if request.method == 'POST':
        delete_id = request.POST['delete_id']
        return_pro = ReturnProduct.objects.get(id=delete_id)
        return_pro.remove_from_customer = True
        return_pro.save()
    return render(request, 'store/returns_product-status.html', {'return_products': return_products, 'status':'m-active'})