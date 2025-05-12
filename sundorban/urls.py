
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('store.urls')),
    path('', include('paymentApp.urls')),
    path('', include('userapp.urls')),
    path('', include('daseboard.urls')),
    path('', include('other_vendors.urls')),
    # path('oauth/', include('social_django.urls', namespace='social')),

    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),

]

# handler404 = 'paymentApp.views.page_not_found'