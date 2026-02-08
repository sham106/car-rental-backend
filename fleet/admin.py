from django.contrib import admin
from .models import Vehicle

# Register your models here.

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'make', 'model', 'year', 'category', 'price_per_day', 'availability')
    list_filter = ('category', 'availability')
    search_fields = ('make', 'model')
