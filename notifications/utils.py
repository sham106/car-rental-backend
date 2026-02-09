"""
Utility functions for notifications.
"""
from django.conf import settings
import traceback
import threading


def _send_email_sync(subject, message_content, admin_email):
    """
    Internal synchronous email sending function using SendGrid HTTP API.
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        sg_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        if not sg_api_key:
            print("ERROR: SENDGRID_API_KEY not configured")
            return False
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@luxedrive.com')
        
        # Create the email message
        mail = Mail(
            from_email=from_email,
            to_emails=admin_email,
            subject=subject,
            html_content=message_content
        )
        
        # Send using SendGrid API
        sg = SendGridAPIClient(api_key=sg_api_key)
        response = sg.send(mail)
        
        print(f"SUCCESS: Email sent to: {admin_email}, Status code: {response.status_code}")
        return True
        
    except ImportError:
        print("ERROR: sendgrid library not installed. Run: pip install sendgrid")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False


def send_booking_email_notification(booking, admin_email):
    """
    Send email notification to admin when a new booking is made.
    Uses async threading to avoid blocking the main request.
    """
    booking_url = f"{getattr(settings, 'FRONTEND_URL', None) or 'http://localhost:5173'}/#/admin/bookings"
    
    subject = f'🚗 New Booking #{booking.booking_reference} - LuxeDrive'
    
    # HTML formatted message
    message_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #333;">New Booking Received!</h2>
        <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Booking Reference:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.booking_reference}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Customer:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.driver_name}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Email:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.driver_email}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Phone:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.driver_phone}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Vehicle ID:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.vehicle_id}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Pickup Date:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.pickup_date}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Return Date:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.return_date}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Total Price:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">${booking.total_price}</td></tr>
            <tr><td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Payment Status:</strong></td><td style="padding: 10px; border-bottom: 1px solid #ddd;">{booking.payment_status}</td></tr>
        </table>
        <p style="margin-top: 20px;">
            <a href="{booking_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Booking in Admin Dashboard</a>
        </p>
    </body>
    </html>
    """
    
    print(f"Attempting to send email via SendGrid API TO: {admin_email}")
    
    # Start email sending in a background thread to avoid blocking the request
    email_thread = threading.Thread(
        target=_send_email_sync,
        args=(subject, message_html, admin_email),
        daemon=True
    )
    email_thread.start()
    
    return True  # Return immediately, email will be sent in background
