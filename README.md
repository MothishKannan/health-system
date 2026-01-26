# 🏥 Healthcare Management System

A comprehensive web application connecting patients, caretakers, and doctors for better healthcare management.

## 🌟 Features

### For Patients
- ✅ Google OAuth login
- 💊 Medicine tracking and reminders
- 📧 Automatic email and SMS reminders
- 🆘 Emergency help button
- 🔄 Medicine refill requests
- 📊 Dashboard with medicine schedule

### For Caretakers
- ✅ Google OAuth login
- 👥 Manage up to 7 patients
- 🔔 Receive emergency alerts
- 📋 Monitor patient medicine adherence
- 💬 Consult with assigned doctor
- 🛒 Order from medical shops
- 📈 Patient activity monitoring

### System Features
- 🔐 Secure Google authentication
- 📱 Responsive design (mobile-friendly)
- 📧 Email notifications
- 💬 SMS notifications via Twilio
- 🔄 Automatic medicine reminders
- 🚨 Emergency alert system
- 📊 Complete medicine tracking

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Google OAuth 2.0
- **Email**: Flask-Mail (Gmail SMTP)
- **SMS**: Twilio
- **Frontend**: Bootstrap 5, jQuery
- **Scheduler**: APScheduler

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Google Cloud Console account
- Twilio account (for SMS)
- Gmail account (for emails)

## 🚀 Installation

### 1. Clone or Download the Project

```bash
# Navigate to your project directory
cd healthcare-system
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual credentials
```

#### Get Google OAuth Credentials:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Go to Credentials → Create OAuth 2.0 Client ID
5. Add authorized redirect URI: `http://localhost:5000/callback`
6. Copy CLIENT_ID and CLIENT_SECRET to .env

#### Get Twilio Credentials:
1. Sign up at [Twilio](https://www.twilio.com/try-twilio)
2. Get Account SID and Auth Token
3. Get a Twilio phone number
4. Add to .env

#### Gmail Configuration:
1. Use your Gmail account
2. Create an App Password at [Google Account](https://myaccount.google.com/apppasswords)
3. Add email and app password to .env

### 5. Initialize Database

```bash
python app.py
```

This will create the database tables automatically.

### 6. Run the Application

```bash
python app.py
```

Visit: `http://localhost:5000`

## 📁 Project Structure

```
healthcare-system/
│
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── models.py                   # Database models
├── notifications.py            # Email/SMS functions
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Environment variables template
│
├── templates/                  # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── patient_dashboard.html
│   ├── patient_profile.html
│   ├── caretaker_dashboard.html
│   ├── add_patient.html
│   ├── view_patient.html
│   ├── add_medicine.html
│   ├── consult_doctor.html
│   ├── medical_shop_order.html
│   ├── 404.html
│   └── 500.html
│
├── static/                     # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── instance/                   # Database (auto-created)
    └── healthcare.db
```

## 🔧 Configuration

### Medicine Reminder Settings

In `config.py`:
- `MAX_PATIENTS_PER_CARETAKER`: Maximum patients per caretaker (default: 7)
- `REMINDER_INTERVALS`: Reminder intervals in minutes (default: [15, 30])

### Reminder Logic

1. **First Reminder**: 15 minutes after scheduled time (Email + SMS)
2. **Second Reminder**: 30 minutes after scheduled time (Email + SMS)
3. **Caretaker Alert**: 45 minutes after scheduled time if not taken

## 📱 Usage Guide

### For Patients

1. **Login**: Click "Login" → Choose "Patient Login" → Sign in with Google
2. **Update Profile**: Add phone number, age, address, medical conditions
3. **View Medicine Schedule**: Check today's medicines on dashboard
4. **Mark Medicine Taken**: Click "Mark Taken" after taking medicine
5. **Emergency Help**: Click red emergency button for immediate caretaker alert
6. **Request Refill**: Click "Request Refill" when medicine is low

### For Caretakers

1. **Login**: Click "Login" → Choose "Caretaker Login" → Sign in with Google
2. **Add Patient**: Enter patient's email (they must register first)
3. **Add Medicine**: Set medicine name, dosage, frequency, schedule
4. **Monitor Patients**: View patient activity and medicine adherence
5. **Handle Alerts**: Respond to emergency alerts and reorder requests
6. **Consult Doctor**: Send consultation requests to assigned doctor
7. **Order Medicines**: Place orders with medical shops

## 🌐 Deployment

### Free Hosting Options

#### 1. Render.com (Recommended)
```bash
# 1. Push code to GitHub
# 2. Connect repository to Render
# 3. Add environment variables
# 4. Deploy
```

#### 2. PythonAnywhere
```bash
# 1. Upload files
# 2. Set up virtual environment
# 3. Configure web app
# 4. Add environment variables
```

#### 3. Railway.app
```bash
# 1. Connect GitHub repository
# 2. Add environment variables
# 3. Deploy
```

### Production Considerations

1. **Database**: Switch to PostgreSQL for production
   ```python
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

2. **HTTPS**: Required for Google OAuth in production

3. **Security**:
   - Use strong SECRET_KEY
   - Never commit .env file
   - Enable HTTPS
   - Use secure session cookies

4. **Performance**:
   - Use production WSGI server (Gunicorn)
   - Enable caching
   - Optimize database queries

## 🐛 Troubleshooting

### Google OAuth Not Working
- Check redirect URI matches exactly
- Ensure Google+ API is enabled
- Verify credentials in .env

### SMS Not Sending
- Verify Twilio account is active
- Check phone numbers are verified
- Ensure proper Twilio credentials

### Emails Going to Spam
- Use proper SMTP settings
- Consider using SendGrid or Mailgun for production

### Database Errors
- Delete `instance/healthcare.db` and restart
- Check SQLAlchemy configuration

## 🔒 Security

- All passwords are hashed
- Google OAuth for secure authentication
- Environment variables for sensitive data
- CSRF protection enabled
- SQL injection prevention via ORM

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review the code comments
- Contact the development team

## 🎯 Future Enhancements

- [ ] Video consultation feature
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Medicine barcode scanner
- [ ] Prescription image upload
- [ ] Health metrics tracking
- [ ] Insurance integration
- [ ] Pharmacy API integration

## 📊 Database Schema

### Users
- id, email, name, google_id, phone, user_type, created_at

### Patients
- id, user_id, caretaker_id, age, address, medical_conditions, emergency_contact

### Caretakers
- id, user_id, specialization, doctor_id

### Medicines
- id, patient_id, name, dosage, frequency, time_slots, start_date, end_date, quantity_remaining, instructions

### Medicine Logs
- id, patient_id, medicine_id, scheduled_time, taken_time, status, reminder_count

### Emergency Alerts
- id, patient_id, caretaker_id, message, status, created_at

### Reorder Requests
- id, patient_id, medicine_id, caretaker_id, quantity, status

---

Made with ❤️ for better healthcare management
