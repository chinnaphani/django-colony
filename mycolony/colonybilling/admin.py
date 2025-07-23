from django.contrib import admin
from .models import AssociationFeeType, PaymentRecord
# Register your models here.

@admin.register (AssociationFeeType)
class AssociationFeeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'association', 'frequency','amount','is_active',)

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('receipt_number','house', 'fee_type', 'amount', 'due_date', 'is_paid', 'paid_on', 'created_at')
    list_filter = ('fee_type__frequency', 'is_paid', 'due_date')
    search_fields = ('house__house_number', 'fee_type__name', 'house__owner_name')
    date_hierarchy = 'due_date'