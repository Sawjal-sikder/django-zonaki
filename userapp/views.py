from django.shortcuts import render, redirect
from userapp.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from uniform import *
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from sundorban.settings import DEFAULT_FROM_EMAIL
from django.contrib.auth.forms import PasswordChangeForm
from store.models import Order, Coupon

User = get_user_model()


def signup(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_customer = True
            user.save()
            login(request, user, backend='userapp.backends.EmailOrPhoneBackend')
            messages.success(request, 'Welcome! Your registration was successful.')
            return redirect('home')
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = RegisterForm()
    return render(request, 'userapp/register.html', {'form': form})


# def signin(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 if user.is_customer:
#                     login(request, user)
#                     return redirect('home')
#                 elif user.is_vendor:
#                     login(request, user)
#                     return redirect('dashboard-home')
#                 elif user.is_staff:
#                     login(request, user)
#                     return redirect('dashboard-home')
#             else:
#                 messages.error(request, 'Your account is not active. Please contact the administrator.')
#         else:
#             messages.error(request, 'Invalid credentials. Please try again.')
#     return render(request, 'userapp/login.html')

from django.utils.http import is_safe_url
def signin(request):
    if request.method == 'POST':
        # Get username and password from the request
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Success! You're in. Ready to explore?")
            
            # Get the next URL from the session (if it exists)
            next_url = request.session.get('next', None)
            
            # Ensure the next_url is safe, only redirect to internal URLs
            if next_url and is_safe_url(next_url, allowed_hosts=request.get_host()):
                request.session.pop('next', None)  # Remove next from session after redirect
                return redirect(next_url)
            
            # Fallback to default URL
            if user.is_superuser or user.is_staff:
                next_url = 'dashboard-home'
            else:
                next_url = 'home'
            
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid login credentials.')
    
    if 'next' in request.GET:
        next_url = request.GET['next']
        
        # Check if the 'next' URL starts with '/add-to-cart/'
        if next_url.startswith('/add-to-cart/'):
            request.session['next'] = request.META.get('HTTP_REFERER', '/login/')
        else:
            request.session['next'] = request.GET['next']

    return render(request, 'userapp/login.html')


@login_required(login_url='signin')
def signout(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('/')


@login_required(login_url='signin')
def customer_dashboard(request):
    order = Order.objects.filter(user=request.user, ordered=True).count()
    coupons = Coupon.objects.filter(is_verified=True, coupon_user=request.user)
    return render(request, 'userapp/dashboard.html', {'order': order, 'coupons':coupons})


@login_required(login_url='signin')
def profile(request):
    return render(request, 'userapp/profile.html')


@login_required(login_url='signin')
def profile_update(request):
    if request.method == 'POST':
        u_form = UpdateRegisterForm(request.POST, instance=request.user)
        p_form = UpdateProfileForm(
            request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')

    else:
        u_form = UpdateRegisterForm(instance=request.user)
        p_form = UpdateProfileForm(instance=request.user.profile)

    context = {

        'u_form': u_form,
        'p_form': p_form,
    }

    return render(request, 'userapp/profile_update.html', context)


@login_required(login_url='signin')
def password_change(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            if request.user.is_superuser:
                return redirect('dashboard-home')
            elif request.user.is_vendor or request.user.is_staff:
                return redirect('dashboard-home')
            else:
                return redirect('customer_dashboard')
        
     
    return render(request, 'userapp/password_change.html')


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
      
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = reverse('password_reset_confirm', args=(uid, token))
            current_site = get_current_site(request)
            mail_subject = 'Password Reset Request'
            message = render_to_string('userapp/password_reset_email.html', {
                'user': user,
                'domain': current_site.domain,
                'reset_link': reset_link,
            })
            send_mail(mail_subject, message, DEFAULT_FROM_EMAIL, [email])
            # print('send_mail ================', send_mail(mail_subject, message, DEFAULT_FROM_EMAIL, [email]))
        return render(request, 'userapp/password_reset_done.html', {'email': email})
    return render(request, 'userapp/password_reset.html')


# def password_reset_confirm(request, uidb64, token):
#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         user = None

#     if user and default_token_generator.check_token(user, token):
#         if request.method == 'POST':
#             new_password = request.POST.get('new_password')
#             user.set_password(new_password)
#             user.save()
#             return redirect('password_reset_complete')
#         return render(request, 'userapp/password_reset_confirm.html')
#     else:
#         return HttpResponse('Password reset link is invalid')

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()

                return redirect('password_reset_complete') 
        return render(request, 'userapp/password_reset_confirm.html')
    else:
        return HttpResponse('Password reset link is invalid')


def password_reset_done(request):
    return render(request, 'userapp/password_reset_done.html')


def password_reset_complete(request):
    return render(request, 'userapp/password_reset_complete.html')


def google_login_with_registration_type(request):
    registration_type = request.GET.get('registration_type')  
    if registration_type == 'customer': 
        request.session['registration_type'] = 'customer' 
    return redirect('google_login')