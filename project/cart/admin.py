from django.contrib import admin
from .models import Customer,Order,Product



@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display=[ 'id','user','customer','product','quantity','date','phone','address','order_status','cancellation_requested','payment' ]