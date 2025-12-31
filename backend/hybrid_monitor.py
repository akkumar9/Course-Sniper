#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebReg Monitor - Working version with web control
Uses database for courses, writes status for web interface
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from webreg_bot import WebRegBot
import time
from datetime import datetime
import json
import sqlite3

DB_PATH = 'webreg.db'
STATUS_FILE = 'monitor_status.json'
CONFIG_FILE = 'monitor_config.json'

def update_status(status, message=''):
    """Update status for web interface"""
    with open(STATUS_FILE, 'w') as f:
        json.dump({
            'running': status == 'running',
            'status': status,
            'message': message,
            'last_update': datetime.now().isoformat()
        }, f)

def get_config():
    """Get configuration (interval, etc)"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'interval': 3600}  # Default 1 hour

def check_stop_signal():
    """Check if user clicked stop on website"""
    if os.path.exists('monitor_stop.signal'):
        os.remove('monitor_stop.signal')
        return True
    return False

def get_active_courses():
    """Get active courses from database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, subject, course_num, email FROM courses WHERE active=1')
    courses = []
    for row in c.fetchall():
        courses.append({
            'id': row[0],
            'subject': row[1],
            'course_num': row[2],
            'email': row[3]
        })
    conn.close()
    return courses

def log_check(course_id, available_seats):
    """Log a check to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO checks (course_id, available_seats) VALUES (?, ?)',
        (course_id, available_seats)
    )
    conn.commit()
    conn.close()

def log_notification(course_id, available_seats, total_seats):
    """Log that we sent a notification"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO notifications (course_id, available_seats, total_seats) VALUES (?, ?, ?)',
        (course_id, available_seats, total_seats)
    )
    conn.commit()
    conn.close()

def was_sound_played_recently(course_id, minutes=60):
    """Check if we played sound recently"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS sound_played (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute(
        '''SELECT COUNT(*) FROM sound_played 
           WHERE course_id=? AND played_at > datetime('now', '-' || ? || ' minutes')''',
        (course_id, minutes)
    )
    count = c.fetchone()[0]
    conn.close()
    return count > 0

def log_sound_played(course_id):
    """Log that we played sound"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO sound_played (course_id) VALUES (?)', (course_id,))
    conn.commit()
    conn.close()

def send_email_notification(course, result):
    """Send email notification"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        with open('email_config.json', 'r') as f:
            config = json.load(f)
        
        to_email = course['email']
        subject = f"🔔 {course['subject']} {course['course_num']} - Seats Available!"
        
        sections_text = ""
        for section in result['sections'][:10]:
            if section['available'] > 0:
                sections_text += f"<li>{section['available']}/{section['total']} seats</li>\n"
        
        body = f"""
        <html>
        <body>
            <h2>WebReg Alert!</h2>
            <p><strong>{course['subject']} {course['course_num']}</strong> has seats available!</p>
            <ul>{sections_text}</ul>
            <p><strong>Total: {result['total_available']} seats</strong></p>
            <p>
                <a href="https://act.ucsd.edu/webreg2/start" 
                   style="background-color: #667eea; color: white; padding: 15px 30px; 
                          text-decoration: none; border-radius: 10px; display: inline-block;">
                    Enroll Now →
                </a>
            </p>
            <p style="color: gray; font-size: 12px; margin-top: 20px;">
                Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['sender_email']
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config['sender_email'], config['sender_password'])
            server.send_message(msg)
        
        print(f"✅ Email sent to {to_email}")
        return True
        
    except FileNotFoundError:
        print("⚠️  No email_config.json - skipping email")
        return False
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("WEBREG MONITOR - Web Controlled Version")
    print("="*60)
    print("Control this from: http://localhost:8000")
    print("="*60 + "\n")
    
    config = get_config()
    check_interval = config.get('interval', 3600)
    
    print(f"Check interval: {check_interval} seconds ({check_interval//60} minutes)")
    print(f"Press Ctrl+C to stop\n")
    
    update_status('starting', 'Logging in...')
    
    # Try logging in with retries
    max_login_attempts = 5
    bot = None
    
    for attempt in range(max_login_attempts):
        try:
            print("="*60)
            print(f"LOGIN ATTEMPT {attempt + 1}/{max_login_attempts}")
            print("="*60)
            
            if bot:
                print("Closing previous browser...")
                bot.close()
                time.sleep(2)
            
            bot = WebRegBot(headless=False)
            bot.login_manual(use_cookies=True)
            
            # Test if login worked
            courses = get_active_courses()
            if courses:
                print("\n🔍 Testing login with a quick search...")
                test_result = bot.search_course(courses[0]['subject'], courses[0]['course_num'])
                
                if test_result:
                    print("\n✅ Login successful and verified!")
                    break
                else:
                    print("\n⚠️  Login appeared to work but search failed")
                    if attempt < max_login_attempts - 1:
                        print(f"Retrying... (attempt {attempt + 2}/{max_login_attempts})")
                        time.sleep(3)
                        continue
            else:
                print("\n✅ Login successful! (No courses to test yet)")
                break
                    
        except Exception as e:
            print(f"\n❌ Login attempt {attempt + 1} failed: {e}")
            if attempt < max_login_attempts - 1:
                print(f"Retrying... (attempt {attempt + 2}/{max_login_attempts})")
                time.sleep(3)
                continue
            else:
                print("\n❌ All login attempts failed!")
                update_status('error', 'Login failed')
                if bot:
                    bot.close()
                return
    
    if not bot:
        print("\n❌ Could not initialize bot")
        update_status('error', 'Failed to start')
        return
    
    print("\n✅ Ready to monitor! Starting checks...\n")
    update_status('running', 'Monitor active')
    
    try:
        iteration = 0
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while True:
            # Check for stop signal
            if check_stop_signal():
                print("\n⏹️  Stop signal received from website")
                break
            
            # Reload config in case interval changed
            config = get_config()
            check_interval = config.get('interval', 3600)
            
            iteration += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print("\n" + "="*60)
            print(f"Check #{iteration} - {timestamp}")
            print("="*60)
            
            update_status('running', f'Check #{iteration}')
            
            courses = get_active_courses()
            
            if not courses:
                print("No active courses. Add some at http://localhost:8000")
                print(f"⏰ Waiting {check_interval} seconds...")
                time.sleep(check_interval)
                continue
            
            print(f"Monitoring {len(courses)} course(s)")
            
            at_least_one_success = False
            
            for course in courses:
                # Check stop signal during course checks too
                if check_stop_signal():
                    print("\n⏹️  Stop signal received")
                    break
                
                subject = course['subject']
                course_num = course['course_num']
                course_id = course['id']
                
                try:
                    print(f"\n[{subject} {course_num}] Checking...")
                    
                    result = bot.search_course(subject, course_num)
                    
                    if result:
                        at_least_one_success = True
                        consecutive_failures = 0
                        
                        log_check(course_id, result['total_available'])
                        
                        if result.get('has_availability'):
                            total = result['total_available']
                            print(f"[{subject} {course_num}] ✅ {total} SEATS AVAILABLE!")
                            
                            # Play sound once per hour
                            if not was_sound_played_recently(course_id, minutes=60):
                                print(f"[{subject} {course_num}] 🔊 Playing sound...")
                                try:
                                    import subprocess
                                    import platform
                                    if platform.system() == "Darwin":
                                        subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
                                        subprocess.run(["say", f"{subject} {course_num} has seats!"], check=False)
                                except:
                                    print("\a" * 3)
                                
                                log_sound_played(course_id)
                            else:
                                print(f"[{subject} {course_num}] 🔇 Sound skipped (played recently)")
                            
                            # Send email always
                            if send_email_notification(course, result):
                                log_notification(
                                    course_id,
                                    result['total_available'],
                                    sum(s['total'] for s in result['sections'])
                                )
                        else:
                            print(f"[{subject} {course_num}] No seats available")
                    else:
                        print(f"[{subject} {course_num}] ⚠️  Could not get results")
                    
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"[{subject} {course_num}] ❌ Error: {e}")
            
            # Check if we had too many consecutive failures
            if not at_least_one_success and courses:
                consecutive_failures += 1
                print(f"\n⚠️  No successful checks (failure {consecutive_failures}/{max_consecutive_failures})")
                
                if consecutive_failures >= max_consecutive_failures:
                    print("\n❌ Too many failures - session probably expired")
                    print("Restarting...\n")
                    update_status('restarting', 'Session expired, restarting...')
                    bot.close()
                    time.sleep(2)
                    main()  # Restart
                    return
            
            print(f"\n⏰ Waiting {check_interval} seconds ({check_interval//60} minutes)...")
            
            # Sleep in small chunks to check for stop signal
            for _ in range(check_interval // 5):
                if check_stop_signal():
                    print("\n⏹️  Stop signal received")
                    break
                time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n✋ Stopped by user")
    finally:
        # DON'T close browser - keep it open for next run
        print("👋 Monitor stopped - browser stays open")
        update_status('stopped', 'Monitor stopped')

if __name__ == "__main__":
    main()