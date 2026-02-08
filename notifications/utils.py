"""
Utility functions for notifications.
"""
from django.core.mail import send_mail
from django.conf import settings
import traceback


def send_booking_email_notification(booking, admin_email):
    """
    Send email notification to admin when a new booking is made.
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
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@luxedrive.com',
            recipient_list=[admin_email],
            fail_silently=False,
        )
        print(f"SUCCESS: Email sent to: {admin_email}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False


def send_booking_whatsapp_notification(booking, admin_phone):
    """
    Send WhatsApp notification to admin using Twilio.
    Requires: pip install twilio
    """
    if not hasattr(settings, 'TWILIO_ACCOUNT_SID') or not settings.TWILIO_ACCOUNT_SID:
        print("Twilio not configured, skipping WhatsApp notification")
        return False
    
    try:
        from twilio.rest import Client
        from twilio.http.http_client import TwilioHTTPClient
        
        # Custom HTTP client with SSL handling
        class CustomHTTPClient(TwilioHTTPClient):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.session.verify = False  # Disable SSL verification
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID, 
            settings.TWILIO_AUTH_TOKEN,
            http_client=CustomHTTPClient()
        )
        
        booking_url = f"{getattr(settings, 'FRONTEND_URL', None) or 'http://localhost:5173'}/#/admin/bookings"
        
        message_body = f"""
        🚗 *New Booking - LuxeDrive*
        
        Ref: {booking.booking_reference}
        Customer: {booking.driver_name}
        Phone: {booking.driver_phone}
        Vehicle: #{booking.vehicle_id}
        Dates: {booking.pickup_date} to {booking.return_date}
        Total: ${booking.total_price}
        
        View: {booking_url}
        """
        
        message = client.messages.create(
            from_='whatsapp:+14155238886',  # Twilio sandbox number
            to=f'whatsapp:{admin_phone}',
            body=message_body
        )
        
        print(f"WhatsApp sent: {message.sid}")
        return True
        
    except ImportError:
        print("Twilio not installed. Run: pip install twilio")
        return False
    except Exception as e:
        print(f"Failed to send WhatsApp: {e}")
        return False
