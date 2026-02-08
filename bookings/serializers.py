from rest_framework import serializers
from .models import Booking
from django.utils import timezone
from datetime import datetime
import json


class BookingSerializer(serializers.ModelSerializer):
    # Explicitly define datetime fields to ensure proper handling
    pickup_date = serializers.DateTimeField()
    return_date = serializers.DateTimeField()
    
    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'vehicle_id', 'pickup_date', 'return_date',
            'pickup_location', 'return_location', 'driver_name', 'driver_email',
            'driver_phone', 'license_number', 'license_image', 'enhancements', 'base_price',
            'enhancements_price', 'total_price', 'payment_status', 'payment_method',
            'status', 'booking_reference', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'booking_reference', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        """Convert naive datetimes to aware datetimes before validation"""
        # Make a copy to avoid modifying the original
        data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Process pickup_date
        if 'pickup_date' in data:
            pickup_date = data['pickup_date']
            if isinstance(pickup_date, str):
                try:
                    # Try parsing the datetime string
                    from datetime import datetime
                    # Try ISO format first
                    try:
                        dt = datetime.fromisoformat(pickup_date.replace('Z', '+00:00'))
                    except ValueError:
                        # Try common formats
                        formats = [
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%dT%H:%M',
                            '%Y-%m-%d %H:%M',
                        ]
                        dt = None
                        for fmt in formats:
                            try:
                                dt = datetime.strptime(pickup_date, fmt)
                                break
                            except ValueError:
                                continue
                        if dt is None:
                            raise ValueError(f"Unable to parse date: {pickup_date}")
                    
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    data['pickup_date'] = dt
                except (ValueError, TypeError):
                    pass
        
        # Process return_date
        if 'return_date' in data:
            return_date = data['return_date']
            if isinstance(return_date, str):
                try:
                    # Try parsing the datetime string
                    from datetime import datetime
                    # Try ISO format first
                    try:
                        dt = datetime.fromisoformat(return_date.replace('Z', '+00:00'))
                    except ValueError:
                        # Try common formats
                        formats = [
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%dT%H:%M',
                            '%Y-%m-%d %H:%M',
                        ]
                        dt = None
                        for fmt in formats:
                            try:
                                dt = datetime.strptime(return_date, fmt)
                                break
                            except ValueError:
                                continue
                        if dt is None:
                            raise ValueError(f"Unable to parse date: {return_date}")
                    
                    if timezone.is_naive(dt):
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                    data['return_date'] = dt
                except (ValueError, TypeError):
                    pass
        
        return super().to_internal_value(data)
    
    def validate_pickup_date(self, value):
        """Ensure pickup_date is timezone-aware"""
        if value and timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value
    
    def validate_return_date(self, value):
        """Ensure return_date is timezone-aware"""
        if value and timezone.is_naive(value):
            return timezone.make_aware(value, timezone.get_current_timezone())
        return value

    def validate_enhancements(self, value):
        if value:
            try:
                if isinstance(value, str):
                    json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format for enhancements")
        return value

    def create(self, validated_data):
        """Ensure datetimes are timezone-aware before saving"""
        pickup_date = validated_data.get('pickup_date')
        return_date = validated_data.get('return_date')
        
        if pickup_date and timezone.is_naive(pickup_date):
            validated_data['pickup_date'] = timezone.make_aware(
                pickup_date, timezone.get_current_timezone()
            )
        
        if return_date and timezone.is_naive(return_date):
            validated_data['return_date'] = timezone.make_aware(
                return_date, timezone.get_current_timezone()
            )
        
        return super().create(validated_data)