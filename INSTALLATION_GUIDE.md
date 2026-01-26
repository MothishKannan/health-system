# Healthcare Management System - Installation Guide

## 📦 Prerequisites
1. Python 3.8 or higher installed
2. VS Code installed
3. Git installed (optional)

## 🔧 Step 1: Install Required Packages

Open your terminal/command prompt in VS Code and run these commands:

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all required packages
pip install flask
pip install flask-sqlalchemy
pip install flask-login
pip install flask-mail
pip install google-auth
pip install google-auth-oauthlib
pip install google-auth-httplib2
pip install twilio
pip install python-dotenv
pip install apscheduler
pip install werkzeug
```

## 📱 Step 2: Get API Keys & Services

### 1. Google OAuth (for login)
- Go to: https://console.cloud.google.com/
- Create a new project
- Enable Google+ API
- Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
- Application type: Web application
- Authorized redirect URIs: `http://localhost:5000/callback`
- Copy your CLIENT_ID and CLIENT_SECRET

### 2. Twilio (for SMS)
- Sign up at: https://www.twilio.com/try-twilio
- Get your Account SID and Auth Token
- Get a Twilio phone number

### 3. Email Service (Gmail SMTP)
- Use your Gmail account
- Enable "Less secure app access" OR use App Password
- App Password: https://myaccount.google.com/apppasswords

## 📁 Step 3: Project Structure

Create these folders in VS Code:
```
healthcare-system/
│
├── app.py                    (Main Flask application)
├── config.py                 (Configuration)
├── models.py                 (Database models)
├── .env                      (Environment variables - API keys)
├── requirements.txt          (Package list)
│
├── templates/                (HTML files)
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── patient_dashboard.html
│   ├── caretaker_dashboard.html
│   └── ...
│
├── static/                   (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── instance/                 (Database - auto-created)
    └── healthcare.db
```

## 🔐 Step 4: Create .env File

Create a file named `.env` in your project root:

```env
# Flask
SECRET_KEY=your-super-secret-key-here-change-this
FLASK_ENV=development

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here

# Twilio (SMS)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-phone-number

# Email (Gmail)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password-here

# Database
DATABASE_URL=sqlite:///healthcare.db
```

## 🚀 Step 5: Run the Application

```bash
# Make sure you're in the project directory
cd healthcare-system

# Activate virtual environment (if not already)
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Run the application
python app.py
```

Your website will be available at: `http://localhost:5000`

## 🌐 Step 6: Free Hosting Options

### Option 1: Render.com (Recommended - Free)
1. Sign up at https://render.com
2. Connect your GitHub repository
3. Create a new "Web Service"
4. Add environment variables from .env
5. Deploy!

### Option 2: PythonAnywhere (Free tier available)
1. Sign up at https://www.pythonanywhere.com
2. Upload your code
3. Configure web app
4. Add environment variables

### Option 3: Railway.app (Free tier)
1. Sign up at https://railway.app
2. Deploy from GitHub
3. Add environment variables

### Option 4: Heroku (Limited free tier)
1. Sign up at https://www.heroku.com
2. Install Heroku CLI
3. Deploy via Git

## ⚠️ Important Notes

1. **Security**: Never commit your `.env` file to GitHub!
2. **Database**: SQLite is for development. For production, use PostgreSQL
3. **HTTPS**: Production websites need HTTPS for Google OAuth
4. **Phone Numbers**: Test SMS with your own number first
5. **Email Limits**: Gmail has daily sending limits

## 🐛 Troubleshooting

**Issue**: Google OAuth not working
- **Solution**: Check redirect URI matches exactly

**Issue**: SMS not sending
- **Solution**: Verify Twilio account is active and phone number verified

**Issue**: Emails going to spam
- **Solution**: Use proper SMTP settings and SPF/DKIM records

## 📞 Next Steps

I'll now create all the code files for you:
1. app.py - Main application
2. models.py - Database models
3. config.py - Configuration
4. All HTML templates
5. CSS and JavaScript files
6. Helper functions for reminders and notifications

Ready to proceed?
