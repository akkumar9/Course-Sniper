# 🎓 CourseSniper - UCSD WebReg Monitor

Automated course enrollment monitoring system for UCSD. Get instant notifications when seats open up in full classes.

## 🚀 Features

- **Real-time monitoring** - Checks WebReg every 30min-4hr (configurable)
- **Email notifications** - Instant alerts when seats become available
- **Web dashboard** - Modern React interface to manage courses
- **Session persistence** - Stays logged in with cookie management
- **Multi-course tracking** - Monitor unlimited courses simultaneously
- **Smart notifications** - Sound alerts once/hour, emails always

## 🛠️ Tech Stack

- **Backend:** Python, Selenium WebDriver, Flask REST API, SQLite
- **Frontend:** React, HTML5, CSS3
- **Automation:** Headless Chrome, dynamic DOM parsing
- **Notifications:** Gmail SMTP, system sound alerts

## 📦 Installation

### Prerequisites
- Python 3.11+
- Chrome browser
- Gmail account (for notifications)

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/course-sniper.git
cd course-sniper
```

2. **Install dependencies:**
```bash
cd backend
pip3 install -r requirements_web.txt
```

3. **Configure email (optional):**
```bash
cp email_config.example.json email_config.json
# Edit email_config.json with your Gmail and app password
```

Get Gmail app password: https://myaccount.google.com/apppasswords

## 🎯 Usage

### Start the system:

**Terminal 1 - API Server:**
```bash
cd backend
python3 api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python3 -m http.server 8000
```

### Use the web interface:

1. Open http://localhost:8000/index.html
2. Add courses (e.g., CSE 100, MATH 20C)
3. Select check interval (30min, 1hr, 2hr, 4hr)
4. Click **"Start Monitor"**
5. Login to WebReg when browser opens (one time)
6. Browser stays minimized - you'll get emails when seats open!

### Stop monitoring:

Click **"Stop Monitor"** on the website or press `Ctrl+C` in the API terminal.

## 📊 How It Works

1. **Session Management:** Uses Selenium to maintain persistent WebReg sessions with cookie-based authentication
2. **DOM Parsing:** Extracts seat data using jqGrid aria-describedby attributes
3. **Background Worker:** Runs continuous monitoring with configurable intervals
4. **Notification System:** Sends email alerts with seat details and enrollment links

## 🗂️ Project Structure
```
course-sniper/
├── backend/
│   ├── webreg_bot.py       # Core Selenium automation
│   ├── hybrid_monitor.py   # Background monitoring service
│   ├── api.py              # Flask REST API
│   └── requirements_web.txt
└── frontend/
    └── index.html          # Web dashboard
```

## ⚙️ Configuration

- **Check interval:** Adjustable from 30 minutes to 4 hours
- **Email cooldown:** 1 hour between notifications per course
- **Sound alerts:** Once per hour per course (macOS only)

## 🐛 Troubleshooting

**"Cookies expired" error:**
- Browser will open for manual login
- Complete Duo authentication
- Select quarter and click Go
- Press Enter in terminal

**API not connecting:**
- Ensure API is running on port 5001
- Check firewall settings
- Use http://localhost:5001 (not 5000)

**Browser keeps popping up:**
- This is normal - minimize it and it will stay minimized
- Browser must stay open for session persistence

## 📝 Notes

- **Session duration:** WebReg cookies typically last 24 hours
- **Rate limiting:** Built-in 3-second delay between course checks
- **Multi-user:** Each user runs their own instance locally
- **Uptime:** Requires computer to stay on (use `caffeinate` on macOS)

## 🤝 Contributing

Pull requests welcome! Please ensure:
- Code follows existing style
- Add comments for complex logic
- Test with actual WebReg before submitting

## ⚠️ Disclaimer

This tool is for educational purposes. Use responsibly and in accordance with UCSD policies. The author is not responsible for any misuse or violations of university policies.

## 📄 License

MIT License - See LICENSE file for details

---

Built with ❤️ for UCSD students tired of refreshing WebReg
