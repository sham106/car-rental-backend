from rest_framework import generics, permissions, serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from bookings.models import Booking

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    license_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'license_number', 'membership_tier', 'points', 'date_joined', 'is_staff', 'license_image_url')
    
    def get_license_image_url(self, obj):
        return getattr(obj, 'license_image_url', None)

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for public customer registration.
    Staff/Admin status is intentionally omitted for security.
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    """
    Public endpoint for customer registration.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    
    def validate(self, attrs):
        # Add username field that equals email (both point to same value)
        # The parent will use attrs['email'] for authentication
        attrs['username'] = attrs.get('email', '')
        return super().validate(attrs)

class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer

class UserProfileView(generics.RetrieveAPIView):
    """
    Returns the profile of the currently authenticated user.
    Used by the frontend to determine if a user is staff.
    Includes the latest license image from bookings.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        # Get the latest license image from user's bookings
        latest_booking_with_license = Booking.objects.filter(
            user=user, 
            license_image__isnull=False
        ).order_by('-created_at').first()
        
        license_image_url = None
        if latest_booking_with_license and latest_booking_with_license.license_image:
            license_image_url = latest_booking_with_license.license_image.url
        
        # Add license_image to the user object temporarily
        user.license_image_url = license_image_url
        return user

class UserListView(generics.ListAPIView):
    """
    Admin endpoint to list all users (customers).
    """
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

class UserDetailView(generics.RetrieveAPIView):
    """
    Admin endpoint to get user details with their bookings.
    """
    queryset = User.objects.filter(is_staff=False)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        bookings = Booking.objects.filter(user=instance).order_by('-created_at')
        booking_data = []
        for booking in bookings:
            booking_data.append({
                'id': booking.id,
                'booking_reference': booking.booking_reference,
                'vehicle_id': booking.vehicle_id,
                'pickup_date': booking.pickup_date,
                'return_date': booking.return_date,
                'driver_name': booking.driver_name,
                'driver_email': booking.driver_email,
                'driver_phone': booking.driver_phone,
                'license_number': booking.license_number,
                'license_image': booking.license_image.url if booking.license_image else None,
                'total_price': float(booking.total_price),
                'status': booking.status,
                'payment_status': booking.payment_status,
                'created_at': booking.created_at,
            })
        
        data = {
            'user': UserSerializer(instance).data,
            'bookings': booking_data,
            'total_bookings': bookings.count(),
            'total_spent': sum(float(b.total_price) for b in bookings),
        }
        return Response(data)
