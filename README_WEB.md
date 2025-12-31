# 🎓 WebReg Monitor - Web Frontend

Beautiful web interface for monitoring UCSD WebReg courses!

## ✨ Features

- 🎨 **Modern UI** - Sleek gradient design
- 📊 **Live Stats** - See notifications, checks, and more
- ➕ **Easy Add** - Add courses with one click
- 📧 **Email Alerts** - Get notified instantly
- ⏯️ **Pause/Resume** - Control monitoring per course
- 📱 **Responsive** - Works on mobile too

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements_web.txt
```

### 2. Set Up Email (Optional)

Create `email_config.json`:
```json
{
  "sender_email": "your@gmail.com",
  "sender_password": "your_app_password"
}
```

Get Gmail app password: https://myaccount.google.com/apppasswords

### 3. Start the API Server

```bash
python3 api.py
```

This starts the backend at `http://localhost:5000`

### 4. Open the Frontend

Open `index.html` in your browser or serve it:

```bash
# Option 1: Just double-click index.html

# Option 2: Use Python's HTTP server
python3 -m http.server 8000
# Then go to: http://localhost:8000
```

### 5. Start the Monitor

In a NEW terminal:

```bash
python3 monitor_web.py
```

This logs into WebReg and starts checking courses!

## 📁 File Structure

```
backend/
├── api.py                      # Flask API server
├── monitor_web.py              # Monitoring script (reads from DB)
├── index.html                  # Web frontend
├── webreg_bot.py              # Bot (from before)
├── email_config.json          # Email settings (create this)
├── cookies.json               # Auto-created
├── webreg.db                  # Auto-created database
└── requirements_web.txt       # Python dependencies
```

## 🎯 How to Use

### Add a Course:
1. Open `http://localhost:8000` (or just open `index.html`)
2. Enter subject (e.g., "CSE"), course number (e.g., "100"), and your email
3. Click "Add Course"

### Monitor Runs Automatically:
- Checks every 60 seconds
- Sends email when seats available
- Only notifies once per hour (no spam!)

### Pause/Resume:
- Click "Pause" to stop monitoring a course
- Click "Resume" to start again

### Delete:
- Click "Delete" to remove a course completely

## 🌐 Running All Three Together

You need **3 terminal windows**:

**Terminal 1 - API Server:**
```bash
python3 api.py
```

**Terminal 2 - Frontend (optional if using file:// ):**
```bash
python3 -m http.server 8000
```

**Terminal 3 - Monitor:**
```bash
python3 monitor_web.py
```

Then open browser to `http://localhost:8000`

## 📊 What You'll See

- **Active Courses** - How many you're monitoring
- **Notifications Sent** - Total alerts sent
- **Total Checks** - How many times we checked
- **Course List** - All your courses with status

## 🎨 Screenshots

The UI has:
- Purple gradient background
- White cards with shadows
- Responsive grid layout
- Smooth animations
- Real-time updates (refreshes every 10 seconds)

## 🔧 Troubleshooting

**"Cannot connect to API"**
- Make sure `api.py` is running
- Check it's on `http://localhost:5000`

**"Login fails"**
- Run `python3 monitor_web.py` 
- Login manually when prompted
- Fresh cookies will be saved

**"No email sent"**
- Check `email_config.json` exists
- Verify Gmail app password is correct
- Make sure 2FA is enabled on Gmail

## 🚀 Deploy to Production

See `DEPLOYMENT.md` for cloud deployment options!

---

Made with ❤️ for UCSD students