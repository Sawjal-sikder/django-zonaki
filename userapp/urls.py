from django.urls import path
from userapp import views


urlpatterns =[
    path("signup", views.signup, name="signup"),
    path('login/', views.signin, name="signin"),
    path('signout/', views.signout, name='signout'),
     path('customer/dashboard', views.customer_dashboard, name='customer_dashboard'),
    path('profile', views.profile, name='profile'),
    path('profile/update', views.profile_update, name='profile_update'),
    
    #Change Password
    path('password-change', views.password_change, name='password_change'),
    
    #Reset Password URL
    path('password-reset', views.password_reset, name='password_reset'),
    path('password-reset/done', views.password_reset_done, name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete', views.password_reset_complete, name='password_reset_complete'),
    
    path('google-login/', views.google_login_with_registration_type, name='google_login_with_type'),
]
