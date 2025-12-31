# -*- coding: utf-8 -*-
"""
WebReg Monitor - Flask API Backend
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import os
import time

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

DB_PATH = 'webreg.db'

# Database setup
def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Courses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            course_num TEXT NOT NULL,
            email TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Notifications table
    c.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            available_seats INTEGER,
            total_seats INTEGER,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    # Checks table
    c.execute('''
        CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            available_seats INTEGER,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT c.id, c.subject, c.course_num, c.email, c.active, c.created_at,
               COUNT(DISTINCT n.id) as notification_count,
               MAX(ch.checked_at) as last_check,
               MAX(ch.available_seats) as last_available
        FROM courses c
        LEFT JOIN notifications n ON c.id = n.course_id
        LEFT JOIN checks ch ON c.id = ch.course_id
        GROUP BY c.id
        ORDER BY c.created_at DESC
    ''')
    
    courses = []
    for row in c.fetchall():
        courses.append({
            'id': row[0],
            'subject': row[1],
            'course_num': row[2],
            'email': row[3],
            'active': row[4] == 1,
            'created_at': row[5],
            'notification_count': row[6],
            'last_check': row[7],
            'last_available': row[8]
        })
    
    conn.close()
    return jsonify(courses)

@app.route('/api/courses', methods=['POST'])
def add_course():
    """Add a new course"""
    data = request.json
    
    subject = data.get('subject', '').upper().strip()
    course_num = data.get('course_num', '').strip()
    email = data.get('email', '').strip()
    
    if not subject or not course_num or not email:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate email
    if '@' not in email:
        return jsonify({'error': 'Invalid email'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if already exists
    c.execute(
        'SELECT id FROM courses WHERE subject=? AND course_num=? AND email=?',
        (subject, course_num, email)
    )
    existing = c.fetchone()
    
    if existing:
        conn.close()
        return jsonify({'error': 'Course already being monitored'}), 400
    
    # Add course
    c.execute(
        'INSERT INTO courses (subject, course_num, email) VALUES (?, ?, ?)',
        (subject, course_num, email)
    )
    course_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': course_id,
        'subject': subject,
        'course_num': course_num,
        'email': email,
        'active': True
    }), 201

@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM courses WHERE id=?', (course_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/courses/<int:course_id>/toggle', methods=['POST'])
def toggle_course(course_id):
    """Toggle course active status"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE courses SET active = 1 - active WHERE id=?', (course_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Total courses
    c.execute('SELECT COUNT(*) FROM courses WHERE active=1')
    total_courses = c.fetchone()[0]
    
    # Total notifications sent
    c.execute('SELECT COUNT(*) FROM notifications')
    total_notifications = c.fetchone()[0]
    
    # Total checks
    c.execute('SELECT COUNT(*) FROM checks')
    total_checks = c.fetchone()[0]
    
    # Recent notifications
    c.execute('''
        SELECT c.subject, c.course_num, n.available_seats, n.sent_at
        FROM notifications n
        JOIN courses c ON n.course_id = c.id
        ORDER BY n.sent_at DESC
        LIMIT 5
    ''')
    recent = []
    for row in c.fetchall():
        recent.append({
            'course': f"{row[0]} {row[1]}",
            'seats': row[2],
            'time': row[3]
        })
    
    conn.close()
    
    return jsonify({
        'total_courses': total_courses,
        'total_notifications': total_notifications,
        'total_checks': total_checks,
        'recent_notifications': recent
    })

@app.route('/api/history/<int:course_id>', methods=['GET'])
def get_course_history(course_id):
    """Get check history for a course"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT available_seats, checked_at
        FROM checks
        WHERE course_id=?
        ORDER BY checked_at DESC
        LIMIT 50
    ''', (course_id,))
    
    history = []
    for row in c.fetchall():
        history.append({
            'seats': row[0],
            'time': row[1]
        })
    
    conn.close()
    return jsonify(history)

@app.route('/api/monitor/status', methods=['GET'])
def get_monitor_status():
    """Get monitor status"""
    status_file = 'monitor_status.json'
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            return jsonify(json.load(f))
    else:
        return jsonify({
            'running': False,
            'status': 'stopped',
            'message': 'Monitor not started'
        })

@app.route('/api/monitor/start', methods=['POST'])
def start_monitor():
    """Start the monitor"""
    import subprocess
    
    # Check if already running
    if os.path.exists('monitor_status.json'):
        with open('monitor_status.json', 'r') as f:
            status = json.load(f)
        if status.get('running'):
            return jsonify({'error': 'Monitor already running'}), 400
    
    # Get interval from request
    data = request.json or {}
    interval = data.get('interval', 3600)  # Default 1 hour
    
    # Save config
    with open('monitor_config.json', 'w') as f:
        json.dump({'interval': interval}, f)
    
    # Start monitor in background using the WORKING hybrid version
    subprocess.Popen([
        'python3', 'hybrid_monitor.py'
    ], stdout=open('monitor.log', 'w'), stderr=subprocess.STDOUT)
    
    time.sleep(2)
    
    return jsonify({
        'success': True, 
        'message': f'Monitor starting (checking every {interval//60} minutes)'
    })

@app.route('/api/monitor/stop', methods=['POST'])
def stop_monitor():
    """Stop the monitor"""
    import os
    # Write stop signal in the backend directory
    signal_path = os.path.join(os.path.dirname(__file__), 'monitor_stop.signal')
    with open(signal_path, 'w') as f:
        f.write('stop')
    
    print(f"[API] Stop signal written to: {signal_path}")
    
    return jsonify({'success': True, 'message': 'Monitor stopping...'})

@app.route('/api/monitor/config', methods=['POST'])
def update_monitor_config():
    """Update monitor configuration"""
    data = request.json or {}
    interval = data.get('interval', 3600)
    
    with open('monitor_config.json', 'w') as f:
        json.dump({'interval': interval}, f)
    
    return jsonify({
        'success': True,
        'message': f'Config updated (checking every {interval//60} minutes)'
    })

@app.route('/api/courses/<int:course_id>/check-now', methods=['POST'])
def check_course_now(course_id):
    """Immediately check a single course"""
    import subprocess
    import sys
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT subject, course_num, email FROM courses WHERE id=?', (course_id,))
    course = c.fetchone()
    conn.close()
    
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    subject, course_num, email = course
    
    # Run check in background
    subprocess.Popen([
        sys.executable, 
        'check_single_course.py',
        str(course_id),
        subject,
        course_num,
        email
    ])
    
    return jsonify({
        'success': True,
        'message': f'Checking {subject} {course_num}...'
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("WEBREG MONITOR - API SERVER")
    print("="*60)
    print("API running at: http://localhost:5001")
    print("Frontend should connect to this")
    print("="*60 + "\n")
    app.run(debug=True, port=5001)