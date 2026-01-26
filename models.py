from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Base user model for both patients and caretakers"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    google_id = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20), nullable=False)  # 'patient' or 'caretaker'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    caretaker_profile = db.relationship('Caretaker', backref='user', uselist=False, cascade='all, delete-orphan')


class Patient(db.Model):
    """Patient-specific information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretaker.id'))
    age = db.Column(db.Integer)
    address = db.Column(db.String(300))
    medical_conditions = db.Column(db.Text)
    emergency_contact = db.Column(db.String(20))
    
    # Relationships
    medicines = db.relationship('Medicine', backref='patient', lazy=True, cascade='all, delete-orphan')
    medicine_logs = db.relationship('MedicineLog', backref='patient', lazy=True, cascade='all, delete-orphan')
    emergency_alerts = db.relationship('EmergencyAlert', backref='patient', lazy=True, cascade='all, delete-orphan')
    reorder_requests = db.relationship('ReorderRequest', backref='patient', lazy=True, cascade='all, delete-orphan')


class Caretaker(db.Model):
    """Caretaker-specific information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    specialization = db.Column(db.String(100))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    
    # Relationships
    patients = db.relationship('Patient', backref='caretaker', lazy=True)


class Doctor(db.Model):
    """Doctor information for consultation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    specialization = db.Column(db.String(100))
    hospital = db.Column(db.String(200))
    
    # Relationships
    caretakers = db.relationship('Caretaker', backref='doctor', lazy=True)
    consultations = db.relationship('Consultation', backref='doctor', lazy=True)


class Medicine(db.Model):
    """Medicine information for patients"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    frequency = db.Column(db.String(50), nullable=False)  # e.g., "3 times daily"
    time_slots = db.Column(db.String(200))  # JSON string: ["08:00", "14:00", "20:00"]
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    quantity_remaining = db.Column(db.Integer, default=30)
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MedicineLog(db.Model):
    """Track when medicines are taken"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    taken_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')  # pending, taken, missed, skipped
    reminder_count = db.Column(db.Integer, default=0)
    caretaker_notified = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    
    # Relationship
    medicine = db.relationship('Medicine', backref='logs')


class EmergencyAlert(db.Model):
    """Emergency help requests from patients"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretaker.id'))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')  # active, acknowledged, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime)


class ReorderRequest(db.Model):
    """Medicine reorder requests"""
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretaker.id'))
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, ordered, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ordered_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Relationship
    medicine = db.relationship('Medicine', backref='reorder_requests')


class Consultation(db.Model):
    """Doctor consultations for caretakers"""
    id = db.Column(db.Integer, primary_key=True)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretaker.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, answered, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime)


class MedicalShopOrder(db.Model):
    """Orders placed to medical shops"""
    id = db.Column(db.Integer, primary_key=True)
    caretaker_id = db.Column(db.Integer, db.ForeignKey('caretaker.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    shop_name = db.Column(db.String(150))
    shop_phone = db.Column(db.String(20))
    items = db.Column(db.Text)  # JSON string of items
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, delivered
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime)
