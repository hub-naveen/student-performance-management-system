#!/usr/bin/env python3
"""
Setup script for Student Performance Management System
This script helps initialize the system and create sample data.
"""

import sqlite3
import bcrypt
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample data for demonstration"""
    
    # Initialize database
    from data.database import db
    
    print("🚀 Setting up Student Performance Management System...")
    
    # Create sample users
    sample_users = [
        ("student1", "student1@school.com", "Student123!", "student"),
        ("student2", "student2@school.com", "Student123!", "student"),
        ("student3", "student3@school.com", "Student123!", "student"),
        ("teacher1", "teacher1@school.com", "Teacher123!", "teacher"),
        ("teacher2", "teacher2@school.com", "Teacher123!", "teacher"),
        ("admin1", "admin1@school.com", "Admin123!", "admin"),
    ]
    
    print("📝 Creating sample users...")
    for username, email, password, role in sample_users:
        success = db.create_user(username, email, password, role)
        if success:
            print(f"✅ Created {role}: {username}")
        else:
            print(f"⚠️ User {username} already exists")
    
    # Create sample student profiles
    sample_profiles = [
        {
            'student_id': 'STU001',
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 16,
            'gender': 'Male',
            'grade_level': '10th',
            'school_name': 'Springfield High School'
        },
        {
            'student_id': 'STU002',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'age': 15,
            'gender': 'Female',
            'grade_level': '9th',
            'school_name': 'Springfield High School'
        },
        {
            'student_id': 'STU003',
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'age': 17,
            'gender': 'Male',
            'grade_level': '11th',
            'school_name': 'Springfield High School'
        }
    ]
    
    print("👤 Creating sample student profiles...")
    for i, profile in enumerate(sample_profiles):
        user_id = i + 1  # Assuming user IDs start from 1
        db.create_student_profile(user_id, profile)
        print(f"✅ Created profile for {profile['first_name']} {profile['last_name']}")
    
    # Create sample performance records
    subjects = ["Mathematics", "Science", "English", "History"]
    exam_types = ["Quiz", "Midterm", "Final", "Assignment"]
    
    print("📊 Creating sample performance records...")
    for student_id in ['STU001', 'STU002', 'STU003']:
        for subject in subjects:
            for exam_type in exam_types:
                # Generate realistic scores
                base_score = random.randint(70, 95)
                score = base_score + random.randint(-10, 10)
                score = max(50, min(100, score))  # Keep between 50-100
                
                date_taken = datetime.now().date() - timedelta(days=random.randint(1, 30))
                
                db.add_performance_record(
                    student_id=student_id,
                    subject=subject,
                    exam_type=exam_type,
                    score=score,
                    max_score=100,
                    date_taken=date_taken,
                    recorded_by=4,  # teacher1 user_id
                    notes=f"Sample {exam_type} for {subject}"
                )
        print(f"✅ Created performance records for {student_id}")
    
    # Create sample attendance records
    print("📅 Creating sample attendance records...")
    for student_id in ['STU001', 'STU002', 'STU003']:
        for i in range(20):  # Last 20 days
            date = datetime.now().date() - timedelta(days=i)
            status = random.choices(['present', 'absent', 'late'], weights=[0.85, 0.1, 0.05])[0]
            
            db.add_attendance_record(
                student_id=student_id,
                date=date,
                status=status,
                recorded_by=4,  # teacher1 user_id
                notes="Sample attendance record"
            )
        print(f"✅ Created attendance records for {student_id}")
    
    # Create sample notifications
    print("🔔 Creating sample notifications...")
    sample_notifications = [
        (1, "Welcome!", "Welcome to the Student Performance Management System!", "info"),
        (2, "Welcome!", "Welcome to the Student Performance Management System!", "info"),
        (3, "Welcome!", "Welcome to the Student Performance Management System!", "info"),
        (4, "System Ready", "You can now start managing student performance data.", "success"),
        (5, "System Ready", "You can now start managing student performance data.", "success"),
        (6, "Admin Access", "You have full administrative access to the system.", "info"),
    ]
    
    for user_id, title, message, notification_type in sample_notifications:
        db.add_notification(user_id, title, message, notification_type)
    
    print("✅ Created sample notifications")
    
    # Create sample recommendations
    print("💡 Creating sample recommendations...")
    sample_recommendations = [
        ("STU001", "study_habits", "Improve Study Habits", "Create a structured study schedule and find a quiet, dedicated study space.", "high"),
        ("STU001", "attendance", "Improve Attendance", "Regular attendance is crucial for academic success. Aim for 90%+ attendance.", "medium"),
        ("STU002", "goal_setting", "Set Specific Goals", "Set clear, achievable academic goals and track your progress regularly.", "medium"),
        ("STU003", "advanced_learning", "Pursue Advanced Learning", "Consider taking advanced courses or participating in academic competitions.", "low"),
    ]
    
    for student_id, rec_type, title, description, priority in sample_recommendations:
        db.add_recommendation(student_id, rec_type, title, description, priority)
    
    print("✅ Created sample recommendations")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Sample Login Credentials:")
    print("Student 1: username=student1, password=Student123!")
    print("Student 2: username=student2, password=Student123!")
    print("Student 3: username=student3, password=Student123!")
    print("Teacher 1: username=teacher1, password=Teacher123!")
    print("Teacher 2: username=teacher2, password=Teacher123!")
    print("Admin 1: username=admin1, password=Admin123!")
    print("\n🚀 Run the application with: streamlit run main_app.py")

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        print("Please ensure all dependencies are installed and model files are present.") 