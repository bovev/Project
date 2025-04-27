from django.contrib import admin
from .models import Reservation, ReservationStatus
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'cottage_name', 'guest_name', 'start_date', 'end_date', 
                    'guests', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'start_date', 'end_date', 'cottage')
    search_fields = ('cottage__name', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Reservation Details'), {
            'fields': ('cottage', 'user', 'status')
        }),
        (_('Stay Information'), {
            'fields': ('start_date', 'end_date', 'guests', 'total_price')
        }),
        (_('System Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def cottage_name(self, obj):
        return obj.cottage.name
    cottage_name.short_description = _('Cottage')
    cottage_name.admin_order_field = 'cottage__name'
    
    def guest_name(self, obj):
        return f"{obj.user.get_full_name() or obj.user.username} ({obj.user.email})"
    guest_name.short_description = _('Guest')
    guest_name.admin_order_field = 'user__username'
    
    actions = ['confirm_reservations', 'mark_as_completed', 'cancel_reservations']
    
    def confirm_reservations(self, request, queryset):
        updated = queryset.filter(status=ReservationStatus.PENDING).update(status=ReservationStatus.CONFIRMED)
        self.message_user(request, _(f'{updated} reservations were confirmed.'))
    confirm_reservations.short_description = _('Confirm selected reservations')
    
    def mark_as_completed(self, request, queryset):
        today = timezone.now().date()
        updated = queryset.filter(end_date__lt=today).update(status=ReservationStatus.COMPLETED)
        self.message_user(request, _(f'{updated} reservations were marked as completed.'))
    mark_as_completed.short_description = _('Mark selected reservations as completed')
    
    def cancel_reservations(self, request, queryset):
        updated = queryset.update(status=ReservationStatus.CANCELLED)
        self.message_user(request, _(f'{updated} reservations were cancelled.'))
    cancel_reservations.short_description = _('Cancel selected reservations')
    
    def save_model(self, request, obj, form, change):
        # Skip validation if admin changes the status to cancelled
        if change and 'status' in form.changed_data and obj.status == ReservationStatus.CANCELLED:
            super(ReservationAdmin, self).save_model(request, obj, form, change)
        else:
            # Use the model's save method which includes validation
            obj.save()