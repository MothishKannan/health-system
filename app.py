from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import json
import os

from config import Config
from models import db, User, Patient, Caretaker, Doctor, Medicine, MedicineLog, EmergencyAlert, ReorderRequest, Consultation, MedicalShopOrder
from notifications import send_email, send_sms, check_medicine_reminders

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize scheduler for automatic reminders
scheduler = BackgroundScheduler()
scheduler.add_job(func=lambda: check_medicine_reminders(app), trigger="interval", minutes=5)
scheduler.start()


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')


@app.route('/auth/google', methods=['POST'])
def google_auth():
    """Handle Google OAuth login"""
    try:
        token = request.json.get('credential')
        user_type = request.json.get('user_type')  # 'patient' or 'caretaker'
        
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            app.config['GOOGLE_CLIENT_ID']
        )
        
        # Get user info
        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')
        
        # Check if user exists
        user = User.query.filter_by(google_id=google_id).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                user_type=user_type
            )
            db.session.add(user)
            db.session.commit()
            
            # Create profile based on user type
            if user_type == 'patient':
                patient = Patient(user_id=user.id)
                db.session.add(patient)
            else:
                caretaker = Caretaker(user_id=user.id)
                db.session.add(caretaker)
            
            db.session.commit()
        
        # Log the user in
        login_user(user)
        
        # Redirect based on user type
        if user.user_type == 'patient':
            return jsonify({'success': True, 'redirect': url_for('patient_dashboard')})
        else:
            return jsonify({'success': True, 'redirect': url_for('caretaker_dashboard')})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


# ==================== PATIENT ROUTES ====================

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    """Patient dashboard"""
    if current_user.user_type != 'patient':
        flash('Access denied. Patients only.', 'danger')
        return redirect(url_for('index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    medicines = Medicine.query.filter_by(patient_id=patient.id, is_active=True).all()
    
    # Get today's medicine schedule
    today = datetime.now().date()
    medicine_logs = MedicineLog.query.filter(
        MedicineLog.patient_id == patient.id,
        db.func.date(MedicineLog.scheduled_time) == today
    ).order_by(MedicineLog.scheduled_time).all()
    
    return render_template('patient_dashboard.html', 
                         patient=patient, 
                         medicines=medicines,
                         medicine_logs=medicine_logs)


@app.route('/patient/profile', methods=['GET', 'POST'])
@login_required
def patient_profile():
    """Patient profile management"""
    if current_user.user_type != 'patient':
        return redirect(url_for('index'))
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update profile
        current_user.phone = request.form.get('phone')
        patient.age = request.form.get('age')
        patient.address = request.form.get('address')
        patient.medical_conditions = request.form.get('medical_conditions')
        patient.emergency_contact = request.form.get('emergency_contact')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('patient_profile.html', patient=patient)


@app.route('/patient/medicine/<int:log_id>/taken', methods=['POST'])
@login_required
def mark_medicine_taken(log_id):
    """Mark medicine as taken"""
    if current_user.user_type != 'patient':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    log = MedicineLog.query.get_or_404(log_id)
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if log.patient_id != patient.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Update log
    log.taken_time = datetime.now()
    log.status = 'taken'
    
    # Update medicine quantity
    medicine = Medicine.query.get(log.medicine_id)
    if medicine.quantity_remaining > 0:
        medicine.quantity_remaining -= 1
    
    db.session.commit()
    
    # Check if quantity is low and send notification
    if medicine.quantity_remaining <= 5:
        if patient.caretaker:
            caretaker_user = User.query.get(patient.caretaker.user_id)
            send_email(
                caretaker_user.email,
                f'Low Medicine Stock Alert - {medicine.name}',
                f'Patient {current_user.name} has only {medicine.quantity_remaining} {medicine.name} remaining.'
            )
    
    return jsonify({'success': True, 'message': 'Medicine marked as taken!'})


@app.route('/patient/emergency', methods=['POST'])
@login_required
def send_emergency_alert():
    """Send emergency help request to caretaker"""
    if current_user.user_type != 'patient':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    
    if not patient.caretaker:
        return jsonify({'success': False, 'error': 'No caretaker assigned'}), 400
    
    message = request.json.get('message', 'Emergency help needed!')
    
    # Create emergency alert
    alert = EmergencyAlert(
        patient_id=patient.id,
        caretaker_id=patient.caretaker_id,
        message=message
    )
    db.session.add(alert)
    db.session.commit()
    
    # Send notifications to caretaker
    caretaker_user = User.query.get(patient.caretaker.user_id)
    
    # Email
    send_email(
        caretaker_user.email,
        f'EMERGENCY ALERT - {current_user.name}',
        f'Emergency help request from {current_user.name}:\n\n{message}\n\nPlease respond immediately.'
    )
    
    # SMS
    if caretaker_user.phone:
        send_sms(
            caretaker_user.phone,
            f'EMERGENCY: {current_user.name} needs help! {message}'
        )
    
    return jsonify({'success': True, 'message': 'Emergency alert sent to caretaker!'})


@app.route('/patient/reorder/<int:medicine_id>', methods=['POST'])
@login_required
def request_medicine_reorder(medicine_id):
    """Request medicine reorder"""
    if current_user.user_type != 'patient':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    medicine = Medicine.query.get_or_404(medicine_id)
    
    if medicine.patient_id != patient.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    quantity = request.json.get('quantity', 30)
    
    # Create reorder request
    reorder = ReorderRequest(
        patient_id=patient.id,
        medicine_id=medicine_id,
        caretaker_id=patient.caretaker_id,
        quantity=quantity
    )
    db.session.add(reorder)
    db.session.commit()
    
    # Notify caretaker
    if patient.caretaker:
        caretaker_user = User.query.get(patient.caretaker.user_id)
        send_email(
            caretaker_user.email,
            f'Medicine Reorder Request - {medicine.name}',
            f'{current_user.name} has requested to reorder {medicine.name}.\nQuantity: {quantity}\n\nPlease arrange for refill.'
        )
    
    return jsonify({'success': True, 'message': 'Reorder request sent to caretaker!'})


# ==================== CARETAKER ROUTES ====================

@app.route('/caretaker/dashboard')
@login_required
def caretaker_dashboard():
    """Caretaker dashboard"""
    if current_user.user_type != 'caretaker':
        flash('Access denied. Caretakers only.', 'danger')
        return redirect(url_for('index'))
    
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    patients = Patient.query.filter_by(caretaker_id=caretaker.id).all()
    
    # Get emergency alerts
    emergency_alerts = EmergencyAlert.query.filter_by(
        caretaker_id=caretaker.id,
        status='active'
    ).order_by(EmergencyAlert.created_at.desc()).all()
    
    # Get reorder requests
    reorder_requests = ReorderRequest.query.filter_by(
        caretaker_id=caretaker.id,
        status='pending'
    ).order_by(ReorderRequest.created_at.desc()).all()
    
    return render_template('caretaker_dashboard.html',
                         caretaker=caretaker,
                         patients=patients,
                         emergency_alerts=emergency_alerts,
                         reorder_requests=reorder_requests)


@app.route('/caretaker/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    """Add a new patient"""
    if current_user.user_type != 'caretaker':
        return redirect(url_for('index'))
    
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    
    # Check patient limit
    patient_count = Patient.query.filter_by(caretaker_id=caretaker.id).count()
    if patient_count >= app.config['MAX_PATIENTS_PER_CARETAKER']:
        flash('You have reached the maximum limit of 7 patients.', 'warning')
        return redirect(url_for('caretaker_dashboard'))
    
    if request.method == 'POST':
        patient_email = request.form.get('patient_email')
        
        # Find patient user
        patient_user = User.query.filter_by(email=patient_email, user_type='patient').first()
        
        if not patient_user:
            flash('Patient not found. Please ensure they have registered first.', 'danger')
            return redirect(url_for('add_patient'))
        
        patient = Patient.query.filter_by(user_id=patient_user.id).first()
        
        if patient.caretaker_id:
            flash('This patient already has a caretaker assigned.', 'warning')
            return redirect(url_for('add_patient'))
        
        # Assign caretaker
        patient.caretaker_id = caretaker.id
        db.session.commit()
        
        flash(f'Patient {patient_user.name} added successfully!', 'success')
        return redirect(url_for('caretaker_dashboard'))
    
    return render_template('add_patient.html')


@app.route('/caretaker/patient/<int:patient_id>')
@login_required
def view_patient(patient_id):
    """View patient details and monitoring"""
    if current_user.user_type != 'caretaker':
        return redirect(url_for('index'))
    
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    patient = Patient.query.get_or_404(patient_id)
    
    if patient.caretaker_id != caretaker.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('caretaker_dashboard'))
    
    patient_user = User.query.get(patient.user_id)
    medicines = Medicine.query.filter_by(patient_id=patient.id, is_active=True).all()
    
    # Get medicine logs for last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    medicine_logs = MedicineLog.query.filter(
        MedicineLog.patient_id == patient.id,
        MedicineLog.scheduled_time >= week_ago
    ).order_by(MedicineLog.scheduled_time.desc()).all()
    
    return render_template('view_patient.html',
                         patient=patient,
                         patient_user=patient_user,
                         medicines=medicines,
                         medicine_logs=medicine_logs)


@app.route('/caretaker/patient/<int:patient_id>/medicine/add', methods=['GET', 'POST'])
@login_required
def add_medicine(patient_id):
    """Add medicine for a patient"""
    if current_user.user_type != 'caretaker':
        return redirect(url_for('index'))
    
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    patient = Patient.query.get_or_404(patient_id)
    
    if patient.caretaker_id != caretaker.id:
        return redirect(url_for('caretaker_dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            dosage = request.form.get('dosage')
            frequency = request.form.get('frequency')
            time_slots = request.form.get('time_slots')
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            quantity = request.form.get('quantity', 30)
            instructions = request.form.get('instructions')
            
            # Parse dates
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
            
            # Create medicine
            medicine = Medicine(
                patient_id=patient.id,
                name=name,
                dosage=dosage,
                frequency=frequency,
                time_slots=time_slots,
                start_date=start_date,
                end_date=end_date,
                quantity_remaining=int(quantity),
                instructions=instructions
            )
            db.session.add(medicine)
            db.session.commit()
            
            # Create medicine logs
            try:
                create_medicine_logs(medicine)
            except Exception as log_error:
                print(f"Error creating logs: {log_error}")
                # Continue even if log creation fails
            
            flash('Medicine added successfully!', 'success')
            return redirect(url_for('view_patient', patient_id=patient_id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding medicine: {e}")
            flash(f'Error adding medicine: {str(e)}', 'danger')
            return redirect(url_for('add_medicine', patient_id=patient_id))
    
    return render_template('add_medicine.html', patient=patient)


@app.route('/caretaker/emergency/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_emergency(alert_id):
    """Acknowledge emergency alert"""
    if current_user.user_type != 'caretaker':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    alert = EmergencyAlert.query.get_or_404(alert_id)
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    
    if alert.caretaker_id != caretaker.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    alert.status = 'acknowledged'
    alert.acknowledged_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Emergency acknowledged!'})


@app.route('/caretaker/emergency/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_emergency(alert_id):
    """Resolve emergency alert"""
    if current_user.user_type != 'caretaker':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    alert = EmergencyAlert.query.get_or_404(alert_id)
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    
    if alert.caretaker_id != caretaker.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    alert.status = 'resolved'
    alert.resolved_at = datetime.now()
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Emergency resolved!'})


@app.route('/caretaker/reorder/<int:reorder_id>/process', methods=['POST'])
@login_required
def process_reorder(reorder_id):
    """Process medicine reorder request"""
    if current_user.user_type != 'caretaker':
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    reorder = ReorderRequest.query.get_or_404(reorder_id)
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    
    if reorder.caretaker_id != caretaker.id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    action = request.json.get('action')  # 'ordered' or 'delivered'
    
    if action == 'ordered':
        reorder.status = 'ordered'
        reorder.ordered_at = datetime.now()
    elif action == 'delivered':
        reorder.status = 'delivered'
        reorder.delivered_at = datetime.now()
        
        # Update medicine quantity
        medicine = Medicine.query.get(reorder.medicine_id)
        medicine.quantity_remaining += reorder.quantity
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Reorder {action}!'})


@app.route('/caretaker/doctor/consult', methods=['GET', 'POST'])
@login_required
def consult_doctor():
    """Consult with assigned doctor"""
    if current_user.user_type != 'caretaker':
        return redirect(url_for('index'))
    
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        consultation = Consultation(
            caretaker_id=caretaker.id,
            doctor_id=caretaker.doctor_id,
            patient_id=request.form.get('patient_id') if request.form.get('patient_id') else None,
            message=request.form.get('message')
        )
        db.session.add(consultation)
        db.session.commit()
        
        # Notify doctor
        if caretaker.doctor:
            send_email(
                caretaker.doctor.email,
                f'New Consultation Request from {current_user.name}',
                f'Message: {request.form.get("message")}'
            )
        
        flash('Consultation request sent to doctor!', 'success')
        return redirect(url_for('caretaker_dashboard'))
    
    consultations = Consultation.query.filter_by(caretaker_id=caretaker.id).order_by(Consultation.created_at.desc()).all()
    patients = Patient.query.filter_by(caretaker_id=caretaker.id).all()
    
    return render_template('consult_doctor.html', 
                         consultations=consultations, 
                         patients=patients,
                         caretaker=caretaker)


@app.route('/caretaker/medical-shop/order', methods=['GET', 'POST'])
@login_required
def order_from_medical_shop():
    """Place order to medical shop"""
    if current_user.user_type != 'caretaker':
        return redirect(url_for('index'))
    
    caretaker = Caretaker.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        order = MedicalShopOrder(
            caretaker_id=caretaker.id,
            patient_id=request.form.get('patient_id') if request.form.get('patient_id') else None,
            shop_name=request.form.get('shop_name'),
            shop_phone=request.form.get('shop_phone'),
            items=request.form.get('items'),  # JSON string
            total_amount=float(request.form.get('total_amount', 0))
        )
        db.session.add(order)
        db.session.commit()
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('caretaker_dashboard'))
    
    patients = Patient.query.filter_by(caretaker_id=caretaker.id).all()
    orders = MedicalShopOrder.query.filter_by(caretaker_id=caretaker.id).order_by(MedicalShopOrder.created_at.desc()).all()
    
    return render_template('medical_shop_order.html', 
                         patients=patients,
                         orders=orders)


# ==================== HELPER FUNCTIONS ====================

def create_medicine_logs(medicine):
    """Create medicine log entries for a medicine"""
    if not medicine.time_slots:
        return
    
    try:
        time_slots = json.loads(medicine.time_slots)
    except Exception as e:
        print(f"Error parsing time slots: {medicine.time_slots}, Error: {e}")
        return
    
    today = datetime.now().date()
    
    # Create logs for next 7 days
    for day in range(7):
        schedule_date = today + timedelta(days=day)
        
        # Check if schedule date is before medicine start date
        if schedule_date < medicine.start_date:
            continue
            
        # Check if within medicine date range
        if medicine.end_date and schedule_date > medicine.end_date:
            break
        
        for time_slot in time_slots:
            try:
                hour, minute = map(int, time_slot.split(':'))
                scheduled_time = datetime.combine(schedule_date, datetime.min.time().replace(hour=hour, minute=minute))
                
                # Don't create logs for past times
                if scheduled_time > datetime.now():
                    log = MedicineLog(
                        patient_id=medicine.patient_id,
                        medicine_id=medicine.id,
                        scheduled_time=scheduled_time
                    )
                    db.session.add(log)
            except Exception as e:
                print(f"Error creating log for time slot {time_slot}: {e}")
                continue
    
    try:
        db.session.commit()
    except Exception as e:
        print(f"Error committing logs: {e}")
        db.session.rollback()


# ==================== DATABASE INITIALIZATION ====================

@app.before_request
def create_tables():
    """Create database tables before first request"""
    db.create_all()


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500


# ==================== RUN APP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)