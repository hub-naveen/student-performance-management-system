import sqlite3
import bcrypt
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import json

class DatabaseManager:
    def __init__(self, db_path="student_performance.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'teacher', 'admin')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Student profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                student_id TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                grade_level TEXT,
                school_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Performance records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                subject TEXT NOT NULL,
                exam_type TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL DEFAULT 100,
                date_taken DATE NOT NULL,
                recorded_by INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recorded_by) REFERENCES users (id)
            )
        ''')
        
        # Attendance records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                date DATE NOT NULL,
                status TEXT CHECK(status IN ('present', 'absent', 'late')),
                recorded_by INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (recorded_by) REFERENCES users (id)
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT CHECK(type IN ('info', 'warning', 'error', 'success')),
                is_read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                recommendation_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
                is_completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def create_user(self, username, email, password, role):
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, password_hash, role FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user and self.verify_password(password, user[2]):
            # Update last login
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
            conn.commit()
            conn.close()
            return {
                'id': user[0],
                'username': user[1],
                'role': user[3]
            }
        
        conn.close()
        return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def create_student_profile(self, user_id, student_data):
        """Create or update student profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO student_profiles 
            (user_id, student_id, first_name, last_name, age, gender, grade_level, school_name, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            user_id, student_data['student_id'], student_data['first_name'], 
            student_data['last_name'], student_data['age'], student_data['gender'],
            student_data['grade_level'], student_data['school_name']
        ))
        
        conn.commit()
        conn.close()
    
    def get_student_profile(self, user_id):
        """Get student profile by user ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM student_profiles WHERE user_id = ?', (user_id,))
        profile = cursor.fetchone()
        
        conn.close()
        return profile
    
    def add_performance_record(self, student_id, subject, exam_type, score, max_score, date_taken, recorded_by, notes=""):
        """Add a performance record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance_records 
            (student_id, subject, exam_type, score, max_score, date_taken, recorded_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (student_id, subject, exam_type, score, max_score, date_taken, recorded_by, notes))
        
        conn.commit()
        conn.close()
    
    def get_student_performance(self, student_id, limit=50):
        """Get performance records for a student"""
        conn = self.get_connection()
        
        query = '''
            SELECT pr.*, u.username as recorded_by_name
            FROM performance_records pr
            LEFT JOIN users u ON pr.recorded_by = u.id
            WHERE pr.student_id = ?
            ORDER BY pr.date_taken DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(student_id, limit))
        conn.close()
        return df
    
    def add_attendance_record(self, student_id, date, status, recorded_by, notes=""):
        """Add attendance record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO attendance_records 
            (student_id, date, status, recorded_by, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, date, status, recorded_by, notes))
        
        conn.commit()
        conn.close()
    
    def get_student_attendance(self, student_id, start_date=None, end_date=None):
        """Get attendance records for a student"""
        conn = self.get_connection()
        
        query = '''
            SELECT ar.*, u.username as recorded_by_name
            FROM attendance_records ar
            LEFT JOIN users u ON ar.recorded_by = u.id
            WHERE ar.student_id = ?
        '''
        
        params = [student_id]
        
        if start_date:
            query += ' AND ar.date >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND ar.date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY ar.date DESC'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    
    def add_notification(self, user_id, title, message, notification_type="info"):
        """Add a notification"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, title, message, notification_type))
        
        conn.commit()
        conn.close()
    
    def get_user_notifications(self, user_id, unread_only=False):
        """Get notifications for a user"""
        conn = self.get_connection()
        
        query = '''
            SELECT * FROM notifications 
            WHERE user_id = ?
        '''
        
        if unread_only:
            query += ' AND is_read = FALSE'
        
        query += ' ORDER BY created_at DESC'
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        return df
    
    def mark_notification_read(self, notification_id):
        """Mark notification as read"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE notifications SET is_read = TRUE WHERE id = ?', (notification_id,))
        conn.commit()
        conn.close()
    
    def add_recommendation(self, student_id, recommendation_type, title, description, priority="medium"):
        """Add a recommendation for a student"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO recommendations 
            (student_id, recommendation_type, title, description, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, recommendation_type, title, description, priority))
        
        conn.commit()
        conn.close()
    
    def get_student_recommendations(self, student_id):
        """Get recommendations for a student"""
        conn = self.get_connection()
        
        query = '''
            SELECT * FROM recommendations 
            WHERE student_id = ?
            ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(student_id,))
        conn.close()
        return df
    
    def get_all_students(self):
        """Get all student profiles (for teachers/admins)"""
        conn = self.get_connection()
        
        query = '''
            SELECT sp.*, u.username, u.email
            FROM student_profiles sp
            JOIN users u ON sp.user_id = u.id
            ORDER BY sp.last_name, sp.first_name
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_performance_summary(self, student_id):
        """Get performance summary for a student"""
        conn = self.get_connection()
        
        query = '''
            SELECT 
                subject,
                AVG(score) as avg_score,
                MAX(score) as max_score,
                MIN(score) as min_score,
                COUNT(*) as total_exams
            FROM performance_records 
            WHERE student_id = ?
            GROUP BY subject
        '''
        
        df = pd.read_sql_query(query, conn, params=(student_id,))
        conn.close()
        return df

# Initialize database
db = DatabaseManager()
