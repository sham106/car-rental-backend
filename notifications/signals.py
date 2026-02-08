from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings
from notifications.models import Notification
from bookings.models import Booking
from notifications.utils import send_booking_email_notification, send_booking_whatsapp_notification
import traceback

User = get_user_model()


def send_booking_notification(booking: Booking):
    """
    Send notification when a new booking is created.
    - Creates in-app notification for primary admin user
    - Sends email to ADMIN_EMAIL address
    """
    
    try:
        # In-app notification - uses admin user email from database
        inapp_admin_email = settings.INAPP_ADMIN_EMAIL if hasattr(settings, 'INAPP_ADMIN_EMAIL') else None
        
        # Email notification - uses ADMIN_EMAIL (can be different)
        admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else 'admin@luxedrive.com'
        admin_phone = settings.ADMIN_PHONE if hasattr(settings, 'ADMIN_PHONE') else None
        
        # Get the admin user for in-app notification
        admin_user = None
        if inapp_admin_email:
            admin_user = User.objects.filter(is_staff=True, email=inapp_admin_email, is_active=True).first()
        
        # Fallback: If specific admin not found, try to find any superuser
        if not admin_user:
            admin_user = User.objects.filter(is_superuser=True, is_active=True).first()
        
        # If no specific in-app admin found, skip in-app notification
        booking_url = f"{getattr(settings, 'FRONTEND_URL', None) or 'http://localhost:5173'}/#/admin/bookings"
        
        # Check for existing notifications for this booking to prevent duplicates
        if booking.booking_reference:
            existing_notifications = Notification.objects.filter(
                notification_type='BOOKING_NEW',
                link__icontains=str(booking.booking_reference)
            )
            
            if existing_notifications.exists():
                print(f"Notification already exists for booking {booking.booking_reference}, skipping")
                return
        
        # 1. Create in-app notification for primary admin only
        if admin_user:
            Notification.objects.create(
                user=admin_user,
                title='New Booking Received',
                message=f"New booking #{booking.booking_reference} from {booking.driver_name}. "
                       f"Vehicle: {booking.vehicle_id}, Dates: {booking.pickup_date} to {booking.return_date}. "
                       f"Total: ${booking.total_price}",
                notification_type='BOOKING_NEW',
                priority='HIGH',
                link=booking_url
            )
            print(f"In-app notification created for {inapp_admin_email}")
        else:
            print(f"In-app admin user not found ({inapp_admin_email}), skipping in-app notification")
        
        # 2. Send email to ADMIN_EMAIL (separate from in-app notification)
        send_booking_email_notification(booking, admin_email)
        
        # 3. Send WhatsApp notification (using Twilio or similar)
        if admin_phone:
            send_booking_whatsapp_notification(booking, admin_phone)
        
        print(f"Notification sent for booking {booking.booking_reference}")
        
    except Exception as e:
        print(f"CRITICAL ERROR: Failed to send booking notification: {e}")
        traceback.print_exc()


@receiver(post_save, sender=Booking)
def booking_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler that triggers when a booking is created.
    """
    if created:
        send_booking_notification(instance)
