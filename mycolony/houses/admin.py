from django.contrib import admin
from .models import House

# Register your models here.
@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ['house_number', 'owner_name', 'membership_number', 'membership_date', 'active','association']
    list_filter = ['association', 'active']
    search_fields = ['house_number', 'owner_name', 'membership_number','phone_number']

