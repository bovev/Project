from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'get_customer_name',
        'get_cottage_name',
        'amount',
        'billed_at',
        'due_date',
        'status',
        'paid_at',
    )
    
    list_filter = (
        'status',
        'billed_at',
        'due_date',
        'paid_at',
    )
    
    search_fields = (
        'invoice_number',
        'reservation__customer__full_name',
        'reservation__cottage__name',
        'notes',
    )
    
    readonly_fields = ('created_at', 'invoice_number')
    
    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'reservation', 'amount')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'billed_at', 'due_date', 'paid_at')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Additional Information'), {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    actions = ['mark_as_paid']
    
    def get_customer_name(self, obj):
        """Get the customer name from the related reservation."""
        return obj.reservation.customer.full_name
    get_customer_name.short_description = _('Customer')
    get_customer_name.admin_order_field = 'reservation__customer__full_name'
    
    def get_cottage_name(self, obj):
        """Get the cottage name from the related reservation."""
        return obj.reservation.cottage.name
    get_cottage_name.short_description = _('Cottage')
    get_cottage_name.admin_order_field = 'reservation__cottage__name'
    
    def mark_as_paid(self, request, queryset):
        """Admin action to mark selected invoices as paid."""
        updated = 0
        for invoice in queryset.filter(status='pending'):
            invoice.mark_as_paid()
            updated += 1
        
        if updated == 1:
            message = _('1 invoice was marked as paid.')
        else:
            message = _('{} invoices were marked as paid.').format(updated)
        
        self.message_user(request, message)
    mark_as_paid.short_description = _('Mark selected invoices as paid')