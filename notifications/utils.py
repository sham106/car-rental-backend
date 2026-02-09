"""
Utility functions for notifications.
"""
from django.core.mail import send_mail
from django.conf import settings
import traceback
import threading


def _send_email_sync(subject, message, admin_email):
    """
    Internal synchronous email sending function.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@luxedrive.com',
            recipient_list=[admin_email],
            fail_silently=False,
        )
        print(f"SUCCESS: Email sent to: {admin_email}")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()


def send_booking_email_notification(booking, admin_email):
    """
    Send email notification to admin when a new booking is made.
    Uses async threading to avoid blocking the main request.
    """
    booking_url = f"{getattr(settings, 'FRONTEND_URL', None) or 'http://localhost:5173'}/#/admin/bookings"
    
    subject = f'🚗 New Booking #{booking.booking_reference} - LuxeDrive'
    
    message = f"""
    A new booking has been made on LuxeDrive!
    
    Booking Reference: {booking.booking_reference}
    Customer: {booking.driver_name}
    Email: {booking.driver_email}
    Phone: {booking.driver_phone}
    Vehicle ID: {booking.vehicle_id}
    Pickup Date: {booking.pickup_date}
    Return Date: {booking.return_date}
    Total Price: ${booking.total_price}
    Payment Status: {booking.payment_status}
    
    View Booking: {booking_url}
    
    Please log in to the admin dashboard to confirm or manage this booking.
    """
    
    print(f"Attempting to send email FROM: {settings.DEFAULT_FROM_EMAIL} TO: {admin_email}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    
    # Start email sending in a background thread to avoid blocking the request
    email_thread = threading.Thread(
        target=_send_email_sync,
        args=(subject, message, admin_email),
        daemon=True
    )
    email_thread.start()
    
    return True  # Return immediately, email will be sent in background
