import requests
from django.shortcuts import get_object_or_404, render, redirect
from store.models import *
from .forms import *
from django.views.generic import *
from django.contrib import messages
from userapp.decorators import *
from userapp.models import User
from django.contrib.auth.decorators import login_required
from userapp.forms import *
from django.contrib.auth import update_session_auth_hash
from other_vendors.models import VendorInformation
from other_vendors.forms import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from store.models import ShipingAddress
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from django.core import serializers
from django.db import transaction
from django.db.models import Q
from django.core.paginator import Paginator
from paymentApp.utils import fetch_consignment, get_access_token



# Create your views here.
@login_required
@daseboard_required
def dashboard_home(request):
    user = request.user
    total_users = User.objects.count()
    total_customer = User.objects.filter(is_customer=True).count()
    total_vendor = User.objects.filter(is_vendor=True).count()
    total_staff = User.objects.filter(is_staff=True, is_superuser=False).count()
    total_superuser = User.objects.filter(is_superuser=True).count()

    all_product_count = Product.objects.all().count()
    all_accepted_product_count = Product.objects.filter(is_verified=True).count()
    all_pending_product_count = Product.objects.filter(is_verified=False).count()

    total_order = Order.objects.filter(ordered=True).count()
    total_pending_order = Order.objects.filter(ordered=True, order_status='Pending').count()
    total_processing_order = Order.objects.filter(ordered=True, order_status='Processing').count()
    total_on_the_way_order = Order.objects.filter(ordered=True, order_status='On the way').count()
    total_complete_order = Order.objects.filter(ordered=True, order_status='Complete').count()
    total_cancel_order = Order.objects.filter(ordered=True, order_status='Cancel').count()
    total_return_order = Order.objects.filter(ordered=True, order_status='Return').count()

    """" user wise data query section start """
    user_total_product_count = Product.objects.filter(user=user).count()
    user_accepted_product_count = Product.objects.filter(user=user, is_verified=True).count()
    user_pending_product_count = Product.objects.filter(user=user, is_verified=False).count()

    user_total_order = Order.objects.filter(user=user, ordered=True).count()
    pending_order = Order.objects.filter(user=user, ordered=True, order_status='Pending').count()
    processing_order = Order.objects.filter(user=user, ordered=True, order_status='Processing').count()
    on_the_way_order = Order.objects.filter(user=user, ordered=True, order_status='On the way').count()
    complete_order = Order.objects.filter(user=user, ordered=True, order_status='Complete').count()
    cancel_order = Order.objects.filter(user=user, ordered=True, order_status='Cancel').count()
    return_order = Order.objects.filter(user=user, ordered=True, order_status='Return').count()
    """" user wise data query section end """

    bkash_eraning = 0
    bkash = BkashPaymentExecute.objects.all()
    for i in bkash:
        bkash_eraning += float(i.amount)

    context = {
        'total_users': total_users,
        'total_customer': total_customer,
        'total_vendor': total_vendor,
        'total_staff': total_staff,
        'total_superuser': total_superuser,

        'all_product_count': all_product_count,
        'all_accepted_product_count': all_accepted_product_count,
        'all_pending_product_count': all_pending_product_count,

        'total_order': total_order,
        'total_pending_order': total_pending_order,
        'total_processing_order': total_processing_order,
        'total_on_the_way_order': total_on_the_way_order,
        'total_complete_order': total_complete_order,
        'total_cancel_order': total_cancel_order,
        'total_return_order': total_return_order,

        'user_total_product_count': user_total_product_count,
        'user_accepted_product_count': user_accepted_product_count,
        'user_pending_product_count': user_pending_product_count,

        'user_total_order': user_total_order,
        'pending_order': pending_order,
        'processing_order': processing_order,
        'on_the_way_order': on_the_way_order,
        'complete_order': complete_order,
        'cancel_order': cancel_order,
        'return_order': return_order,

        'bkash_eraning': bkash_eraning,
        }
    return render(request, 'dashboard/index.html', context)


@login_required
@daseboard_required
def pending_product_list(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    user_type = request.GET.get('user_type', '')

    time_period = request.GET.get('time_period', '')

    categories = ProductCategory.objects.filter(is_verified=True)
    brands = Brand.objects.filter(is_verified=True)

    products = Product.objects.filter(is_verified=False)

    if not (request.user.is_superuser or request.user.is_staff):
        products = products.filter(user=request.user)
    if search:
        products = products.annotate(
            total_stock=Sum('variation__quantity')
        ).filter(Q(product_name__icontains=search) | Q(id__icontains=search) | Q(total_stock__icontains=search))
    if category:
        products = products.filter(categoris_id=category)
    if brand:
        products = products.filter(brand_id=brand)
    if user_type:
        if user_type == 'superuser':
            products = products.filter(user__is_superuser=True)
        
        elif user_type == 'staff':
            products = products.filter(user__is_staff=True)
        elif user_type == 'customer':
            products = products.filter(user__is_customer=True)
        elif user_type == 'vendor':
            products = products.filter(user__is_vendor=True)

    if time_period:
        now = datetime.now()
        if time_period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif time_period == 'yesterday':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end = start + timedelta(days=1)
        elif time_period == 'thisweek':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif time_period == 'lastweek':
            start = now - timedelta(days=now.weekday() + 7)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif time_period == 'thismonth':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=now.day)
        elif time_period == 'lastmonth':
            start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            end = start + timedelta(days=31)
        elif time_period == 'thisyear':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=365)
        elif time_period == 'lastyear':
            start = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=365)
        
        products = products.filter(created_at__range=(start, end))

    return render(request, 'dashboard/product/pending-product-list.html', {
        'products': products,
        'categories': categories,
        'brands': brands
    })


@login_required
@daseboard_required
def publish_product_list(request):
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    brand = request.GET.get('brand', '')
    user_type = request.GET.get('user_type', '')
    time_period = request.GET.get('time_period', '')

    categories = ProductCategory.objects.filter(is_verified=True)
    brands = Brand.objects.filter(is_verified=True)

    products = Product.objects.filter(is_verified=True)

    if not (request.user.is_superuser or request.user.is_staff):
        products = products.filter(user=request.user)

    if search:
        products = products.annotate(
            total_stock=Sum('variation__quantity')
        ).filter(Q(product_name__icontains=search) | Q(id__icontains=search) | Q(total_stock__icontains=search))
    if category:
        products = products.filter(categoris_id=category)
    if brand:
        products = products.filter(brand_id=brand)
    if user_type:
        if user_type == 'superuser':
            products = products.filter(user__is_superuser=True)
        elif user_type == 'staff':
            products = products.filter(user__is_staff=True)
        elif user_type == 'customer':
            products = products.filter(user__is_customer=True)
        elif user_type == 'vendor':
            products = products.filter(user__is_vendor=True)
    if time_period:
        now = datetime.now()
        if time_period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif time_period == 'yesterday':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end = start + timedelta(days=1)
        elif time_period == 'thisweek':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif time_period == 'lastweek':
            start = now - timedelta(days=now.weekday() + 7)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif time_period == 'thismonth':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=now.day)
        elif time_period == 'lastmonth':
            start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            end = start + timedelta(days=31)
        elif time_period == 'thisyear':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=365)
        elif time_period == 'lastyear':
            start = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=365)
        
        products = products.filter(created_at__range=(start, end))

    return render(request, 'dashboard/product/publish-product-list.html', {
        'products': products,
        'categories': categories,
        'brands': brands
    })


@login_required
@daseboard_required
def product_detail(request, pk):
    product = Product.objects.get(pk=pk)
    return render(request, 'dashboard/product/product-detail.html', {'product': product})


class ProductInline():
    form_class = ProductForm
    model = Product
    template_name = "dashboard/product/product-add.html"

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all(x.is_valid() for x in named_formsets.values()):
            return self.render_to_response(self.get_context_data(form=form))

        form.instance.user = self.request.user
        self.object = form.save()  # Save the main form to get the Product instance

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, f'formset_{name}_valid', None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        return redirect('publish_product_list')
    
    def form_invalid(self, form):
        named_formsets = self.get_named_formsets()
     
        for name, formset in named_formsets.items():
            print(f"Formset '{name}' errors:", formset.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def formset_variants_valid(self, formset):
        variants = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for variant in variants:
            variant.product = self.object  # Associate the Product instance
            variant.save()

    def formset_images_valid(self, formset):
        images = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for image in images:
            image.product = self.object  # Associate the Product instance
            image.save()

class ProductCreate(ProductInline, CreateView):
    def get_context_data(self, **kwargs):
        ctx = super(ProductCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'variants': VariantFormSet(prefix='variants'),
                'images': ImageFormSet(prefix='images'),
            }
        else:
            return {
                'variants': VariantFormSet(self.request.POST or None, self.request.FILES or None, prefix='variants'),
                'images': ImageFormSet(self.request.POST or None, self.request.FILES or None, prefix='images'),
            }
        


class ProductUpdate(ProductInline, UpdateView):
    def get_context_data(self, **kwargs):
        ctx = super(ProductUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        variants_formset = VariantFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='variants')
        images_formset = ImageFormSet(self.request.POST or None, self.request.FILES or None, instance=self.object, prefix='images')

        return {
            'variants': variants_formset,
            'images': images_formset,
        }
    

@login_required
@daseboard_required
def delete_image(request, pk):
    try:
        image = ProductImgGallery.objects.get(id=pk)
    except Image.DoesNotExist:
        messages.success(request, 'Object Does not exit')
        return redirect('update_product', pk=image.product.id)

    image.delete()
    messages.success(request, 'Image successfully deleted!')
    return redirect('product-update', pk=image.product.id)


@login_required
@daseboard_required
def delete_variant(request, pk):
    try:
        variant = Variation.objects.get(id=pk)
    except variant.DoesNotExist:
        messages.success(request, 'Object Does not exit')
        return redirect('product-update', pk=variant.product.id)

    variant.delete()
    messages.success(request, 'Variant successfully deleted!')
    return redirect('product-update', pk=variant.product.id)


@login_required
@daseboard_required
def dashboard_product_delete(request, pk):
    product = Product.objects.get(pk=pk)
    product.delete()
    messages.success(request, 'Product successfully deleted!')
    return redirect('dashboard-home')


@login_required
@daseboard_required
def product_verify(request):
    if request.method == 'POST':
        selected_products = request.POST.getlist('selected_products')
        for product_id in selected_products:
            product = get_object_or_404(Product, id=product_id)
            product.is_verified = True
            product.save()
        messages.success(request, 'Selected products have been verified.')
    return redirect('pending_product_list')


@login_required
@daseboard_required
def product_delete(request):
    if request.method == 'POST':
        selected_products = request.POST.getlist('selected_products')
        for product_id in selected_products:
            product = get_object_or_404(Product, id=product_id)
            product.delete()
        messages.success(request, 'Selected products have been deleted.')
    return redirect('pending_product_list')


# Category
# @login_required
# @daseboard_required
# def verified_category_list(request):
#     categories = ProductCategory.objects.filter(is_verified=True)
#     return render(request, 'dashboard/category/verified-category-list.html', {'categories': categories})


# @login_required
# @daseboard_required
# def pending_category_list(request):
#     categories = ProductCategory.objects.filter(is_verified=False)
#     return render(request, 'dashboard/category/pending-category-list.html', {'categories': categories})


# @login_required
# @daseboard_required
# def category_list(request):
#     categories = ProductCategory.objects.all()
#     category_data = [{
#         'id': category.id,
#         'name': category.category_name,
#         'slug': category.slug,
#         'parent': category.parent.category_name if category.parent else None,
#         'image': category.img.url if category.img else None,
#         'commission': category.commission,
#         'is_verified': category.is_verified
#     } for category in categories]
#     return JsonResponse({'categories': category_data}, safe=False)
#     # return render(request, 'dashboard/category/add-category.html', {'categories': categories})


# def add_category(request):
#     categories = ProductCategory.objects.all()
#     if request.method == 'POST':
#         form = CategoryForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
        
#             return JsonResponse({'status': 'success', 'message': 'Category successfully added.'})
#         else:
#             print(form.errors)
#             return JsonResponse({'status': 'error', 'message': 'Category form submission failed.'})
    
#     return render(request, 'dashboard/category/add-category.html', {'categories': categories})


# def category_update(request, slug):
#     categories = ProductCategory.objects.all()
#     category = get_object_or_404(ProductCategory, slug=slug)

#     if request.method == 'POST':
#         form = CategoryForm(request.POST, request.FILES, instance=category)
#         if form.is_valid():
#             form.save()
#             return redirect('add_category')
#         else:
#             print(form.errors)
#             messages.error(request, 'Category List Failed')
#     form = CategoryForm(instance=category)

#     context = {
#         'categories': categories,
#         'category': category,
#         'form': form,
#     }
    
#     return render(request, 'dashboard/category/add-category.html', context)


# def category_update(request, slug):
#     category = get_object_or_404(ProductCategory, slug=slug)

#     # Serialize to JSON
#     data = serializers.serialize('json', [category])
#     # Convert to Python object for easier manipulation
#     # json_data = json.loads(data)[0]['fields']

#     return JsonResponse(data, safe=False)


# def category_update(request, slug):
#     try:
#         category = ProductCategory.objects.get(slug=slug)
#         data = {
#             'name': category.category_name,
#             'img': category.img.url if category.img else '',  # Handle image field
#             'parent': category.parent.id if category.parent else '',
#             'commission': category.commission if category.commission else '',
#             'is_verified': category.is_verified,
#         }
#         return JsonResponse(data, safe=False)
#     except ProductCategory.DoesNotExist:
#         return JsonResponse({'error': 'Category not found'}, status=404)



# @login_required
# @daseboard_required
# @csrf_exempt
# def category_delete(request, slug):

#     try:
#         category = ProductCategory.objects.get(slug=slug)
#         category.delete()
#         return JsonResponse({'status': 'success', 'message': 'Category successfully deleted!'})
#     except ProductCategory.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Category does not exist.'})


# @login_required
# @daseboard_required
# def selected_category_verify(request):
#     if request.method == 'POST':
#         selected_categories = request.POST.getlist('selected_categories')
#         print(selected_categories)
#         for category in selected_categories:
#             category = get_object_or_404(ProductCategory, id=category)
#             category.is_verified = True
#             category.save()
#         messages.success(request, 'Selected category have been verified.')
#     return redirect('pending_category_list')


# @login_required
# @daseboard_required
# def selected_category_delete(request):
#     if request.method == 'POST':
#         selected_categories = request.POST.getlist('selected_categories')
#         for category in selected_categories:
#             category = get_object_or_404(ProductCategory, id=category)
#             category.delete()
#         messages.success(request, 'Selected categories have been deleted.')
#     return redirect('pending_category_list')



# category
@login_required
@daseboard_required
def category_data(request): # use
    query_data = request.GET.get('query_data', 'All')
    if query_data == 'All':
        obj = ProductCategory.objects.all().order_by('-id')
    elif query_data == 'Pending':
        obj = ProductCategory.objects.filter(is_verified=False).order_by('-id')
    elif query_data == 'Complete':
        obj = ProductCategory.objects.filter(is_verified=True).order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    objects = None
    added = False
    form = ProductCategoryForm()
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            objects = ProductCategory.objects.get(id=obj_id)
        else:
            added = True
        form = ProductCategoryForm(request.POST, request.FILES, instance=objects)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your Category has been successfully updated!')
                return redirect('category_data')
            else:
                messages.success(request, 'Your Category has been successfully added!')
        else:
            messages.error(request, 'Data didn"t valid!')
            return redirect('category_data')
    return render(request, 'dashboard/product_categories/category-data.html', {'query': query, 'form': form, 'added':added, 'query_data':query_data})


@login_required
@daseboard_required
def selected_category_verify(request): # use
    if request.method == 'POST':
        selected_categories = request.POST.getlist('seleted_category')
        for category in selected_categories:
            category = get_object_or_404(ProductCategory, id=category)
            category.is_verified = True
            category.save()
        messages.success(request, 'Selected category have been verified.')
    return redirect('category_data')


@login_required
@daseboard_required
def selected_category_delete(request): # use
    if request.method == 'POST':
        selected_categories = request.POST.getlist('seleted_category')
        for category in selected_categories:
            category = get_object_or_404(ProductCategory, id=category)
            category.delete()
        messages.success(request, 'Selected categories have been deleted.')
    return redirect('category_data')


@login_required
@daseboard_required
def category_create(request): # use
    parent_categories = ProductCategory.get_parent_categories()
    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created admin will verify it!')
            return redirect('category_create')
        else:
            messages.error(request, 'Error adding.')
    else:
        form = ProductCategoryForm()
    return render(request, 'dashboard/product_categories/create.html', {'form': form, 'parent_categories': parent_categories})


@login_required
@daseboard_required
def category_delete(request, category_id): # use
    category = get_object_or_404(ProductCategory, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted.')
    return redirect('category_data')




@login_required
@daseboard_required
def category_list(request):
    categories = ProductCategory.objects.all()
    return render(request, 'dashboard/product_categories/list.html', {'categories': categories})


@login_required
@daseboard_required
def category_filter(request):
    status = request.GET.get('status', 'All')

    if status == 'All':
        categories = ProductCategory.objects.all()
    elif status == 'Pending':
        categories = ProductCategory.objects.filter(is_verified=False)
    elif status == 'Verified':
        categories = ProductCategory.objects.filter(is_verified=True)
    else:
        categories = ProductCategory.objects.all()

    return JsonResponse({'categories': list(categories.values())}, safe=False)



@login_required
@daseboard_required
def category_update(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    parent_categories = ProductCategory.get_parent_categories()

    # print(request.POST, request.FILES)

    if request.method == 'POST':
        form = ProductCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category saved.')
            return redirect('category_list')
        else:
            messages.error(request, 'Error saving.')
    else:
        form = ProductCategoryForm(instance=category)
    return render(request, 'dashboard/product_categories/update.html', {'form': form, 'parent_categories': parent_categories})


#Brand
@login_required
@daseboard_required
def brand_data(request): # use
    query_data = request.GET.get('query_data', 'All')
    if query_data == 'All':
        obj = Brand.objects.all().order_by('-id')
    elif query_data == 'Pending':
        obj = Brand.objects.filter(is_verified=False).order_by('-id')
    elif query_data == 'Complete':
        obj = Brand.objects.filter(is_verified=True).order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    objects = None
    added = False
    form = BrandAddForm()
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            objects = Brand.objects.get(id=obj_id)
        else:
            added = True
        form = BrandAddForm(request.POST, request.FILES, instance=objects)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your Brand has been successfully updated!')
                return redirect('brand_data')
            else:
                messages.success(request, 'Your Brand has been successfully added!')
    return render(request, 'dashboard/product_brand/brand-data.html', {'query': query, 'form': form, 'added':added, 'query_data':query_data})


@login_required
@daseboard_required
def selected_brand_verify(request): # use
    if request.method == 'POST':
        selected_brands = request.POST.getlist('selected_brands')
        for brand in selected_brands:
            brand = get_object_or_404(Brand, id=brand)
            brand.is_verified = True
            brand.save()
        messages.success(request, 'Selected brands have been verified.')
    return redirect('brand_data')


@login_required
@daseboard_required
def selected_brand_delete(request): # use
    if request.method == 'POST':
        selected_brands = request.POST.getlist('selected_brands')
        for brand in selected_brands:
            brand = get_object_or_404(Brand, id=brand)
            brand.delete()
        messages.success(request, 'Selected brands have been deleted.')
    return redirect('brand_data')


@login_required
@daseboard_required
def brand_create(request): # use
    if request.method == 'POST':
        form = BrandAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand created admin will verify it!')
            return redirect('brand_create')
    else:
        form = BrandAddForm()
    return render(request, 'dashboard/product_brand/create.html', {'form': form})


@login_required
@daseboard_required
def brand_delete(request, slug): # use
    brand = Brand.objects.get(slug=slug)
    brand.delete()
    messages.success(request, 'Brand successfully deleted!')
    return redirect('brand_data')





@login_required
@daseboard_required
def brand_list(request):
    brands = Brand.objects.filter()
    return render(request, 'dashboard/product_brand/list.html', {'brands': brands})


@login_required
@daseboard_required
def brand_filter(request):
    status = request.GET.get('status', 'All')

    if status == 'All':
        brands = Brand.objects.all()
    elif status == 'Pending':
        brands = Brand.objects.filter(is_verified=False)
    elif status == 'Verified':
        brands = Brand.objects.filter(is_verified=True)
    else:
        brands = Brand.objects.all()

    return JsonResponse({'brands': list(brands.values())}, safe=False)


@login_required
@daseboard_required
def brand_update(request, slug):
    brands = Brand.objects.get(slug=slug)
    form = BrandAddForm(request.POST, request.FILES, instance=brands)
    if request.method == 'POST':
        form = BrandAddForm(request.POST, request.FILES, instance=brands)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Brand successfully updated!')
            return redirect('brand_list')
    else:
        form = BrandAddForm(instance=brands)
    context = {
        'brands': brands,
        'form': form,
    }
    return render(request, 'dashboard/product_brand/update.html', context)

# @login_required
# @daseboard_required
# def brand_delete(request, slug):
#     brand = Brand.objects.get(slug=slug)
#     brand.delete()
#     messages.success(request, 'Brand successfully deleted!')
#     return redirect('brand_list')


# @login_required
# @daseboard_required
# def selected_brand_verify(request):
#     if request.method == 'POST':
#         selected_brands = request.POST.getlist('selected_brands')
#         for brand in selected_brands:
#             brand = get_object_or_404(Brand, id=brand)
#             brand.is_verified = True
#             brand.save()
#         messages.success(request, 'Selected brands have been verified.')
#     return redirect('brand_list')


# @login_required
# @daseboard_required
# def selected_brand_delete(request):
#     if request.method == 'POST':
#         selected_brands = request.POST.getlist('selected_brands')
#         for brand in selected_brands:
#             brand = get_object_or_404(Brand, id=brand)
#             brand.delete()
#         messages.success(request, 'Selected brands have been deleted.')
#     return redirect('brand_list')

#Brand
# @login_required
# @daseboard_required
# def verified_brand_list(request):
#     brands = Brand.objects.filter(is_verified=True)
#     return render(request, 'dashboard/brand/verified-brand-list.html', {'brands': brands})


# @login_required
# @daseboard_required
# def pending_brand_list(request):
#     brands = Brand.objects.filter(is_verified=False)
#     return render(request, 'dashboard/brand/pending-brand-list.html', {'brands': brands})


# @login_required
# @daseboard_required
# def add_brand(request):
#     brands = Brand.objects.all()
#     if request.method == 'POST':
#         form = BrandAddForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Brand successfully added!')
#             return redirect('pending_brand_list')
#     else:
#         form = BrandAddForm()
#     # return render(request, 'dashboard/brand/add-brand.html', {'form': form})
#     return render(request, 'dashboard/brand/brand-form.html', {'form': form, 'brands': brands})


# @login_required
# @daseboard_required
# def brand_update(request, slug):
#     brands = Brand.objects.get(slug=slug)
#     form = BrandAddForm(request.POST, request.FILES, instance=brands)
#     if request.method == 'POST':
#         form = BrandAddForm(request.POST, request.FILES, instance=brands)
#         if form.is_valid():
#             form.image = request.POST.get('image')
#             form.save()
#             messages.success(request, 'Brand successfully updated!')
#             return redirect('verified_brand_list')
#     else:
#         form = BrandAddForm(instance=brands)
#     context = {
#         'brands': brands,
#         'form': form,
#     }
#     return render(request, 'dashboard/brand/add-brand.html', context)


# @login_required
# @daseboard_required
# def brand_delete(request, slug):
#     brand = Brand.objects.get(slug=slug)
#     brand.delete()
#     messages.success(request, 'Brand successfully deleted!')
#     return redirect('verified_brand_list')


# @login_required
# @daseboard_required
# def selected_brand_verify(request):
#     if request.method == 'POST':
#         selected_brands = request.POST.getlist('selected_brands')
#         for brand in selected_brands:
#             brand = get_object_or_404(Brand, id=brand)
#             brand.is_verified = True
#             brand.save()
#         messages.success(request, 'Selected brands have been verified.')
#     return redirect('pending_brand_list')


# @login_required
# @daseboard_required
# def selected_brand_delete(request):
#     if request.method == 'POST':
#         selected_brands = request.POST.getlist('selected_brands')
#         for brand in selected_brands:
#             brand = get_object_or_404(Brand, id=brand)
#             brand.delete()
#         messages.success(request, 'Selected brands have been deleted.')
#     return redirect('pending_brand_list')



#Banner
@login_required
@daseboard_required
def banner_data(request):
    obj = Banner.objects.all().order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    banner = None
    added = False
    form = BannerForm()
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            banner = Banner.objects.get(id=obj_id)
        else:
            added = True
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your banner has been successfully updated!')
                return redirect('banner_data')
            else:
                messages.success(request, 'Your banner has been successfully added!')
    return render(request, 'dashboard/banner/banner-data.html', {'query': query, 'form': form, 'added':added})


@login_required
@daseboard_required
def banner_delete(request, pk):
    banner = Banner.objects.get(pk=pk)
    banner.delete()
    messages.success(request, 'Banner successfully deleted!')
    return redirect('banner_data')



@login_required
@daseboard_required
def banner_list(request):
    banner = Banner.objects.all()
    return render(request, 'dashboard/banner/banner-list.html', {'banner': banner})


@login_required
@daseboard_required
def banner_add(request):
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your banner has been successfully added!')
            return redirect('banner-list')
    else:
        form = BannerForm()
    return render(request, 'dashboard/banner/banner-add.html', {'form': form})


@login_required
@daseboard_required
def banner_update(request, pk):
    banner = Banner.objects.get(pk=pk)
    form = BannerForm(request.POST, request.FILES, instance=banner)
    if request.method == 'POST':
        form = BannerForm(request.POST, request.FILES, instance=banner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Banner successfully updated!')
            return redirect('banner-list')
    else:
        form = BannerForm(instance=banner)
    context = {
        'banner': banner,
        'form': form,
    }
    return render(request, 'dashboard/banner/banner-add.html', context)


# @login_required
# @daseboard_required
# def banner_delete(request, pk):
#     banner = Banner.objects.get(pk=pk)
#     banner.delete()
#     messages.success(request, 'Banner successfully deleted!')
#     return redirect('banner-list')


#Logo
@login_required
@daseboard_required
def logo_list(request):
    logo = WebsiteInformation.objects.all()
    return render(request, 'dashboard/logo/logo-list.html', {'logo': logo})


@login_required
@daseboard_required
def logo_add(request):
    if request.method == 'POST':
        form = WebsiteInformationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Website information successfully added!')
            return redirect('logo-list')
    else:
        form = WebsiteInformationForm()
    return render(request, 'dashboard/logo/logo-add.html', {'form': form})


@login_required
@daseboard_required
def logo_update(request, pk):
    logo = WebsiteInformation.objects.get(pk=pk)
    form = WebsiteInformationForm(request.POST, request.FILES, instance=logo)
    if request.method == 'POST':
        form = WebsiteInformationForm(request.POST, request.FILES, instance=logo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Website information successfully updated!')
            return redirect('logo-list')
    else:
        form = WebsiteInformationForm(instance=logo)
    context = {
        'logo': logo,
        'form': form,
    }
    return render(request, 'dashboard/logo/logo-add.html', context)


@login_required
@daseboard_required
def logo_delete(request, pk):
    logo = WebsiteInformation.objects.get(pk=pk)
    logo.delete()
    messages.success(request, 'Website information successfully deleted!')
    return redirect('logo-list')


# Coupon
@login_required
@daseboard_required
def coupon_list(request):
    coupons = Coupon.objects.all()
    now = timezone.now
    return render(request, 'dashboard/coupon/coupon-list.html', {'coupons': coupons, 'now':now})


@login_required
@daseboard_required
def coupon_add(request):
    if request.method == 'POST':
        form = CouponProductAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'Coupon successfully added!')
            return redirect('coupon-list')
    else:
        form = CouponProductAddForm()
    return render(request, 'dashboard/coupon/coupon-add.html', {'form': form})


@login_required
@daseboard_required
def coupon_update(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    form = CouponProductAddForm(request.POST, request.FILES, instance=coupon)
    if request.method == 'POST':
        form = CouponProductAddForm(request.POST, request.FILES, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon successfully updated!')
            return redirect('coupon-list')
    else:
        form = CouponProductAddForm(instance=coupon)
    return render(request, 'dashboard/coupon/coupon-add.html', {'form': form})


@login_required
@daseboard_required
def coupon_add_2(request):
    if request.method == 'POST':
        form = CouponUserAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, 'Coupon successfully added!')
            return redirect('coupon-list')
    else:
        form = CouponUserAddForm()
    return render(request, 'dashboard/coupon/coupon-add.html', {'form': form})


@login_required
@daseboard_required
def coupon_update_2(request, pk):
    coupon = get_object_or_404(Coupon, pk=pk)
    form = CouponUserAddForm(request.POST, request.FILES, instance=coupon)
    if request.method == 'POST':
        form = CouponUserAddForm(request.POST, request.FILES, instance=coupon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon successfully updated!')
            return redirect('coupon-list')
    else:
        form = CouponUserAddForm(instance=coupon)
    return render(request, 'dashboard/coupon/coupon-add.html', {'form': form})


@login_required
@daseboard_required
def coupon_delete(request, pk):
    coupon = Coupon.objects.get(pk=pk)
    coupon.delete()
    messages.success(request, 'Coupon successfully deleted!')
    return redirect('coupon-list')


#free_delivery
@login_required
@daseboard_required
def free_delivery_data(request): # use
    query_data = request.GET.get('query_data', 'True')
    search_data = request.GET.get('search_data', '')
    if query_data == 'True':
        query = Product.objects.filter(Q(product_name__icontains=search_data) | Q(id__icontains=search_data)
            ,is_verified=True, free_delivery=True).order_by('-id')
    else:
        query = Product.objects.filter(Q(product_name__icontains=search_data) | Q(id__icontains=search_data)
            ,is_verified=True, free_delivery=False).order_by('-id')
    
    return render(request, 'dashboard/product_free_delivery/free-delivery-data.html', {'query': query, 'query_data':query_data, 'search_data':search_data})


@login_required
@daseboard_required
def selected_free_delivery_verify(request): # use
    if request.method == 'POST':
        selected_free_deliverys = request.POST.getlist('selected_brands')
        for free_delivery in selected_free_deliverys:
            free_delivery = get_object_or_404(Product, id=free_delivery)
            free_delivery.free_delivery = True
            free_delivery.save()
        messages.success(request, 'Selected free deliverys have been added.')
    return redirect('free_delivery_data')


@login_required
@daseboard_required
def selected_free_delivery_remove(request): # use
    if request.method == 'POST':
        selected_free_deliverys = request.POST.getlist('selected_brands')
        for free_delivery in selected_free_deliverys:
            free_delivery = get_object_or_404(Product, id=free_delivery)
            free_delivery.free_delivery = False
            free_delivery.save()
        messages.success(request, 'Selected free deliverys have been removed.')
    return redirect('free_delivery_data')


@login_required
@daseboard_required
def free_delivery_remove(request, slug): # use
    free_delivery = Product.objects.get(slug=slug)
    free_delivery.free_delivery = False
    free_delivery.save()
    messages.success(request, 'Free Delivery successfully removed.')
    return redirect('free_delivery_data')


#Flashsale
@login_required
@daseboard_required
def flashsale_list(request):
    flashsale = FlashSale.objects.all()
    return render(request, 'dashboard/flashsale/flashsale-list.html', {'flashsale': flashsale})



@login_required
@daseboard_required
def flashsale_add(request):
    if request.method == 'POST':
        form = FlashsaleForm(request.POST)
        flashformset = FlashSaleProductFormset(request.POST, request.FILES, prefix='flashsale_products')

        if form.is_valid() and flashformset.is_valid():
            flash_sale_instance = form.save(commit=False)
            flash_sale_instance.save()
            for product_form in flashformset:
                product_instance = product_form.save(commit=False)
                product_instance.flash_sale = flash_sale_instance
                product_instance.save()
            return redirect('flashsale-list')  
    else:
        form = FlashsaleForm()
        flashformset = FlashSaleProductFormset(prefix='flashsale_products')

    return render(request, 'dashboard/flashsale/flashsale-add.html', {'form': form,'flashformset': flashformset})


@login_required
@daseboard_required
def flashsale_update(request, pk):
    flash_sale_instance = get_object_or_404(FlashSale, pk=pk)

    if request.method == 'POST':
        form = FlashsaleForm(request.POST, instance=flash_sale_instance)
        flashformset = FlashSaleProductFormset(request.POST, request.FILES, instance=flash_sale_instance, prefix='flashsale_products')
        if form.is_valid() and flashformset.is_valid():
            flash_sale_instance = form.save(commit=False)
            flash_sale_instance.save()
            for product_form in flashformset:
                product_instance = product_form.save(commit=False)
                product_instance.flash_sale = flash_sale_instance
                product_instance.save()
            return redirect('flashsale-list')  
    else:
        form = FlashsaleForm(instance=flash_sale_instance)
        flashformset = FlashSaleProductFormset(instance=flash_sale_instance, prefix='flashsale_products')

    return render(request, 'dashboard/flashsale/flashsale-add.html', {
        'form': form,
        'flashformset': flashformset,
        'flash_sale_instance': flash_sale_instance
    })


@login_required
@daseboard_required
def flashsale_delete(request, product_id):
    flashsale_product = get_object_or_404(FlashSale, id=product_id)
    flashsale_product.delete()
    return redirect('flashsale-list')

@login_required
@daseboard_required
def flashsale_product_delete(request, product_id):
    flashsale_product = get_object_or_404(FlashSaleProduct, id=product_id)
    flashsale_product.delete()
    return JsonResponse({'success': True}, status=200)


@login_required
@daseboard_required
def product_vartions(request, pk):
    product = get_object_or_404(Product, pk=pk)
    varitions = Variation.objects.filter(product=product)
    return render(request, 'dashboard/flashsale/variation.html', {'varitions': varitions})



# Campaign
@login_required
@daseboard_required
def campaign_category_list(request):
    campaign_category = Campaign.objects.all()
    return render(request, 'dashboard/campaign-category/campaign-category-list.html', {'campaign_category': campaign_category})


@login_required
@daseboard_required
def campaign_category_add(request):
    if request.method == 'POST':
        form = CampaignCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign category successfully added!')
            return redirect('campaign-category-list')
    else:
        form = CampaignCategoryForm()
    return render(request, 'dashboard/campaign-category/campaign-category-add.html', {'form': form})


@login_required
@daseboard_required
def campaign_category_update(request, pk):
    campaign_category = get_object_or_404(Campaign, pk=pk)
    form = CampaignCategoryForm(request.POST, request.FILES, instance=campaign_category)
    if request.method == 'POST':
        form = CampaignCategoryForm(request.POST, request.FILES, instance=campaign_category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign category successfully updated!')
            return redirect('campaign-category-list')
    else:
        form = CampaignCategoryForm(instance=campaign_category)
    return render(request, 'dashboard/campaign-category/campaign-category-add.html', {'form': form})


@login_required
@daseboard_required
def campaign_category_delete(request, pk):
    campaign_category = Campaign.objects.get(pk=pk)
    campaign_category.delete()
    messages.success(request, 'Campaign category successfully deleted!')
    return redirect('campaign-category-list')


#Campaign product
@login_required
@daseboard_required
def campaign_product_list(request):
    campaign_product = CampaignProduct.objects.all()
    return render(request, 'dashboard/campaign-product/campaign-product-list.html', {'campaign_product': campaign_product})


@login_required
@daseboard_required
def campaign_product_add(request):
    if request.method == 'POST':
        form = CampaignProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign product successfully added!')
            return redirect('campaign-product-list')
    else:
        form = CampaignProductForm()
    return render(request, 'dashboard/campaign-product/campaign-product-add.html', {'form': form})


@login_required
@daseboard_required
def campaign_product_update(request, pk):
    campaign_product = get_object_or_404(CampaignProduct, pk=pk)
    form = CampaignProductForm(request.POST, instance=campaign_product)
    if request.method == 'POST':
        form = CampaignProductForm(request.POST, instance=campaign_product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Campaign product successfully updated!')
            return redirect('campaign-product-list')
    else:
        form = CampaignProductForm(instance=campaign_product)
    return render(request, 'dashboard/campaign-product/campaign-product-add.html', {'form': form})


@login_required
@daseboard_required
def campaign_product_delete(request, pk):
    campaign_product = CampaignProduct.objects.get(pk=pk)
    campaign_product.delete()
    messages.success(request, 'Campaign product successfully deleted!')
    return redirect('campaign-product-list')


#Deal of the day
@login_required
@daseboard_required
def deal_of_the_day_product_data(request): # use
    obj = DealOfTheDayProduct.objects.all().order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    added = False

    latest_flash_sale = FlashSale.objects.filter(is_active=True).last()
    flashsale_product_ids = ''
    if latest_flash_sale:
        flashsale_product_ids = FlashSaleProduct.objects.filter(flash_sale=latest_flash_sale) \
            .values_list('product__id', flat=True) \
            .distinct()
        
    deal_list = list(DealOfTheDayProduct.objects.all().values_list('product__id', flat=True).distinct())
    combined_list = list(flashsale_product_ids) + deal_list
    sorted_list = sorted(set(combined_list))
    products = Product.objects.filter(is_verified=True).exclude(id__in=sorted_list)
    without_falshsale_products = Product.objects.filter(is_verified=True).exclude(id__in=flashsale_product_ids)
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            objects = DealOfTheDayProduct.objects.get(id=obj_id)
        else:
            objects = None
        form = DealOfTheDayProductForm(request.POST, request.FILES, instance=objects)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your banner has been successfully updated!')
            else:
                added = True
                messages.success(request, 'Your banner has been successfully added!')
            return redirect('deal_of_the_day_product_data')
        else:
            messages.error(request, 'Data didn"t valid!')
    return render(request, 'dashboard/deal_of-the_day/deal-data.html', {'query': query, 'products': products,'without_falshsale_products': without_falshsale_products, 'added':added})


@login_required
@daseboard_required
def deal_of_the_day_product_delete(request, pk): # use
    deal_of_the_day = DealOfTheDayProduct.objects.get(pk=pk)
    deal_of_the_day.delete()
    messages.success(request, 'Deal of the day successfully deleted!')
    return redirect('deal_of_the_day_product_data')


@login_required
@daseboard_required
def deal_of_the_day_product_list(request):
    deal_of_the_day = DealOfTheDayProduct.objects.all()
    return render(request, 'dashboard/deal_of-the_day/dotd_product-list.html', {'deal_of_the_day': deal_of_the_day})

@login_required
@daseboard_required
def deal_of_the_day_product_add(request):
    if request.method == 'POST':
        form = DealOfTheDayProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deal of the day successfully added!')
            return redirect('deal_of_the_day_product-list')
    else:
        form = DealOfTheDayProductForm()
        flashsale_list = list(FlashSaleProduct.objects.filter(flash_sale__is_active=True).values_list('product__id', flat=True).distinct())
        deal_list = list(DealOfTheDayProduct.objects.all().values_list('product__id', flat=True).distinct())
        combined_list = flashsale_list + deal_list
        sorted_list = sorted(set(combined_list))
        products = Product.objects.filter(is_verified=True).exclude(id__in=sorted_list)
    return render(request, 'dashboard/deal_of-the_day/dotd_product-add.html', {'form': form, 'products':products})


@login_required
@daseboard_required
def deal_of_the_day_product_update(request, pk):
    deal_of_the_day = get_object_or_404(DealOfTheDayProduct, pk=pk)
    form = DealOfTheDayProductForm(request.POST, instance=deal_of_the_day)
    if request.method == 'POST':
        form = DealOfTheDayProductForm(request.POST, instance=deal_of_the_day)
        if form.is_valid():
            form.save()
            messages.success(request, 'Deal of the day successfully updated!')
            return redirect('deal_of_the_day_product-list')
    else:
        form = DealOfTheDayProductForm(instance=deal_of_the_day)
        flashsale_list = list(FlashSaleProduct.objects.filter(flash_sale__is_active=True).values_list('product__id', flat=True).distinct())
        deal_list = list(DealOfTheDayProduct.objects.all().values_list('product__id', flat=True).distinct())
        combined_list = flashsale_list + deal_list
        sorted_list = sorted(set(combined_list))
        products = Product.objects.filter(is_verified=True).exclude(id__in=sorted_list)
    return render(request, 'dashboard/deal_of-the_day/dotd_product-add.html', {'form': form, 'products':products})



#Review
@login_required
@daseboard_required
def rating_list(request):
    rating = ProductReview.objects.all()
    return render(request, 'dashboard/rating/rating-list.html', {'rating': rating})

@login_required
@daseboard_required
def rating_add(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product review successfully added!')
            return redirect('rating-list')
    else:
        form = ReviewForm()
    return render(request, 'dashboard/rating/rating-add.html', {'form': form})

@login_required
@daseboard_required
def rating_update(request, pk):
    rating = get_object_or_404(ProductReview, pk=pk)
    form = ReviewForm(request.POST, instance=rating)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=rating)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product review successfully updated!')
            return redirect('rating-list')
    else:
        form = ReviewForm(instance=rating)
    return render(request, 'dashboard/rating/rating-add.html', {'form': form})

@login_required
@daseboard_required
def rating_delete(request, pk):
    rating = ProductReview.objects.get(pk=pk)
    rating.delete()
    messages.success(request, 'Product review successfully deleted!')
    return redirect('rating-list')

# Contact
@login_required
@daseboard_required
def contact_data_list(request):
    contact_datas = ConductData.objects.all()
    return render(request, 'dashboard/contact/contact-list.html', {'contact_datas': contact_datas})


@login_required
@daseboard_required
def contact_data_detail(request, pk):
    contact_datas = ConductData.objects.get(pk=pk)
    contact_datas.view_status = True
    contact_datas.save()
    return render(request, 'dashboard/contact/contact-detail.html', {'contact_datas': contact_datas})

@login_required
@daseboard_required
def contact_add(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact successfully added!')
            return redirect('contact-list')
    else:
        form = ContactForm()
    return render(request, 'dashboard/contact/contact-add.html', {'form': form})

@login_required
@daseboard_required
def contact_update(request, pk):
    contact = get_object_or_404(ConductData, pk=pk)
    form = ContactForm(request.POST, instance=contact)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact successfully updated!')
            return redirect('contact-list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'dashboard/contact/contact-add.html', {'form': form})

@login_required
@daseboard_required
def contact_delete(request, pk):
    contact = ConductData.objects.get(pk=pk)
    contact.delete()
    messages.success(request, 'Contact successfully deleted!')
    return redirect('contact-list')


#Privacy Policy
@login_required
@daseboard_required
def privacy_policy_list(request):
    privacy_policy = PrivacyPolicy.objects.all()
    return render(request, 'dashboard/privacy-policy/privacy_policy-list.html', {'privacy_policy': privacy_policy})


@login_required
@daseboard_required
def privacy_policy_add(request):
    if request.method == 'POST':
        form = PrivacyPolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy policy successfully added!')
            return redirect('privacy_policy-list')
    else:
        form = PrivacyPolicyForm()
    return render(request, 'dashboard/privacy-policy/privacy_policy-add.html', {'form': form})


@login_required
@daseboard_required
def privacy_policy_update(request, pk):
    privacy_policy = get_object_or_404(PrivacyPolicy, pk=pk)
    form = PrivacyPolicyForm(request.POST, instance=privacy_policy)
    if request.method == 'POST':
        form = PrivacyPolicyForm(request.POST, instance=privacy_policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Privacy policy successfully updated!')
            return redirect('privacy_policy-list')
    else:
        form = PrivacyPolicyForm(instance=privacy_policy)

    return render(request, 'dashboard/privacy-policy/privacy_policy-add.html', {'form': form})


def privacy_policy_delete(request, pk):
    privacy_policy = PrivacyPolicy.objects.get(pk=pk)
    privacy_policy.delete()
    messages.success(request, 'Privacy policy successfully deleted!')
    return redirect('privacy_policy-list')


#Terms Conditions
@login_required
@daseboard_required
def terms_condition_list(request):
    terms_condition = TermsAndConditions.objects.all()
    return render(request, 'dashboard/terms-condition/terms_condition-list.html', {'terms_condition': terms_condition})


@login_required
@daseboard_required
def terms_condition_add(request):
    if request.method == 'POST':
        form = TermsAndConditionsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Terms conditions successfully added!')
            return redirect('terms_conditions_list')
    else:
        form = TermsAndConditionsForm()
    return render(request, 'dashboard/terms-condition/terms_condition-add.html', {'form': form})


@login_required
@daseboard_required
def terms_condition_update(request, pk):
    terms_condition = get_object_or_404(TermsAndConditions, pk=pk)
    form = TermsAndConditionsForm(request.POST, instance=terms_condition)
    if request.method == 'POST':
        form = TermsAndConditionsForm(request.POST, instance=terms_condition)
        if form.is_valid():
            form.save()
            messages.success(request, 'Terms conditions successfully updated!')
            return redirect('terms_conditions_list')
    else:
        form = TermsAndConditionsForm(instance=terms_condition)
    return render(request, 'dashboard/terms-condition/terms_condition-add.html', {'form': form})


@login_required
@daseboard_required
def terms_condition_delete(request, pk):
    terms_condition = TermsAndConditions.objects.get(pk=pk)
    terms_condition.delete()
    messages.success(request, 'Terms conditions successfully deleted!')
    return redirect('terms_conditions_list')


# mission
@login_required
@daseboard_required
def mission_list(request):
    mission = Mission.objects.all()
    return render(request, 'dashboard/mission/mission-list.html', {'mission': mission})


@login_required
@daseboard_required
def mission_add(request):
    if request.method == 'POST':
        form = MissionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mission successfully added!')
            return redirect('mission-list')
    else:
        form = MissionForm()
    return render(request, 'dashboard/mission/mission-add.html', {'form': form})


@login_required
@daseboard_required
def mission_update(request, pk):
    mission = get_object_or_404(Mission, pk=pk)
    form = MissionForm(request.POST, instance=mission)
    if request.method == 'POST':
        form = MissionForm(request.POST, instance=mission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mission successfully updated!')
            return redirect('mission-list')
    else:
        form = MissionForm(instance=mission)
    return render(request, 'dashboard/mission/mission-add.html', {'form': form})


@login_required
@daseboard_required
def mission_delete(request, pk):
    mission = Mission.objects.get(pk=pk)
    mission.delete()
    messages.success(request, 'Vision successfully deleted!')
    return redirect('mission-list')


# vision
@login_required
@daseboard_required
def vision_list(request):
    vision = Vision.objects.all()
    return render(request, 'dashboard/vision/vision-list.html', {'vision': vision})


@login_required
@daseboard_required
def vision_add(request):
    if request.method == 'POST':
        form = VisionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vision successfully added!')
            return redirect('vision-list')
    else:
        form = VisionForm()
    return render(request, 'dashboard/vision/vision-add.html', {'form': form})


@login_required
@daseboard_required
def vision_update(request, pk):
    vision = get_object_or_404(Vision, pk=pk)
    form = VisionForm(request.POST, instance=vision)
    if request.method == 'POST':
        form = VisionForm(request.POST, instance=vision)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vision successfully updated!')
            return redirect('vision-list')
    else:
        form = VisionForm(instance=vision)
    
    return render(request, 'dashboard/vision/vision-add.html', {'form': form})


@login_required
@daseboard_required
def vision_delete(request, pk):
    vision = Vision.objects.get(pk=pk)
    vision.delete()
    messages.success(request, 'Vision successfully deleted!')
    return redirect('vision-list')


#Return Policy
@login_required
@daseboard_required
def returns_policy_list(request):
    returns_policy = Returns_Policy.objects.all()
    return render(request, 'dashboard/returns_policy/returns_policy-list.html', {'returns_policy': returns_policy})


@login_required
@daseboard_required
def returns_policy_add(request):
    if request.method == 'POST':
        form = Returns_PolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return policy successfully added!')
            return redirect('returns_policy-list')
    else:
        form = Returns_PolicyForm()
    return render(request, 'dashboard/returns_policy/returns_policy-add.html', {'form': form})


@login_required
@daseboard_required
def returns_policy_update(request, pk):
    returns_policy = get_object_or_404(Returns_Policy, pk=pk)
    form = Returns_PolicyForm(request.POST, instance=returns_policy)
    if request.method == 'POST':
        form = Returns_PolicyForm(request.POST, instance=returns_policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return policy successfully updated!')
            return redirect('returns_policy-list')
    else:
        form = Returns_PolicyForm(instance=returns_policy)
    
    return render(request, 'dashboard/returns_policy/returns_policy-add.html', {'form': form})


@login_required
@daseboard_required
def returns_policy_delete(request, pk):
    returns_policy = Returns_Policy.objects.get(pk=pk)
    returns_policy.delete()
    messages.success(request, 'Return policy successfully deleted!')
    return redirect('returns_policy-list')


#Return Product
@login_required
@daseboard_required
def returns_product_list(request):
    statuse = ['Processing', 'Pending', 'On the way']
    return_products = ReturnProduct.objects.filter(status__in=statuse)
    owned_products = Product.objects.filter(user=request.user)
    vendor_return_products = ReturnProduct.objects.filter(items__item__in=owned_products, status__in=statuse)
    
    return render(request, 'dashboard/returns_product/returns_product-list.html', {'return_products': return_products, 'vendor_return_products': vendor_return_products})

@login_required
@daseboard_required
def returns_product_details(request,pk):
    statuse = ['Processing', 'Pending', 'On the way']
    return_products = ReturnProduct.objects.filter(status__in=statuse, pk=pk)
    owned_products = Product.objects.filter(user=request.user)
    vendor_return_products = ReturnProduct.objects.filter(items__item__in=owned_products, status__in=statuse)
    
    return render(request, 'dashboard/returns_product/return_product-detail.html', {'return_products': return_products, 'vendor_return_products': vendor_return_products})


@login_required
@daseboard_required
def returns_product_complete(request):
    return_products = ReturnProduct.objects.filter(status='Complete')
    owned_products = Product.objects.filter(user=request.user)
    vendor_return_products = ReturnProduct.objects.filter(items__item__in=owned_products, status='Complete')
    
    return render(request, 'dashboard/returns_product/returns_product-complete.html', {'return_products': return_products, 'vendor_return_products': vendor_return_products})

@login_required
@daseboard_required
def returns_product_cancel(request):
    return_products = ReturnProduct.objects.filter(status='Cancel')
    owned_products = Product.objects.filter(user=request.user)
    vendor_return_products = ReturnProduct.objects.filter(items__item__in=owned_products, status='Cancel')
    
    return render(request, 'dashboard/returns_product/returns_product-cancel.html', {'return_products': return_products, 'vendor_return_products': vendor_return_products})




@login_required
@daseboard_required
def returns_product_add(request):
    if request.method == 'POST':
        form = DashReturnProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return policy successfully added!')
            return redirect('returns_product-list')
    else:
        form = DashReturnProductForm()
    return render(request, 'dashboard/returns_product/returns_product-add.html', {'form': form})


@login_required
@daseboard_required
def returns_product_update(request, pk):
    returns_product = get_object_or_404(ReturnProduct, pk=pk)
    form = DashReturnProductForm(request.POST, instance=returns_product)
    if request.method == 'POST':
        form = DashReturnProductForm(request.POST, instance=returns_product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Return product successfully updated!')
            return redirect('returns_product-list')
    else:
        form = DashReturnProductForm(instance=returns_product)
    
    return render(request, 'dashboard/returns_product/returns_product-add.html', {'form': form})


@login_required
@daseboard_required
def returns_product_delete(request, pk):
    returns_product = ReturnProduct.objects.get(pk=pk)
    returns_product.delete()
    messages.success(request, 'Return policy successfully deleted!')
    return redirect('returns_product-list')




# shipping_delivery
@login_required
@daseboard_required
def shipping_delivery_list(request):
    shipping_delivery = ShippingAndDelivery.objects.all()
    return render(request, 'dashboard/shipping_delivery/shipping_delivery-list.html', {'shipping_delivery': shipping_delivery})


@login_required
@daseboard_required
def shipping_delivery_add(request):
    if request.method == 'POST':
        form = ShippingAndDeliveryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipping delivery successfully added!')
            return redirect('shipping_delivery-list')
    else:
        form = ShippingAndDeliveryForm()
    return render(request, 'dashboard/shipping_delivery/shipping_delivery-add.html', {'form': form})


@login_required
@daseboard_required
def shipping_delivery_update(request, pk):
    shipping_delivery = get_object_or_404(ShippingAndDelivery, pk=pk)
    form = ShippingAndDeliveryForm(request.POST, instance=shipping_delivery)
    if request.method == 'POST':
        form = ShippingAndDeliveryForm(
            request.POST, instance=shipping_delivery)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shipping delivery successfully updated!')
            return redirect('shipping_delivery-list')
    else:
        form = ShippingAndDeliveryForm(instance=shipping_delivery)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/shipping_delivery/shipping_delivery-add.html', context)


@login_required
@daseboard_required
def shipping_delivery_delete(request, pk):
    shipping_delivery = ShippingAndDelivery.objects.get(pk=pk)
    shipping_delivery.delete()
    messages.success(request, 'Shipping delivery successfully deleted!')
    return redirect('shipping_delivery-list')


#About Us
@login_required
@daseboard_required
def aboutus_list(request):
    aboutus = AboutUs.objects.all()
    return render(request, 'dashboard/aboutus/aboutus-list.html', {'aboutus': aboutus})


@login_required
@daseboard_required
def aboutus_add(request):
    if request.method == 'POST':
        form = AboutUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'About us successfully added!')
            return redirect('aboutus-list')
    else:
        form = AboutUsForm()
    return render(request, 'dashboard/aboutus/aboutus-add.html', {'form': form})


@login_required
@daseboard_required
def aboutus_update(request, pk):
    aboutus = get_object_or_404(AboutUs, pk=pk)
    form = AboutUsForm(request.POST, instance=aboutus)
    if request.method == 'POST':
        form = AboutUsForm(request.POST, instance=aboutus)
        if form.is_valid():
            form.save()
            messages.success(request, 'About us successfully updated!')
            return redirect('aboutus-list')
    else:
        form = AboutUsForm(instance=aboutus)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/returns_policy/aboutus-add.html', context)


@login_required
@daseboard_required
def aboutus_delete(request, pk):
    aboutus = AboutUs.objects.get(pk=pk)
    aboutus.delete()
    messages.success(request, 'About us successfully deleted!')
    return redirect('aboutus-list')



@login_required
@daseboard_required
def unrole_order(request):
    users = User.objects.filter(is_staff=True, is_superuser=False)
    roled_type = request.GET.get('roled_type', 'False')
    roled_type = roled_type == 'True'
    staff_id = request.GET.get('staff_id', None)
    if request.user.is_superuser:
        if roled_type:
            if staff_id:
                pending_orders = Order.objects.filter(ordered=True, staff_role=staff_id).order_by('-id')
            else:
                p_id = list(Order.objects.filter(ordered=True, staff_role=None).values_list('id', flat=True).distinct())
                pending_orders = Order.objects.filter(ordered=True).exclude(id__in=p_id).order_by('-id')
        else:
            pending_orders = Order.objects.filter(ordered=True, staff_role=None).order_by('-id')
    else:
        pending_orders = Order.objects.none()
    
    if request.method == 'POST':
        user_id = request.POST['user_id']
        order_ids = request.POST.getlist('order_ids')
        user = User.objects.get(id=user_id)
        orders = Order.objects.filter(id__in=order_ids)
        for order in orders:
            order.staff_role = user
            order.staff_roled_date = timezone.now()
            order.save()
        messages.success(request, f'Roled these orders: {order_ids} to this User: {user}')
        return redirect('unrole_order')
    return render(request, 'dashboard/order/unrole-order-list.html', {
        'pending_orders': pending_orders, 
        'users': users, 
        'roled_type': roled_type,
        'staff_id':staff_id
    })


@login_required
@daseboard_required
def order_list(request):
    search = request.GET.get('search', '')
    order_status = request.GET.get('order_status', '')
    parcel_type = request.GET.get('parcel_type', 'Pending')
    time_period = request.GET.get('time_period', '')
    
    # Base query for all orders
    query = Order.objects.filter(ordered=True).order_by('-ordered_date')

    # Filter orders based on user roles
    if request.user.is_superuser:
        unroled_order = list(query.filter(staff_role=None).values_list('id', flat=True).distinct())
        query = query.exclude(id__in=unroled_order)
    elif request.user.is_staff:
        query = query.filter(staff_role=request.user)
    elif request.user.is_vendor:
        query = query.filter(items__item__user=request.user).distinct()
    else:
        query = Order.objects.none()

    if search:
        query = query.filter(Q(id__icontains=search) | Q(shipping_address__full_name__icontains=search))

    if order_status:
        query = query.filter(items__pathao_status=order_status)

    if parcel_type == 'Pending':
        query = query.filter(Q(merchant_order_id__isnull=True) | Q(merchant_order_id=""))
    elif parcel_type == 'Parcel':
        query = query.exclude(Q(merchant_order_id__isnull=True) | Q(merchant_order_id=""))

    if time_period:
        now = datetime.now()
        if time_period == 'today':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif time_period == 'yesterday':
            start = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
            end = start + timedelta(days=1)
        elif time_period == 'thisweek':
            start = now - timedelta(days=now.weekday())
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif time_period == 'lastweek':
            start = now - timedelta(days=now.weekday() + 7)
            start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif time_period == 'thismonth':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=now.day)
        elif time_period == 'lastmonth':
            start = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
            end = start + timedelta(days=31)
        elif time_period == 'thisyear':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=365)
        elif time_period == 'lastyear':
            start = now.replace(year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=365)
        
        query = query.filter(ordered_date__range=(start, end))

    # print('query', query)
    if request.method == "POST":
        order_id = request.POST['order_id']
        remark_data = request.POST['remark_data']
        order = Order.objects.get(id=order_id)
        order.order_remark = remark_data
        order.save()
        messages.success(request, 'Remarked!!')
        return redirect('order_list')
    return render(request, 'dashboard/order/order-list.html', {'query': query})



@login_required
@daseboard_required
def pending_order(request):
    ORDER_STATUS = ['Pending','Processing','On the way']
    if request.user.is_superuser:
        unroled_order = list(Order.objects.filter(ordered=True, staff_role=None, order_status__in=ORDER_STATUS).values_list('id',flat=True).distinct())
        pending_orders = Order.objects.filter(ordered=True, order_status__in=ORDER_STATUS).exclude(id__in=unroled_order).order_by('-id')
    elif request.user.is_staff:
        pending_orders = Order.objects.filter(ordered=True, staff_role=request.user, order_status__in=ORDER_STATUS).order_by('-id')   
    elif request.user.is_vendor:
        pending_orders = Order.objects.filter(
            ordered=True, 
            order_status__in=ORDER_STATUS,
            items__item__user=request.user
        ).distinct().order_by('-id')
    else:
        pending_orders = Order.objects.none()

    if request.method == "POST":
        order_id = request.POST['order_id']
        remark_data = request.POST['remark_data']
        order = Order.objects.get(id=order_id)
        order.order_remark = remark_data
        order.save()
        messages.success(request, 'Remarked!!')
        return redirect('pending_order')
    # print('pending_orders', pending_orders)
    return render(request, 'dashboard/order/pending-order-list.html', {'pending_orders': pending_orders})


@login_required
@daseboard_required
def complete_order(request):
    if request.user.is_superuser:
        unroled_order = list(Order.objects.filter(ordered=True, staff_role=None, order_status='Complete').values_list('id',flat=True).distinct())
        complete_orders = Order.objects.filter(ordered=True, order_status='Complete').exclude(id__in=unroled_order).order_by('-id')
    elif request.user.is_staff:
        complete_orders = Order.objects.filter(ordered=True, staff_role=request.user, order_status='Complete').order_by('-id')
    elif request.user.is_vendor:
        complete_orders = Order.objects.filter(
            ordered=True, 
            order_status='Complete', 
            items__item__user=request.user
        ).distinct().order_by('-id')
    else:
        complete_orders = Order.objects.none()
    return render(request, 'dashboard/order/complete-order-list.html', {'complete_orders': complete_orders})


@login_required
@daseboard_required
def return_order(request):
    if request.user.is_superuser:
        unroled_order = list(Order.objects.filter(ordered=True, staff_role=None, order_status='Return').values_list('id',flat=True).distinct())
        complete_orders = Order.objects.filter(ordered=True, order_status='Return').exclude(id__in=unroled_order).order_by('-id')
    elif request.user.is_staff:
        complete_orders = Order.objects.filter(ordered=True, staff_role=request.user, order_status='Return').order_by('-id')
    elif request.user.is_vendor:
        complete_orders = Order.objects.filter(
            ordered=True, 
            order_status='Return', 
            items__item__user=request.user
        ).distinct().order_by('-id')
    else:
        complete_orders = Order.objects.none()
    return render(request, 'dashboard/order/complete-order-list.html', {'complete_orders': complete_orders})

@login_required
@daseboard_required
def cancel_order(request):
    if request.user.is_superuser:
        unroled_order = list(Order.objects.filter(ordered=True, staff_role=None, order_status='Cancel').values_list('id',flat=True).distinct())
        complete_orders = Order.objects.filter(ordered=True, order_status='Cancel').exclude(id__in=unroled_order).order_by('-id')
    elif request.user.is_staff:
        complete_orders = Order.objects.filter(ordered=True, staff_role=request.user, order_status='Cancel').order_by('-id')
    elif request.user.is_vendor:
        complete_orders = Order.objects.filter(
            ordered=True, 
            order_status='Cancel', 
            items__item__user=request.user
        ).distinct().order_by('-id')
    else:
        complete_orders = Order.objects.none()
    return render(request, 'dashboard/order/complete-order-list.html', {'complete_orders': complete_orders})


@login_required
@daseboard_required
def vendor_order(request):
    user = request.user
    order_vendor = Order.objects.filter(user=user, ordered=True).order_by('-id')
    order = Order.objects.filter(ordered=True).order_by('-id')
    context = {
        'order_vendor': order_vendor,
        'order': order,
    }
    return render(request, 'dashboard/order/order-list.html', context)



@login_required
@daseboard_required
def order_detail(request, pk):
    order = Order.objects.get(pk=pk)
    order.order_read_status = True
    order.save()
    if order.merchant_order_id:
        order_items = OrderItem.objects.filter(order=order)
        order_items_ids = list(order_items.values_list('id',flat=True).distinct())
        fetch_consignment(order_items_ids)

    if request.user.is_superuser or request.user.is_staff:
        order_items = OrderItem.objects.filter(order=order)
    elif request.user.is_vendor:
        order_items = OrderItem.objects.filter(order=order, item__user=request.user)
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'dashboard/order/order-detail.html', context)

@login_required
@daseboard_required
def order_status_update(request, pk):
    order = Order.objects.get(pk=pk)
    order_status = request.POST.get('order_status')
    order.order_status = order_status
    order.save()
    messages.success(request, "Status updated!!")
    return redirect('order_detail', pk=order.id)


# @login_required
# @daseboard_required
# def OrderDetails(request, pk):
#     user = request.user
#     order = get_object_or_404(Order, user=user, pk=pk)
#     order.order_read_status = True
#     order.save()

#     order_items_vendor = OrderItem.objects.filter(order=order,item__user=request.user)
#     context = {
#         'order': order,
#         'order_items_vendor': order_items_vendor,
#     }
#     return render(request, 'dashboard/order/order-details.html', context)


@login_required
@daseboard_required
def order_update(request, pk):
    order = get_object_or_404(Order, pk=pk)
    shipping_addresses = ShipingAddress.objects.all()  # Fetch all shipping addresses
    coupons = Coupon.objects.all()  # Fetch all coupons
    users = get_user_model().objects.all()  # Fetch all users
    items = OrderItem.objects.all()  # Fetch all order items

    if request.method == 'POST':
        order.user_id = request.POST.get('user')
        order.items.set(request.POST.getlist('items'))
        order.order_status = request.POST.get('order_status')
        order.total_order_amount = request.POST.get('total_order_amount')
        order.paid_amount = request.POST.get('paid_amount')
        order.due_amount = request.POST.get('due_amount')
        order.orderId = request.POST.get('orderId')
        order.paymentId = request.POST.get('paymentId')
        order.payment_option = request.POST.get('payment_option')
        order.order_read_status = request.POST.get('order_read_status') == 'on'
        # order.redx_percel_traking_number = request.POST.get('redx_percel_traking_number')
        # order.others_transport_trakink_url = request.POST.get('others_transport_trakink_url')
        order.shipping_address_id = request.POST.get('shipping_address')
        order.coupon_id = request.POST.get('coupon')
        order.save()
        messages.success(request, 'Order successfully updated!')
        return redirect('order_detail', pk=order.pk)
    
    context = {
        'order': order,
        'shipping_addresses': shipping_addresses,  # Pass the addresses to the template
        'coupons': coupons,  # Pass the coupons to the template
        'users': users,  # Pass the users to the template
        'items': items,  # Pass the items to the template
    }
    return render(request, 'dashboard/order/order-update.html', context)


@login_required
@daseboard_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.delete()
    messages.success(request, 'Order successfully deleted!')
    return redirect('order_list')


@login_required
@daseboard_required
def shipping_address_update(request, pk):
    order = Order.objects.get(pk=pk)
    shipping_address = ShipingAddress.objects.get(order=order)
    form = OrderShippingAddressUpdateForm(
        request.POST, request.FILES, instance=shipping_address)

    if request.method == 'POST':
        form = OrderShippingAddressUpdateForm(
            request.POST, request.FILES, instance=shipping_address)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Shipping address successfully updated!')
            return redirect('order_list')
    else:
        form = OrderShippingAddressUpdateForm(instance=shipping_address)
    context = {
        'order': order,
        'form': form,
    }
    return render(request, 'dashboard/order/shipping-address-update.html', context)

# User
@login_required
@daseboard_required
def superuser_list(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request, 'dashboard/user/superuser-list.html', {'superusers': superusers})


@login_required
@daseboard_required
def customer_list(request):
    user_coupon_list = Coupon.objects.filter(is_verified=True, product=None)
    sort_by = request.GET.get('sort_by', 'max_order')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M')
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M')
    # Base queryset
    customers = User.objects.filter(is_customer=True, is_superuser=False, is_staff=False)

    # Apply sorting
    if sort_by == 'max_order':
        customers = sorted(customers, key=lambda v: v.max_order(from_date, to_date), reverse=True)
    elif sort_by == 'min_order':
        customers = sorted(customers, key=lambda v: v.max_order(from_date, to_date))
    elif sort_by == 'max_buy':
        customers = sorted(customers, key=lambda v: v.total_buys(from_date, to_date), reverse=True)
    elif sort_by == 'min_buy':
        customers = sorted(customers, key=lambda v: v.total_buys(from_date, to_date))
    
    obj_paginator = Paginator(customers, 25)
    obj_page_number = request.GET.get("page")
    query = obj_paginator.get_page(obj_page_number)
    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        user_ids = request.POST.getlist('user_ids')
        users = User.objects.filter(id__in=user_ids)
        coupon = Coupon.objects.get(id=coupon_id)
        coupon.coupon_user.add(*users)
        coupon.save()
        messages.success(request, f'This {coupon.code} is give to these users {user_ids}')
        return redirect('customer_list')

    return render(request, 'dashboard/user/customer-list.html', {'query': query, 'sort_by':sort_by, 'from_date':from_date, 'to_date':to_date, 'user_coupon_list':user_coupon_list})



@login_required
@daseboard_required
def customer_filter_page_list(request, pk):
    user = get_object_or_404(User, pk=pk)
    form_type = request.GET.get('form_type', '')
    order_status = request.GET.get('order-status', 'Complete')
    return_product_status = request.GET.get('return-product-status', 'Complete')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    search = request.GET.get('search', '')

    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M')
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M')

    # order filter start
    if form_type == 'order':
        order_list = Order.objects.filter(
            Q(orderId__icontains=search) | Q(payment_option__icontains=search),
            user=user, order_status=order_status, ordered=True
        )
        if from_date:
            order_list = order_list.filter(ordered_date__gte=from_date)
        if to_date:
            order_list = order_list.filter(ordered_date__lte=to_date)
    else:
        order_list = Order.objects.filter(user=user, ordered=True, order_status=order_status)
    order_paginator = Paginator(order_list, 10)
    order_page_number = request.GET.get("page")
    orders = order_paginator.get_page(order_page_number)
    # order filter end
    # return product filter start
    if form_type == 'return_product':
        returnproduct_list = ReturnProduct.objects.filter(
            Q(comment__icontains=search) | Q(bank_transfer__icontains=search),
            customer=user, status=return_product_status
        )
        if from_date:
            returnproduct_list = returnproduct_list.filter(created_on__gte=from_date)
        if to_date:
            returnproduct_list = returnproduct_list.filter(created_on__lte=to_date)
    else:
        returnproduct_list = ReturnProduct.objects.filter(customer=user, status=return_product_status)
    returnproduct_paginator = Paginator(returnproduct_list, 10)
    returnproduct_page_number = request.GET.get("page")
    returnproducts = returnproduct_paginator.get_page(returnproduct_page_number)
    # return product filter end

    nav_active_item = request.GET.get("order_page") if request.GET.get("order_page") else "order" if not form_type else form_type
    context ={
        "user_id": user.id,
        'orders': orders,
        'nav_active_item':nav_active_item,
        'returnproducts':returnproducts,

        'form_type':form_type,
        'order_status':order_status,
        'return_product_status':return_product_status,
        'from_date':from_date,
        'to_date':to_date,
        'search':search,
        }
    return render(request, 'dashboard/user/customer-filter-page-list.html', context)




@login_required
@daseboard_required
def staff_list(request):
    staffs = User.objects.filter(is_staff=True, is_superuser=False, is_vendor=False, is_customer=False)
    return render(request, 'dashboard/user/staff-list.html', {'staffs': staffs})


@login_required
@daseboard_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'dashboard/user/user.html', {'user': user})



@login_required
@daseboard_required
def user_add(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  
            messages.success(request, 'User successfully added!')
            return redirect('user-update', pk=user.pk)  
    else:
        form = RegisterForm()
    return render(request, 'dashboard/user/user-add.html', {'form': form})



@login_required
@daseboard_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserForm(request.POST, instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User successfully updated!')
            return redirect('superuser_list')
    else:
        form = UserForm(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/user/user-add.html', context)

@login_required
@daseboard_required
def user_delete(request, pk):
    user = User.objects.get(pk=pk)
    user.delete()
    messages.success(request, 'User successfully deleted!')
    return redirect('superuser_list')


#vendor_payment
@login_required
@daseboard_required
def vandor_payment_pending(request):
    if request.user.is_active and request.user.is_vendor:
        vendor = VendorPayment.objects.filter(user=request.user, status__in=['Pending', 'Processing'])
    else:
        vendor = VendorPayment.objects.filter(status__in=['Pending', 'Processing'])

    if request.method == "POST":
        payment_id = request.POST["payment_id"]
        remark_id = request.POST["remark_id"]
        vendor_payement = VendorPayment.objects.get(id=payment_id)
        vendor_payement.remark = remark_id
        vendor_payement.save()
        messages.success(request, "Remark has successfully added")
        return redirect('vandor_payment_complete')
    return render(request, 'dashboard/vendor_payment/list.html', {'vendor': vendor, 'p':'p'})

@login_required
@daseboard_required
def vandor_payment_complete(request):
    if request.user.is_active and request.user.is_vendor:
        vendor = VendorPayment.objects.filter(user=request.user, status='Complete')
    else:
        vendor = VendorPayment.objects.filter(status='Complete')
    return render(request, 'dashboard/vendor_payment/list.html', {'vendor': vendor})


@login_required
@daseboard_required 
def vandor_payment_add_1(request):
    users = User.objects.filter(is_active=True, is_vendor=True)
    if request.method == 'POST':
        selected_user_id = request.POST['user']
        return redirect('vandor_payment_add_2', pk=selected_user_id)
    context = {
        'users': users,
    }
    return render(request, 'dashboard/vendor_payment/add.html', context)

@login_required
@daseboard_required 
def vandor_payment_add_2(request, pk):
    selected_user = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(
        items__item__user=selected_user,
        ordered=True,
        order_status='Complete'
    ).distinct()
    user_payments = VendorPayment.objects.filter(user=selected_user, status='Complete').values_list('product__id', flat=True)
    item_list = [
        item for order in orders for item in order.items.all()
        if item.item.id not in user_payments and item.item.user == selected_user
    ]
    if request.method == "POST":
        form = DashVendorPaymentForm(request.POST)
        if form.is_valid():
            products = form.cleaned_data['product']
            new_payment = form.save(commit=False)
            new_payment.user = selected_user
            new_payment.save()
            new_payment.product.set(products)
            messages.success(request, 'Payment request added successfully.')
            return redirect('dashboard-home')
        else:
            messages.error(request, 'Payment request creation failed. Please check the form errors.')
    else:
        form = DashVendorPaymentForm()

    context = {
        'orders': orders,
        'item_list': item_list,
        'form': form,
        'selected_user_id': pk,
        'payment': None,
        'request_date': None,
        'complete_date': None,
    }
    return render(request, 'dashboard/vendor_payment/add.html', context)


@login_required
@daseboard_required
def vandor_payment_details(request, pk):
    payment = get_object_or_404(VendorPayment, pk=pk)
    vendor_info = get_object_or_404(VendorInformation, user=payment.user)
    context = {
        'payment': payment,
        'vendor_info': vendor_info,
    }
    return render(request, 'dashboard/vendor_payment/details.html', context)




@login_required
@daseboard_required
def vandor_payment_update(request, pk):
    payment = get_object_or_404(VendorPayment, pk=pk)

    if not (request.user.is_staff or request.user.is_superuser or payment.user == request.user):
        messages.error(request, 'You do not have permission to edit this payment.')
        return redirect('dashboard-home')

    user_payments = VendorPayment.objects.filter(user=payment.user).exclude(pk=pk).values_list('product__id', flat=True) 

    orders = Order.objects.filter(
        items__item__user=payment.user,
        ordered=True,
        order_status='Complete'
    ).distinct()
    item_list = [
        item for order in orders for item in order.items.all()
        if item.item.id not in user_payments and item.item.user == payment.user
    ]

    if request.method == "POST":
        form = DashVendorPaymentForm(request.POST, instance=payment)
        if form.is_valid():
            products = form.cleaned_data['product']
            status = form.cleaned_data['status']
            updated_payment = form.save(commit=False)
            if request.user.is_superuser:
                updated_payment.user = payment.user
            if status == 'Complete':
                updated_payment.complete_date = timezone.now()
            updated_payment.save()
            updated_payment.product.set(products)
            messages.success(request, 'Payment request updated successfully.')
            if status == 'Complete':
                return redirect('vandor_payment_complete')
            return redirect('vandor_payment_pending')
        else:
            messages.error(request, 'Payment request update failed. Please check the form errors.')
    else:
        form = DashVendorPaymentForm(instance=payment)

    # print('item_list =================',item_list)
    context = {
        'orders': orders,
        'item_list': item_list,
        'form': form,
        'payment': payment,
        'selected_products': payment.product.all()
    }
    return render(request, 'dashboard/vendor_payment/update.html', context)

@login_required
@daseboard_required
def vandor_payment_delete(request, pk):
    profile = VendorPayment.objects.get(pk=pk)
    profile.delete()
    messages.success(request, 'Profile successfully deleted!')
    return redirect('vandor_payment_complete')


#Profile
@login_required
@daseboard_required
def profile_list(request):
    profile = Profile.objects.all()
    return render(request, 'dashboard/profile/profile-list.html', {'profile': profile})

@login_required
@daseboard_required
def profile_add(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully added!')
            return redirect('profile-list')
    else:
        form = UpdateProfileForm()
    return render(request, 'dashboard/profile/profile-add.html', {'form': form})

@login_required
@daseboard_required
def profile_update(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    form = UpdateProfileForm(request.POST, instance=profile)
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile successfully updated!')
            return redirect('profile-list')
    else:
        form = UpdateProfileForm(instance=profile)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/profile/profile-add.html', context)

@login_required
@daseboard_required
def profile_delete(request, pk):
    profile = Profile.objects.get(pk=pk)
    profile.delete()
    messages.success(request, 'Profile successfully deleted!')
    return redirect('profile-list')


@login_required
@daseboard_required
def create_parcel(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = PercelForm(request.POST)
        if form.is_valid():
            form.instance.order = order
            form.instance.customer_name = order.shipping_address.full_name
            form.instance.customer_phone = order.shipping_address.phone
            form.instance.customer_address = order.shipping_address.full_address
            form.instance.merchant_invoice_id = order.id
            form.instance.cash_collection_amount = order.due_amount
            form.instance.order_note = order.shipping_address.order_note

            # API details
            Api_Key = 'lcajvcs30r3kjei7uh4koit3dw1y6fq9'
            Secret_Key = 'sfrpkpdrdg9buwtu5tb9lpqw'
            api_url = 'https://portal.steadfast.com.bd/api/v1/create_order'

            payload = {
                "recipient_name": order.shipping_address.full_name,
                "recipient_phone": order.shipping_address.phone,
                "recipient_address": order.shipping_address.full_address,
                "invoice": str(order.id),
                "cod_amount": order.due_amount,
                "note": order.shipping_address.order_note
            }

            headers = {
                "Api-Key": Api_Key,
                "Secret-Key": Secret_Key,
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(api_url, headers=headers, json=payload)
                response.raise_for_status()  # Raise an error for bad status codes
                resp_data = response.json()

                # Extract consignment details
                tracking_code = resp_data['consignment']['tracking_code']

                # Save form and update order with consignment details
                form.instance.tracking_id = tracking_code
                form.save()
                order.redx_percel_traking_number = tracking_code
                order.save()

                messages.success(request, 'Parcel created successfully.')
                return redirect('pending_order')
            except requests.exceptions.RequestException as e:
           
                # Handle the error as needed
                if response.status_code == 400 and 'errors' in resp_data:
                    errors = resp_data['errors']
                    if 'invoice' in errors:
                        messages.error(request, f"Failed to create parcel: {errors['invoice'][0]}")
                    else:
                        messages.error(request, "An unknown error occurred. Please try again.")
                else:
                    messages.error(request, "Failed to create parcel. Please try again.")
    else:
        form = PercelForm()

    return render(request, 'dashboard/order_parcel/redx-percel-create.html', {'form': form, 'order': order})


#Image
@login_required
@daseboard_required
def image_list(request):
    images = ImageGallery.objects.all()
    return render(request, 'daseboard/gallery/image-list.html', {'images': images})


@login_required
@daseboard_required
def image_add(request):
    if request.method == 'POST':
        form = ImageAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Image successfully added!')
            return redirect('image-list')
    else:
        form = ImageAddForm()
    return render(request, 'daseboard/gallery/image-add.html', {'form': form})


@login_required
@daseboard_required
def image_update(request, pk):
    images = ImageGallery.objects.get(pk=pk)
    form = ImageAddForm(request.POST, request.FILES, instance=images)

    if request.method == 'POST':
        form = ImageAddForm(request.POST, request.FILES, instance=images)
        if form.is_valid():
            form.image = request.POST.get('image')
            form.save()
            messages.success(request, 'Image successfully updated!')
            return redirect('image-list')
    else:
        form = ImageAddForm(instance=images)
    context = {
        'images': images,
        'form': form,
    }
    return render(request, 'daseboard/gallery/image-update.html', context)


@login_required
@daseboard_required
def image_delete(request, pk):
    image = ImageGallery.objects.get(pk=pk)
    image.delete()
    messages.success(request, 'Image successfully deleted!')
    return redirect('image-list')


#Video
@login_required
@daseboard_required
def video_list(request):
    videos = VideoGallery.objects.all()
    return render(request, 'daseboard/gallery/video-list.html', {'videos': videos})


@login_required
@daseboard_required
def video_add(request):
    if request.method == 'POST':
        form = VideoAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'New video successfully added!')
            return redirect('video-list')
    else:
        form = VideoAddForm()
    return render(request, 'daseboard/gallery/video-add.html', {'form': form})


@login_required
@daseboard_required
def video_update(request, pk):
    video = VideoGallery.objects.get(pk=pk)
    form = VideoAddForm(request.POST, request.FILES, instance=video)

    if request.method == 'POST':
        form = VideoAddForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, 'Video successfully updated!')
            return redirect('video-list')
    else:
        form = VideoAddForm(instance=video)
    context = {
        'video': video,
        'form': form,
    }
    return render(request, 'daseboard/gallery/video-update.html', context)


@login_required
@daseboard_required
def video_delete(request, pk):
    video = VideoGallery.objects.get(pk=pk)
    video.delete()
    messages.success(request, 'Video successfully deleted!')
    return redirect('video-list')



# it is pathao api store create
@login_required
@daseboard_required
def create_store_and_verify(request, pk):
    profile = get_object_or_404(VendorInformation, pk=pk)
    # print(f'====================================================')
    # print(f'called create_store_and_verify = {profile = }')
    if not profile.store_id or profile.store_id == 'None':
        access_token = get_access_token()
        url = f"{settings.PATHAO_API_BASE_URL}/aladdin/api/v1/stores"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {
            "name": profile.shop_name,
            "contact_name": profile.user.full_name,
            "contact_number": profile.phone1,
            "secondary_contact": profile.phone2,
            "address": profile.address,
            "city_id": profile.division,
            "zone_id": profile.district,
            "area_id": profile.upazila,
        }
        try:
            with transaction.atomic():
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    res = response.json()
                    store_id = res["data"]["store_id"]
                    profile.store_id = store_id
                    # print(f'called create_store_and_verify inside if condition = {store_id = }')
                    profile.is_verified = True
                    profile.save()
                    messages.success(request, "Store successfully created and vendor verified!")
                else:
                    res = response.json()
                    error_message = res.get("errors", "Something went wrong!")  
                    messages.error(request, f"Error creating store: {error_message}")
        except requests.Timeout:
            messages.error(request, "The request to create the store timed out. Please try again.")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    else:
        # print(f'called create_store_and_verify inside else condition = {store_id = }')
        # print(f'====================================================')
        profile.is_verified = True
        profile.save()
        messages.info(request, "Profile Updated!!")


@login_required
@daseboard_required
def admin_create_pathao_store(request): # using
    query = VendorInformation.objects.filter(is_verified=True)
    if request.method == 'POST':
        vendor_info_id = request.POST.get('vendor_info_id')
        profile = get_object_or_404(VendorInformation, id=vendor_info_id)
        create_store_and_verify(request, profile.id)
        return redirect('admin_create_pathao_store')
    return render(request, 'dashboard/pathao/create-store.html', {'query':query})


@login_required
@daseboard_required
def pathao_store_list(request): # using
    query = PathaoStores.objects.all()
    for i in query:
        try:
            query2 = VendorInformation.objects.filter(is_verified=True, shop_name=i.store_name, division=i.city_id, district=i.zone_id).first()
            query2.store_id = i.store_id
            query2.save()
        except:
            continue
    return render(request, 'dashboard/pathao/pathao-store-list.html', {'query':query})




@login_required
@daseboard_required
def profile_accept_list(request):
    sort_by = request.GET.get('sort_by', 'max_sale')
    # Base queryset
    vendor = VendorInformation.objects.filter(is_verified=True)

    # Apply sorting
    if sort_by == 'max_order':
        vendor = sorted(vendor, key=lambda v: v.max_order(), reverse=True)
    elif sort_by == 'min_order':
        vendor = sorted(vendor, key=lambda v: v.max_order())
    elif sort_by == 'max_sale':
        vendor = sorted(vendor, key=lambda v: v.total_sales(), reverse=True)
    elif sort_by == 'min_sale':
        vendor = sorted(vendor, key=lambda v: v.total_sales())
    
    obj_paginator = Paginator(vendor, 25)
    obj_page_number = request.GET.get("page")
    vendor_profile = obj_paginator.get_page(obj_page_number)
    return render(request, 'dashboard/vendor-profile/profile_accept_list.html', {'vendor_profile': vendor_profile, 'sort_by':sort_by})


@login_required
@daseboard_required
def profile_unaccept_list(request):
    vendor_profile = VendorInformation.objects.filter(is_verified=False)
    return render(request, 'dashboard/vendor-profile/profile_unaccept_list.html', {'vendor_profile': vendor_profile})


@login_required
@daseboard_required
def vendor_profile_update(request, pk):
    profile = get_object_or_404(VendorInformation, pk=pk)
    if request.method == 'POST':
        form = VendorInformationFormUpdate(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            is_verify = form.cleaned_data['is_verified']
            if is_verify and (not profile.store_id or profile.store_id == 'None'):
                create_store_and_verify(request, pk)
            messages.success(request, 'Vendor profile successfully updated!')
            return redirect('profile_accept_list')
    else:
        form = VendorInformationFormUpdate(instance=profile)
    
    return render(request, 'dashboard/vendor-profile/profile_update.html', {'form': form})


@login_required
@daseboard_required
def vendor_profile_view(request, pk):
    profile = get_object_or_404(VendorInformation, pk=pk)
    return render(request, 'dashboard/vendor-profile/vendor-profile-view.html', {'profile': profile})



@login_required
@daseboard_required
def vendor_product_list(request, pk):
    profile = get_object_or_404(VendorInformation, pk=pk)
    form_type = request.GET.get('form_type', '')
    approval = request.GET.get('approval', 'Complete')
    order_status = request.GET.get('order-status', 'Complete')
    payment_status = request.GET.get('payment-status', 'Complete')
    return_product_status = request.GET.get('return-product-status', 'Complete')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    search = request.GET.get('search', '')

    verify = True if approval == 'Complete' else False
    if from_date:
        from_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M')
    if to_date:
        to_date = datetime.strptime(to_date, '%Y-%m-%dT%H:%M')
    
    # product filter start
    if form_type == 'product':
        product_list = Product.objects.filter(
            Q(product_name__icontains=search) | Q(parent_code__icontains=search) |
            Q(categoris__category_name__icontains=search) | Q(brand__name__icontains=search) |
            Q(price_range__price_range__icontains=search),
            user=profile.user, is_verified=verify
        )
        if from_date:
            product_list = product_list.filter(created_at__gte=from_date)
        if to_date:
            product_list = product_list.filter(created_at__lte=to_date)
    else:
        product_list = Product.objects.filter(user=profile.user,is_verified=verify)
    products_paginator = Paginator(product_list, 10)
    products_page_number = request.GET.get("page")
    products = products_paginator.get_page(products_page_number)
    # product filter end
    # order filter start
    if form_type == 'order':
        order_list = Order.objects.filter(
            Q(orderId__icontains=search) | Q(payment_option__icontains=search),
            items__item__user=profile.user, order_status=order_status, ordered=True
        )
        if from_date:
            order_list = order_list.filter(ordered_date__gte=from_date)
        if to_date:
            order_list = order_list.filter(ordered_date__lte=to_date)
    else:
        order_list = Order.objects.filter(items__item__user=profile.user, order_status=order_status)
    order_paginator = Paginator(order_list, 10)
    order_page_number = request.GET.get("page")
    orders = order_paginator.get_page(order_page_number)
    # order filter end
    # payment filter start
    if form_type == 'payment':
        payment_list = VendorPayment.objects.filter(
            Q(message__icontains=search) | Q(remark__icontains=search),
            user=profile.user, status=payment_status
        )
        if from_date:
            payment_list = payment_list.filter(request_date__gte=from_date)
        if to_date:
            payment_list = payment_list.filter(request_date__lte=to_date)
    else:
        payment_list = VendorPayment.objects.filter(user=profile.user, status=payment_status)
    payment_paginator = Paginator(payment_list, 10)
    payment_page_number = request.GET.get("page")
    payments = payment_paginator.get_page(payment_page_number)
    # payment filter end
    # return product filter start
    if form_type == 'return_product':
        returnproduct_list = ReturnProduct.objects.filter(
            Q(comment__icontains=search) | Q(bank_transfer__icontains=search),
            items__item__user=profile.user, status=return_product_status
        )
        if from_date:
            returnproduct_list = returnproduct_list.filter(created_on__gte=from_date)
        if to_date:
            returnproduct_list = returnproduct_list.filter(created_on__lte=to_date)
    else:
        returnproduct_list = ReturnProduct.objects.filter(items__item__user=profile.user, status=return_product_status)
    returnproduct_paginator = Paginator(returnproduct_list, 10)
    returnproduct_page_number = request.GET.get("page")
    returnproducts = returnproduct_paginator.get_page(returnproduct_page_number)
    # return product filter end

    nav_active_item = request.GET.get("order_page") if request.GET.get("order_page") else "product" if not form_type else form_type
    context ={
        "user_id":profile.user.id,
        'products': products,
        'orders': orders,
        'payments': payments,
        'nav_active_item':nav_active_item,
        'returnproducts':returnproducts,

        'form_type':form_type,
        'approval':approval,
        'order_status':order_status,
        'payment_status':payment_status,
        'return_product_status':return_product_status,
        'from_date':from_date,
        'to_date':to_date,
        'search':search,
        }
    return render(request, 'dashboard/vendor-profile/vendor-product-list.html', context)


@login_required
@daseboard_required
def vendor_all_details(request,pk):
    order = Order.objects.get(pk=pk)
    order.order_read_status = True
    order.save()
    user = request.GET.get('user_id')
    order_items = OrderItem.objects.filter(order=order, item__user=user)
    context = {
        'user_id': user,
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'dashboard/order/vendor-order-detail.html', context)


@login_required
@daseboard_required
def vendor_profile_verify(request, pk):
    create_store_and_verify(request, pk)
    return redirect('vendor_profile_view', pk=pk)


@login_required
@daseboard_required
def vendor_profile_delete(request, pk):
    profile = VendorInformation.objects.get(pk=pk)
    profile.delete()
    messages.success(request, 'Vendor profile successfully deleted!')
    return redirect('profile_unaccept_list')


#Price Range
@login_required
@daseboard_required
def price_range_data(request): # use
    obj = PriceRange.objects.all().order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    added = False
    form = PriceRangeForm()
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            objects = PriceRange.objects.get(id=obj_id)
        else:
            objects = None
        form = PriceRangeForm(request.POST, request.FILES, instance=objects)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your banner has been successfully updated!')
                return redirect('price_range_data')
            else:
                added = True
                messages.success(request, 'Your banner has been successfully added!')
        else:
            messages.error(request, 'Data didn"t valid!')
    return render(request, 'dashboard/price_range/price-range-data.html', {'query': query, 'form': form, 'added':added})


@login_required
@daseboard_required
def price_range_delete(request, pk):
    price_range = PriceRange.objects.get(pk=pk)
    price_range.delete()
    messages.success(request, 'Price range successfully deleted!')
    return redirect('price_range_data')

@login_required
@daseboard_required
def price_range_list(request):
    price_ranges = PriceRange.objects.all()
    return render(request, 'dashboard/price_range/price_range_list.html', {'price_ranges': price_ranges})


@login_required
@daseboard_required
def price_range_create(request):
    if request.method == 'POST':
        form = PriceRangeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New price range successfully added!')
            return redirect('price_range_list')
    else:
        form = PriceRangeForm()
    return render(request, 'dashboard/price_range/price_range_form.html', {'form': form})


@login_required
@daseboard_required
def price_range_update(request, pk):
    price_range = PriceRange.objects.get(pk=pk)
    if request.method == 'POST':
        form = PriceRangeForm(request.POST, instance=price_range)
        if form.is_valid():
            form.save()
            messages.success(request, 'Price range successfully updated!')
            return redirect('price_range_list')
    else:
        form = PriceRangeForm(instance=price_range)
    return render(request, 'dashboard/price_range/price_range_form.html', {'form': form})




@login_required
@daseboard_required
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            
            user = request.user
            if user.check_password(current_password):
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Password successfully changed!.')
                    return redirect('dashboard-home')
                else:
                    messages.error(request, 'New passwords do not match.')
            else:
                messages.error(request, 'Current password is incorrect.')
    else:
        form = ChangePasswordForm()
    return render(request, 'dashboard/user/change-password.html')


def update_profile(request):
    if request.method == 'POST':
        u_form = UpdateRegisterForm(request.POST, instance=request.user)
        p_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('dashboard-home')
    else:
        u_form = UpdateRegisterForm(instance=request.user)
        p_form = UpdateProfileForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
    }
    return render(request, 'dashboard/user/update-profile.html', context)

def website_information_create(request):
    if request.method == 'POST':
        form = WebsiteInformationForm(request.POST, request.FILES)
        phone_formset = PhoneNumberFormSet(request.POST, prefix='phone')
        email_formset = EmailAddressFormSet(request.POST, prefix='email')
        address_formset = CompanyAddressFormSet(request.POST, prefix='address')

        if form.is_valid() and phone_formset.is_valid() and email_formset.is_valid() and address_formset.is_valid():
            website_info = form.save()
            phone_formset.instance = website_info
            phone_formset.save()
            email_formset.instance = website_info
            email_formset.save()
            address_formset.instance = website_info
            address_formset.save()
            return redirect('website_information_list')
    else:
        form = WebsiteInformationForm()
        phone_formset = PhoneNumberFormSet(prefix='phone')
        email_formset = EmailAddressFormSet(prefix='email')
        address_formset = CompanyAddressFormSet(prefix='address')

    return render(request, 'dashboard/logo/website_information_form.html', {
        'form': form,
        'phone_formset': phone_formset,
        'email_formset': email_formset,
        'address_formset': address_formset
    })

def website_information_update(request, pk):
    website_info = get_object_or_404(WebsiteInformation, pk=pk)
    if request.method == 'POST':
        form = WebsiteInformationForm(request.POST, request.FILES, instance=website_info)
        phone_formset = PhoneNumberFormSet(request.POST, instance=website_info, prefix='phone')
        email_formset = EmailAddressFormSet(request.POST, instance=website_info, prefix='email')
        address_formset = CompanyAddressFormSet(request.POST, instance=website_info, prefix='address')

        if form.is_valid() and phone_formset.is_valid() and email_formset.is_valid() and address_formset.is_valid():
            form.save()
            phone_formset.save()
            email_formset.save()
            address_formset.save()
            return redirect('website_information_list')
    else:
        form = WebsiteInformationForm(instance=website_info)
        phone_formset = PhoneNumberFormSet(instance=website_info, prefix='phone')
        email_formset = EmailAddressFormSet(instance=website_info, prefix='email')
        address_formset = CompanyAddressFormSet(instance=website_info, prefix='address')

    return render(request, 'dashboard/logo/website_information_form.html', {
        'form': form,
        'phone_formset': phone_formset,
        'email_formset': email_formset,
        'address_formset': address_formset
    })


def website_information_list(request):
    website_infos = WebsiteInformation.objects.all()
    context = {'website_infos': website_infos}
    return render(request, 'dashboard/logo/website_information_list.html', context)


def website_information_detail(request, pk):
    website_info = get_object_or_404(WebsiteInformation, pk=pk)
    phone_numbers = PhoneNumber.objects.filter(website=website_info)
    email_addresses = EmailAddress.objects.filter(website=website_info)
    company_addresses = CompanyAddress.objects.filter(website=website_info)
    context = {
        'website_info': website_info,
        'phone_numbers': phone_numbers,
        'email_addresses': email_addresses,
        'company_addresses': company_addresses
    }
    return render(request, 'dashboard/logo/website_information_detail.html', context)


def delete_website_info(request, pk):
    website_info = get_object_or_404(WebsiteInformation, pk=pk)
    website_info.delete()
    messages.success(request, 'Website successfully deleted!')
    return redirect('website_information_list')


@csrf_exempt
def delete_phone_number(request):
    if request.method == 'POST' and request.is_ajax():
        phone_id = request.POST.get('phone_id')
        if phone_id:
            PhoneNumber.objects.filter(id=phone_id).delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
def delete_email_address(request):
    if request.method == 'POST' and request.is_ajax():
        email_id = request.POST.get('email_id')
        if email_id:
            EmailAddress.objects.filter(id=email_id).delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@csrf_exempt
def delete_company_address(request):
    if request.method == 'POST' and request.is_ajax():
        address_id = request.POST.get('address_id')
        if address_id:
            CompanyAddress.objects.filter(id=address_id).delete()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})



# color 
@login_required
@daseboard_required
def color_data(request): # use
    obj = Color.objects.all().order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    added = False
    form = ColorForm()
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            objects = Color.objects.get(id=obj_id)
        else:
            objects = None
        form = ColorForm(request.POST, request.FILES, instance=objects)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your color has been successfully updated!')
                return redirect('color_data')
            else:
                added = True
                messages.success(request, 'Your color has been successfully added!')
        else:
            messages.error(request, 'Data didn"t valid!')
    return render(request, 'dashboard/color/color-data.html', {'query': query, 'form': form, 'added':added})


@login_required
@daseboard_required
def color_delete(request, pk): # use
    color = Color.objects.get(pk=pk)
    color.delete()
    messages.success(request, 'Successfully color deleted!.')
    return redirect('color_data')


@login_required
@daseboard_required
def color_add(request):
    color = Color.objects.all()
    if request.method == "POST":
        form = ColorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully color added!')
            return redirect('colors_list')
    form = ColorForm()
    # return render(request, 'dashboard/color/color-add.html', {'form': form})
    return render(request, 'dashboard/color/color-form.html', {'form': form, 'color': color})


@login_required
@daseboard_required
def colors_list(request):
    colors = Color.objects.all()
    return render(request, 'dashboard/color/colors-list.html', {'colors': colors})


@login_required
@daseboard_required
def color_update(request, pk):
    color = get_object_or_404(Color, pk=pk)
    if request.method == "POST":
        form = ColorForm(request.POST, instance=color)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully color updated!')
            return redirect('colors_list')
    form = ColorForm(instance=color)
    return render(request, 'dashboard/color/color-add.html', {'form': form, 'color': color})


# @login_required
# @daseboard_required
# def color_delete(request, pk):
#     color = Color.objects.get(pk=pk)
#     color.delete()
#     messages.success(request, 'Successfully color deleted!.')
#     return redirect('colors_list')


# size
@login_required
@daseboard_required
def size_data(request): # use
    obj = Size.objects.all().order_by('-id')
    obj_pagignator = Paginator(obj, 15)
    obj_page_number = request.GET.get("page")
    query = obj_pagignator.get_page(obj_page_number)

    added = False
    form = SizeForm()
    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        if obj_id:
            objects = Size.objects.get(id=obj_id)
        else:
            objects = None
        form = SizeForm(request.POST, request.FILES, instance=objects)
        if form.is_valid():
            form.save()
            if obj_id:
                messages.success(request, 'Your size has been successfully updated!')
                return redirect('size_data')
            else:
                added = True
                messages.success(request, 'Your size has been successfully added!')
        else:
            messages.error(request, 'Data didn"t valid!')
    return render(request, 'dashboard/size/size-data.html', {'query': query, 'form': form, 'added':added})


@login_required
@daseboard_required
def size_delete(request, pk): # use
    size = Size.objects.get(pk=pk)
    size.delete()
    messages.success(request, 'Successfully size deleted!.')
    return redirect('size_data')


@login_required
@daseboard_required
def size_add(request):
    if request.method == "POST":
        form = SizeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully size added!')
            return redirect('sizes_list')
    form = SizeForm()
    return render(request, 'dashboard/size/size-add.html', {'form': form})


@login_required
@daseboard_required
def sizes_list(request):
    sizes = Size.objects.all()
    return render(request, 'dashboard/size/sizes-list.html', {'sizes': sizes})


@login_required
@daseboard_required
def size_update(request, pk):
    size = get_object_or_404(Size, pk=pk)
    if request.method == "POST":
        form = SizeForm(request.POST, instance=size)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully size updated!')
            return redirect('sizes_list')
    else:
        form = SizeForm(instance=size)
    return render(request, 'dashboard/size/size-add.html', {'form': form})





# @login_required
# @daseboard_required
# def product_verify(request):
#     if request.method == 'POST':
#         product_ids = request.POST.getlist('selected_products')
#         Product.objects.filter(id__in=product_ids).update(is_verified=True)
#         return redirect('publish_product_list')


 



