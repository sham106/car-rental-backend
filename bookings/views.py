from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime
from .models import Booking
from .serializers import BookingSerializer
from notifications.utils import send_booking_email_notification

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class BookingListCreateView(generics.ListCreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def create(self, request, *args, **kwargs):
        print("=" * 50)
        print("Incoming request data:", request.data)
        print("=" * 50)
        
        serializer = self.get_serializer(data=request.data)
        
        # This will show validation errors
        if not serializer.is_valid():
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        print("Validated data:", serializer.validated_data)
        
        # Check if vehicle is available for the requested dates
        vehicle_id = serializer.validated_data.get('vehicle_id')
        pickup_date = serializer.validated_data.get('pickup_date')
        return_date = serializer.validated_data.get('return_date')
        
        print(f"Checking availability for vehicle {vehicle_id} from {pickup_date} to {return_date}")
        
        # Check for conflicting bookings (excluding cancelled bookings)
        conflicting_bookings = Booking.objects.filter(
            vehicle_id=vehicle_id,
            status__in=['PENDING', 'CONFIRMED', 'ACTIVE']
        ).filter(
            pickup_date__lt=return_date,
            return_date__gt=pickup_date
        )
        
        if conflicting_bookings.exists():
            return Response(
                {'error': 'This vehicle is not available for the selected dates. Please choose different dates or a different vehicle.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set the user from the request
        booking = serializer.save(user=request.user)
        
        # Send email notification to admin
        from django.conf import settings
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'shamsikush@gmail.com')
        send_booking_email_notification(booking, admin_email)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Only allow staff to update certain fields
        if not request.user.is_staff:
            # Remove restricted fields for non-staff
            restricted_fields = ['status', 'payment_status', 'user']
            for field in restricted_fields:
                if field in request.data:
                    del request.data[field]
        
        serializer.save()
        return Response(serializer.data)


@api_view(['GET'])
def get_vehicle_booked_dates(request, vehicle_id):
    """
    Get all booked dates for a vehicle (for calendar display).
    Returns a list of date ranges that are booked.
    """
    from django.utils.dateparse import parse_date
    
    # Get all confirmed/pending/active bookings for this vehicle
    bookings = Booking.objects.filter(
        vehicle_id=vehicle_id,
        status__in=['PENDING', 'CONFIRMED', 'ACTIVE']
    ).order_by('pickup_date')
    
    booked_dates = []
    for booking in bookings:
        booked_dates.append({
            'id': booking.id,
            'pickup_date': booking.pickup_date.isoformat(),
            'return_date': booking.return_date.isoformat(),
            'status': booking.status,
            'user_name': booking.driver_name,
        })
    
    return Response({
        'vehicle_id': vehicle_id,
        'bookings': booked_dates,
    })


@api_view(['GET'])
def check_vehicle_availability(request, vehicle_id):
    """
    Check if a vehicle is available for given dates.
    Query params: pickup_date, return_date
    """
    pickup_date_str = request.query_params.get('pickup_date')
    return_date_str = request.query_params.get('return_date')
    
    if not pickup_date_str or not return_date_str:
        return Response({'error': 'Please provide pickup_date and return_date'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Parse and convert to aware datetimes
    pickup_date = parse_datetime(pickup_date_str)
    return_date = parse_datetime(return_date_str)
    
    if not pickup_date or not return_date:
        return Response({'error': 'Invalid date format. Use ISO format.'},
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Ensure datetimes are timezone-aware
    if timezone.is_naive(pickup_date):
        pickup_date = timezone.make_aware(pickup_date, timezone.get_current_timezone())
    if timezone.is_naive(return_date):
        return_date = timezone.make_aware(return_date, timezone.get_current_timezone())
    
    # Check for conflicting bookings (excluding cancelled/completed bookings)
    conflicting_bookings = Booking.objects.filter(
        vehicle_id=vehicle_id,
        status__in=['PENDING', 'CONFIRMED', 'ACTIVE']
    ).filter(
        pickup_date__lt=return_date,
        return_date__gt=pickup_date
    )
    
    is_available = not conflicting_bookings.exists()
    
    if is_available:
        return Response({'available': True})
    else:
        # Get the earliest conflicting booking's return date
        earliest_conflict = conflicting_bookings.order_by('return_date').first()
        return Response({
            'available': False,
            'message': 'This vehicle is not available for the selected dates.',
            'next_available_date': earliest_conflict.return_date if earliest_conflict else None
        })
