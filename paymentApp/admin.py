from django.contrib import admin
from .models import *
# Register your models here.

class BkashPaymentAdmin(admin.ModelAdmin):
    list_display = ('id','user','paymentID','amount','merchantInvoiceNumber')

admin.site.register(ShipingAddress)
admin.site.register(BkashPayment,BkashPaymentAdmin)
admin.site.register(BkashPaymentExecute)
admin.site.register(BkashPaymentRefund)
admin.site.register(PathaoStores)
admin.site.register(BkashApi)
admin.site.register(PathaoToken)