# WebReg Monitor - Deployment Guide

## Quick Start (Local Background)

1. **Edit courses in `webreg_worker.py`:**
```python
db.add_course("CSE", "100", email="youremail@ucsd.edu")
db.add_course("MATH", "20C", email="youremail@ucsd.edu")
```

2. **Run in background:**
```bash
# macOS/Linux
nohup python3 webreg_worker.py > webreg.log 2>&1 &

# Keep running even after closing terminal
```

3. **Check logs:**
```bash
tail -f webreg.log
```

4. **Stop:**
```bash
ps aux | grep webreg_worker
kill <PID>
```

---

## Cloud Deployment Options (24/7 Free)

### Option 1: **Render.com** (Easiest, Free tier)

**Pros:** Free, easy, works great for background tasks
**Cons:** Sleeps after 15 min inactivity (paid tier fixes this)

**Steps:**
1. Push code to GitHub
2. Go to render.com → New Background Worker
3. Connect GitHub repo
4. Set start command: `python webreg_worker.py`
5. Add environment variables (cookies, etc.)
6. Deploy!

**Cost:** Free tier (with sleep), $7/month for always-on

---

### Option 2: **Railway.app** (Best for 24/7)

**Pros:** $5 free credit/month, no sleep, easy
**Cons:** Need credit card

**Steps:**
1. Push to GitHub
2. Railway.app → New Project
3. Deploy from GitHub
4. Add start command
5. Runs 24/7!

**Cost:** ~$5/month after free credit

---

### Option 3: **Fly.io** (Most flexible)

**Pros:** Free tier, full control, Docker
**Cons:** Requires Docker knowledge

**Cost:** Free tier available

---

### Option 4: **Your Own Computer** (Free but energy cost)

**Run as system service:**

**macOS (launchd):**
```bash
# Create plist file
cat > ~/Library/LaunchAgents/com.webreg.monitor.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.webreg.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/path/to/webreg_worker.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.webreg.monitor.plist
```

---

## Frontend (Web Interface)

### Option 1: **Simple HTML + API**

Create a simple webpage where users:
1. Enter course (CSE 100)
2. Enter email
3. Click "Monitor"
4. Backend adds to database

**Tech:** HTML + JavaScript + Flask API

---

### Option 2: **Modern Stack**

**Frontend:** Next.js (React)
**Backend:** FastAPI (Python)
**Database:** PostgreSQL
**Deploy:** Vercel (frontend) + Render (backend)

**Features:**
- User accounts
- Dashboard showing all courses
- Email/SMS notifications
- History of seat availability

**Estimated time:** 2-3 days to build

---

## Notification Options

### Email (Free)
```python
import smtplib
from email.mime.text import MIMEText

def send_email(to_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your@gmail.com'
    msg['To'] = to_email
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your@gmail.com', 'app_password')
        server.send_message(msg)
```

### SMS via Twilio (Paid)
```python
from twilio.rest import Client

def send_sms(phone, message):
    client = Client('account_sid', 'auth_token')
    client.messages.create(
        to=phone,
        from_='+1234567890',
        body=message
    )
```

### Discord Webhook (Free)
```python
import requests

def send_discord(webhook_url, message):
    requests.post(webhook_url, json={'content': message})
```

---

## Recommended Path for You

**Phase 1: Now (Local)**
- Use `webreg_worker.py` on your Mac
- Run it in background with `nohup`
- Get email notifications working

**Phase 2: Cloud (1-2 days)**
- Deploy to Render.com as background worker
- Free tier should work for testing
- Upgrade to $7/month for 24/7

**Phase 3: Frontend (1 week)**
- Build simple HTML form
- Create Flask API to add courses
- Deploy frontend to Vercel (free)

**Phase 4: Polish (optional)**
- Add user accounts
- Build dashboard
- Add Discord/SMS notifications

---

## Energy & Cost Comparison

| Method | Energy Cost | Actual Cost | Uptime |
|--------|-------------|-------------|--------|
| Your Mac 24/7 | ~$3-5/month | Free | 99% if on |
| Render.com | $0 | $7/month | 100% |
| Railway.app | $0 | $5/month | 100% |
| Fly.io | $0 | Free tier | 95% |

**Recommendation:** Railway.app ($5/month) for 24/7 automated monitoring

---

## Next Steps

1. **Test locally:** Run `webreg_worker.py` with `headless=False` first
2. **Verify it works:** Check it finds seats correctly
3. **Add email:** Implement email notifications
4. **Deploy:** Choose Railway.app or Render.com
5. **Build frontend:** (Optional) Create web interface

Want me to help with any of these steps?