from django.contrib import admin
from .models import AssociationFeeType, PaymentRecord,CorpusFundRecord
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


@admin.register(CorpusFundRecord)
class CorpusFundRecordAdmin(admin.ModelAdmin):
    list_display = ('house', 'amount', 'is_paid', 'paid_on', 'receipt_number')
    list_filter = ('is_paid', 'paid_on')
    search_fields = ('house__owner_name', 'house__house_number', 'receipt_number')
    readonly_fields = ('receipt_number', 'paid_on')
    ordering = ('-paid_on',)


