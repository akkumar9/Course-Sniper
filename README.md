# CourseSniper - UCSD WebReg Monitor

Automatically monitors UCSD WebReg and emails you when seats open up in full classes.

## What it does

Checks WebReg every 30 minutes to 4 hours (you pick) and sends you an email the second a seat opens up. Way better than refreshing the page 500 times a day.

## Features

- Monitors as many courses as you want
- Email notifications when seats are available
- Web interface to add/remove courses
- Stays logged into WebReg so you don't have to keep signing in
- Sound alert on your computer when it finds a seat
- Configurable check intervals

## Tech used

Python, Selenium, Flask, SQLite. Frontend is just HTML/CSS/JS (no React or anything fancy).

## Installation

You need Python 3.11 or newer and Chrome.

Clone this repo:
```bash
git clone https://github.com/aryankumar009/Course-Sniper.git
cd Course-Sniper
```

Install dependencies:
```bash
cd backend
pip3 install -r requirements_web.txt
```

Optional - set up email notifications:
```bash
cp email_config.example.json email_config.json
```
Then edit email_config.json with your Gmail and app password. Get an app password here: https://myaccount.google.com/apppasswords

## How to run

Open two terminals.

Terminal 1:
```bash
cd backend
python3 api.py
```

Terminal 2:
```bash
cd frontend
python3 -m http.server 8000
```

Then open http://localhost:8000/index.html in your browser.

Add the courses you want to monitor, pick how often you want it to check (I use 1 hour), and click Start Monitor. A Chrome window will open for you to login to WebReg. Do the Duo thing, select your quarter, click Go. After that just minimize the browser and forget about it.

You'll get an email whenever a seat opens up.

To stop it, click Stop Monitor on the website.

## How it works

Uses Selenium to automate Chrome. Logs into WebReg, saves your cookies so you stay logged in, then checks your courses on a loop. When it finds available seats it sends you an email and plays a sound.

The web interface talks to a Flask API that manages everything. Course data gets stored in SQLite.

## File structure
```
backend/
  webreg_bot.py         - main bot code
  hybrid_monitor.py     - monitoring loop
  api.py                - Flask API
  
frontend/
  index.html            - web interface
```

## Settings

Check interval: 30 minutes to 4 hours
Email cooldown: won't spam you, only sends once per hour per course
Sound alerts: plays once per hour (macOS only)

## Troubleshooting

If cookies expire the browser will pop up again for you to login. Just login again and you're good.

Make sure the API is running on port 5001 (not 5000, AirPlay uses that).

The browser needs to stay open. Just minimize it.

## Notes

Your computer needs to stay on for this to work. On Mac you can use `caffeinate` to keep it awake.

WebReg sessions last about 24 hours before you need to login again.

There's a 3 second delay between checking different courses so you don't spam WebReg.

Each person runs their own copy locally.

## Contributing

PRs welcome. Just make sure your code works with actual WebReg before submitting.

## Disclaimer

Educational purposes only. Don't abuse this or violate UCSD policies. I'm not responsible if you do something dumb with it.

## License

MIT
