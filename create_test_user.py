#!/usr/bin/env python3
"""
Script to create a test user in the database
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def create_test_user():
    """Create a test administrator user"""
    with app.app_context():
        # Create database tables if they don't exist
        db.create_all()
        
        # Check if test user already exists
        test_user = User.query.filter_by(email='admin@test.com').first()
        if test_user:
            print("Test user already exists!")
            return
        
        # Create test administrator user
        admin_user = User(
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            role='administrator',
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        # Create test teacher user
        teacher_user = User(
            email='teacher@test.com',
            password_hash=generate_password_hash('teacher123'),
            role='teacher',
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        # Create test student user
        student_user = User(
            email='student@test.com',
            password_hash=generate_password_hash('student123'),
            role='student',
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(admin_user)
            db.session.add(teacher_user)
            db.session.add(student_user)
            db.session.commit()
            print("✅ Test users created successfully!")
            print("📧 Admin: admin@test.com / admin123")
            print("📧 Teacher: teacher@test.com / teacher123")
            print("📧 Student: student@test.com / student123")
        except Exception as e:
            print(f"❌ Error creating test users: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_user()
