from flask_mail import Mail, Message
from twilio.rest import Client
from datetime import datetime, timedelta
from models import MedicineLog, Patient, User, Medicine
import os

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app"""
    mail.init_app(app)


def send_email(to_email, subject, body):
    """Send email notification"""
    try:
        msg = Message(
            subject=subject,
            recipients=[to_email],
            body=body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def send_sms(to_phone, message):
    """Send SMS notification via Twilio"""
    try:
        account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        from_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_phone]):
            print("Twilio credentials not configured")
            return False
        
        client = Client(account_sid, auth_token)
        
        message = client.messages.create(
            body=message,
            from_=from_phone,
            to=to_phone
        )
        
        return True
    except Exception as e:
        print(f"SMS error: {e}")
        return False


def check_medicine_reminders(app):
    """
    Background job to check for medicine reminders
    This runs every 5 minutes to check if patients need reminders
    """
    with app.app_context():
        from models import db
        
        now = datetime.now()
        
        # Get all pending medicine logs that are due now (within 5 minutes window)
        pending_logs = MedicineLog.query.filter(
            MedicineLog.status == 'pending',
            MedicineLog.scheduled_time <= now,
            MedicineLog.scheduled_time >= now - timedelta(minutes=5)
        ).all()
        
        for log in pending_logs:
            time_since_scheduled = (now - log.scheduled_time).total_seconds() / 60
            
            # First reminder after 15 minutes
            if time_since_scheduled >= 15 and log.reminder_count == 0:
                send_first_reminder(log)
                log.reminder_count = 1
                db.session.commit()
            
            # Second reminder after 30 minutes
            elif time_since_scheduled >= 30 and log.reminder_count == 1:
                send_second_reminder(log)
                log.reminder_count = 2
                db.session.commit()
            
            # Notify caretaker after 45 minutes if still not taken
            elif time_since_scheduled >= 45 and log.reminder_count == 2 and not log.caretaker_notified:
                notify_caretaker(log)
                log.caretaker_notified = True
                log.status = 'missed'
                db.session.commit()


def send_first_reminder(log):
    """Send first reminder to patient"""
    patient = Patient.query.get(log.patient_id)
    user = User.query.get(patient.user_id)
    medicine = Medicine.query.get(log.medicine_id)
    
    # Email reminder
    subject = f"Medicine Reminder - {medicine.name}"
    body = f"""
    Hi {user.name},
    
    This is a reminder to take your medicine:
    
    Medicine: {medicine.name}
    Dosage: {medicine.dosage}
    Scheduled Time: {log.scheduled_time.strftime('%I:%M %p')}
    
    Please take your medicine and mark it as taken in your dashboard.
    
    Best regards,
    Healthcare Management System
    """
    send_email(user.email, subject, body)
    
    # SMS reminder
    if user.phone:
        sms_message = f"Reminder: Take {medicine.name} ({medicine.dosage}) now. Scheduled at {log.scheduled_time.strftime('%I:%M %p')}"
        send_sms(user.phone, sms_message)


def send_second_reminder(log):
    """Send second reminder to patient"""
    patient = Patient.query.get(log.patient_id)
    user = User.query.get(patient.user_id)
    medicine = Medicine.query.get(log.medicine_id)
    
    # Email reminder
    subject = f"URGENT: Medicine Reminder - {medicine.name}"
    body = f"""
    Hi {user.name},
    
    This is your SECOND reminder to take your medicine:
    
    Medicine: {medicine.name}
    Dosage: {medicine.dosage}
    Scheduled Time: {log.scheduled_time.strftime('%I:%M %p')}
    You are 30 minutes late!
    
    Please take your medicine immediately and mark it as taken.
    If you don't take it soon, your caretaker will be notified.
    
    Best regards,
    Healthcare Management System
    """
    send_email(user.email, subject, body)
    
    # SMS reminder
    if user.phone:
        sms_message = f"URGENT: Take {medicine.name} NOW! You're 30 min late. Caretaker will be notified if not taken soon."
        send_sms(user.phone, sms_message)


def notify_caretaker(log):
    """Notify caretaker when patient misses medicine"""
    patient = Patient.query.get(log.patient_id)
    patient_user = User.query.get(patient.user_id)
    medicine = Medicine.query.get(log.medicine_id)
    
    if not patient.caretaker:
        return
    
    caretaker_user = User.query.get(patient.caretaker.user_id)
    
    # Email to caretaker
    subject = f"ALERT: Patient {patient_user.name} Missed Medicine"
    body = f"""
    ATTENTION,
    
    Patient {patient_user.name} has not taken their medicine after 2 reminders:
    
    Medicine: {medicine.name}
    Dosage: {medicine.dosage}
    Scheduled Time: {log.scheduled_time.strftime('%I:%M %p')}
    Time Elapsed: 45+ minutes
    
    Please contact the patient immediately to ensure they take their medicine.
    
    Patient Contact:
    Phone: {patient_user.phone or 'Not provided'}
    Email: {patient_user.email}
    
    Best regards,
    Healthcare Management System
    """
    send_email(caretaker_user.email, subject, body)
    
    # SMS to caretaker
    if caretaker_user.phone:
        sms_message = f"ALERT: {patient_user.name} missed {medicine.name} at {log.scheduled_time.strftime('%I:%M %p')}. Please contact them!"
        send_sms(caretaker_user.phone, sms_message)


def send_low_stock_alert(medicine, patient):
    """Alert when medicine stock is low"""
    patient_user = User.query.get(patient.user_id)
    
    # Email to patient
    subject = f"Low Medicine Stock - {medicine.name}"
    body = f"""
    Hi {patient_user.name},
    
    Your medicine stock is running low:
    
    Medicine: {medicine.name}
    Remaining Quantity: {medicine.quantity_remaining}
    
    Please request a refill from your caretaker soon to avoid running out.
    
    Best regards,
    Healthcare Management System
    """
    send_email(patient_user.email, subject, body)
    
    # Also notify caretaker if assigned
    if patient.caretaker:
        caretaker_user = User.query.get(patient.caretaker.user_id)
        subject = f"Low Stock Alert - {patient_user.name}"
        body = f"""
        Patient {patient_user.name} has low stock of {medicine.name}.
        
        Remaining: {medicine.quantity_remaining}
        
        Please arrange for refill.
        """
        send_email(caretaker_user.email, subject, body)
