# 🚀 QUICK START GUIDE - Healthcare Management System

## ⚡ FASTEST WAY TO GET STARTED

### Windows Users:
```cmd
1. Double-click: setup.bat
2. Edit .env file with your API keys
3. Double-click: start.bat
4. Open browser: http://localhost:5000
```

### Mac/Linux Users:
```bash
1. Run: ./setup.sh
2. Edit .env file with your API keys
3. Run: ./start.sh
4. Open browser: http://localhost:5000
```

## 📝 REQUIRED SETUP (5 Minutes)

### 1. Google OAuth (Required for Login)
- Go to: https://console.cloud.google.com/
- Create new project
- Enable "Google+ API"
- Create OAuth 2.0 credentials
- Add redirect URI: `http://localhost:5000/callback`
- Copy CLIENT_ID and CLIENT_SECRET to .env file

### 2. Email Setup (Gmail - Required)
- Go to: https://myaccount.google.com/apppasswords
- Create an app password
- Add your email and app password to .env file

### 3. SMS Setup (Twilio - Optional but Recommended)
- Sign up: https://www.twilio.com/try-twilio
- Get free trial credits
- Copy Account SID, Auth Token, and Phone Number to .env

## 📂 WHAT'S IN THE PACKAGE?

```
healthcare-system/
├── app.py                      ⭐ Main application
├── config.py                   ⚙️ Settings
├── models.py                   📊 Database models
├── notifications.py            📧 Email & SMS
├── requirements.txt            📦 Dependencies
├── .env.example               🔐 Config template
├── setup.bat / setup.sh       🛠️ Auto setup
├── start.bat / start.sh       ▶️ Run app
├── templates/                  📄 HTML pages (11 files)
├── static/                     🎨 CSS & JS
└── README.md                   📖 Full documentation
```

## 🎯 FEATURES CHECKLIST

### Patient Features:
- ✅ Google login
- ✅ Medicine tracking dashboard
- ✅ Automatic reminders (email + SMS)
- ✅ Emergency help button
- ✅ Medicine refill requests
- ✅ Profile management

### Caretaker Features:
- ✅ Manage up to 7 patients
- ✅ Add medicines with schedules
- ✅ Receive emergency alerts
- ✅ View patient activity
- ✅ Consult with doctor
- ✅ Order from medical shops

## 🔧 TROUBLESHOOTING

### Can't login with Google?
- Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
- Verify redirect URI: http://localhost:5000/callback
- Make sure Google+ API is enabled

### Emails not sending?
- Check MAIL_USERNAME and MAIL_PASSWORD in .env
- Use Gmail App Password, not regular password
- Allow less secure apps OR use app password

### SMS not working?
- Verify Twilio credentials in .env
- Check if trial account is active
- Verify phone numbers in Twilio console

### Database errors?
- Delete instance/healthcare.db
- Restart the application
- Database will be recreated automatically

## 📱 HOW TO USE

### As a Patient:
1. Login → Patient Login → Sign in with Google
2. Update profile with phone number
3. Your caretaker will add medicines
4. Check dashboard for today's schedule
5. Click "Mark Taken" after taking medicine
6. Use emergency button if needed

### As a Caretaker:
1. Login → Caretaker Login → Sign in with Google
2. Add patients using their email
3. Add medicines for each patient
4. Monitor patient activities
5. Respond to emergency alerts
6. Process medicine refill requests

## 🌐 DEPLOY FOR FREE

### Option 1: Render.com (Easiest)
1. Push code to GitHub
2. Create account on render.com
3. New Web Service → Connect GitHub
4. Add environment variables
5. Deploy!

### Option 2: PythonAnywhere
1. Upload files to PythonAnywhere
2. Set up virtual environment
3. Configure web app
4. Done!

## 📞 NEED HELP?

1. Read README.md for detailed docs
2. Check INSTALLATION_GUIDE.md
3. Review code comments
4. All files are well-documented!

## ⚠️ IMPORTANT NOTES

1. **Security**: Never commit .env file to Git!
2. **Database**: SQLite for development, PostgreSQL for production
3. **HTTPS**: Required for production Google OAuth
4. **Reminders**: Run continuously to send automatic reminders

## 🎉 YOU'RE ALL SET!

Your complete healthcare management system is ready to run!

Questions? Check README.md for comprehensive documentation.

Made with ❤️ for better healthcare
