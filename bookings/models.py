from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver

User = get_user_model()


class AwareDateTimeField(models.DateTimeField):
    """Custom DateTimeField that automatically converts naive datetimes to aware"""
    
    def to_python(self, value):
        if value is None:
            return value
        
        # If it's already a datetime object
        if hasattr(value, 'hour'):
            if timezone.is_naive(value):
                return timezone.make_aware(value, timezone.get_current_timezone())
            return value
        
        # If it's a string, suppress the warning and parse
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            result = super().to_python(value)
        
        if result and timezone.is_naive(result):
            return timezone.make_aware(result, timezone.get_current_timezone())
        return result
    
    def get_prep_value(self, value):
        """Prepare value for database"""
        if value is None:
            return value
        
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone.get_current_timezone())
        
        return super().get_prep_value(value)


def license_upload_path(instance, filename):
    """Generate upload path for license images"""
    return f'licenses/user_{instance.user.id}/{filename}'


@receiver(pre_save, sender='bookings.Booking')
def make_datetime_aware(sender, instance, **kwargs):
    """Convert naive datetimes to aware datetimes before saving"""
    # This is a fallback - the AwareDateTimeField should handle most cases
    if instance.pickup_date and timezone.is_naive(instance.pickup_date):
        instance.pickup_date = timezone.make_aware(
            instance.pickup_date, timezone.get_current_timezone()
        )
    if instance.return_date and timezone.is_naive(instance.return_date):
        instance.return_date = timezone.make_aware(
            instance.return_date, timezone.get_current_timezone()
        )


class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'),
        ('PAID', 'Paid at Pickup'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    vehicle_id = models.IntegerField()
    
    # Rental details
    pickup_date = AwareDateTimeField()
    return_date = AwareDateTimeField()
    pickup_location = models.CharField(max_length=200)
    return_location = models.CharField(max_length=200)
    
    # Driver information
    driver_name = models.CharField(max_length=200)
    driver_email = models.EmailField()
    driver_phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    license_image = models.ImageField(upload_to=license_upload_path, blank=True, null=True)
    
    # Enhancements
    enhancements = models.TextField(blank=True, default='[]')  # JSON array
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    enhancements_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50, default='Manual at Pickup')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    # Reference
    booking_reference = models.CharField(max_length=20, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_reference} - {self.driver_name}"

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate booking reference
            import random
            import string
            prefix = 'LX'
            random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            self.booking_reference = f"{prefix}-{random_chars}"
        super().save(*args, **kwargs)
