import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from sqlalchemy.orm import Session
from backend.models.models import NotificationRecord, Parent, Resident
from backend.config import settings

def send_parent_notification(
    db: Session,
    hosteler_id: int,
    event_type: str,
    message_text: str
):
    """
    Triggers configured Email and/or WhatsApp notifications to the resident's parent.
    Stores notification audit status in notification_records table.
    """
    resident = db.query(Resident).filter(Resident.id == hosteler_id).first()
    if not resident:
        return

    parents = db.query(Parent).filter(Parent.hosteler_id == hosteler_id).all()
    if not parents:
        print(f"[Notification] No parent records found for resident ID {hosteler_id}.")
        return

    for parent in parents:
        pref = parent.notification_preference.lower() if parent.notification_preference else "both"

        # Email notification
        if pref in ["email", "both"]:
            if parent.email:
                send_email_notification(
                    db=db,
                    hosteler_id=hosteler_id,
                    recipient=parent.email,
                    event_type=event_type,
                    message_text=message_text
                )

        # WhatsApp notification
        if pref in ["whatsapp", "both"]:
            phone = parent.whatsapp_number or parent.phone
            if phone:
                send_whatsapp_notification(
                    db=db,
                    hosteler_id=hosteler_id,
                    recipient=phone,
                    event_type=event_type,
                    message_text=message_text
                )

def send_email_notification(db: Session, hosteler_id: int, recipient: str, event_type: str, message_text: str):
    """Sends email via SMTP or logs if credentials not provided."""
    status = "SENT"
    err_msg = None

    if settings.ENABLE_EMAIL and settings.EMAIL_USER and settings.EMAIL_PASSWORD:
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_FROM or settings.EMAIL_USER
            msg['To'] = recipient
            msg['Subject'] = f"Hostel Notification: {event_type.replace('_', ' ').title()}"

            msg.attach(MIMEText(message_text, 'plain'))

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
                server.send_message(msg)
            print(f"[Email Service] Email sent successfully to {recipient}")
        except Exception as e:
            status = "FAILED"
            err_msg = str(e)
            print(f"[Email Service] Failed to send email to {recipient}: {e}")
    else:
        # Development / Fallback mode logging
        print(f"[Email Service (MOCK SENT)] To: {recipient} | Subject: {event_type} | Body: {message_text}")
        status = "SENT"

    # Log record
    record = NotificationRecord(
        hosteler_id=hosteler_id,
        event_type=event_type,
        channel="EMAIL",
        recipient=recipient,
        message=message_text,
        status=status,
        error_message=err_msg
    )
    db.add(record)
    db.commit()

def send_whatsapp_notification(db: Session, hosteler_id: int, recipient: str, event_type: str, message_text: str):
    """Sends WhatsApp message via Meta Graph API / Provider endpoint or logs fallback."""
    status = "SENT"
    err_msg = None

    if settings.ENABLE_WHATSAPP and settings.WHATSAPP_API_URL and settings.WHATSAPP_API_TOKEN:
        try:
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient,
                "type": "text",
                "text": {"body": message_text}
            }
            response = requests.post(settings.WHATSAPP_API_URL, json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201]:
                print(f"[WhatsApp Service] WhatsApp message sent to {recipient}")
            else:
                status = "FAILED"
                err_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"[WhatsApp Service] Failed: {err_msg}")
        except Exception as e:
            status = "FAILED"
            err_msg = str(e)
            print(f"[WhatsApp Service] Exception sending WhatsApp to {recipient}: {e}")
    else:
        # Development / Fallback mode logging
        print(f"[WhatsApp Service (MOCK SENT)] To: {recipient} | Message: {message_text}")
        status = "SENT"

    record = NotificationRecord(
        hosteler_id=hosteler_id,
        event_type=event_type,
        channel="WHATSAPP",
        recipient=recipient,
        message=message_text,
        status=status,
        error_message=err_msg
    )
    db.add(record)
    db.commit()
