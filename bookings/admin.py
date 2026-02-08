from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_reference', 'driver_name', 'driver_email', 'vehicle_id', 'pickup_date', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['booking_reference', 'driver_name', 'driver_email', 'license_number']
    readonly_fields = ['booking_reference', 'created_at', 'updated_at']
