#!/usr/bin/env python3
"""
Simple database initialization script
"""

from app import app, db, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def init_database():
    """Initialize database and create test users"""
    with app.app_context():
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Create test users
            print("Creating test users...")
            
            # Check if test users already exist
            admin_user = User.query.filter_by(email='admin@test.com').first()
            if not admin_user:
                admin_user = User(
                    email='admin@test.com',
                    password_hash=generate_password_hash('admin123'),
                    role='administrator',
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(admin_user)
                print("✅ Admin user created")
            
            teacher_user = User.query.filter_by(email='teacher@test.com').first()
            if not teacher_user:
                teacher_user = User(
                    email='teacher@test.com',
                    password_hash=generate_password_hash('teacher123'),
                    role='teacher',
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(teacher_user)
                print("✅ Teacher user created")
            
            student_user = User.query.filter_by(email='student@test.com').first()
            if not student_user:
                student_user = User(
                    email='student@test.com',
                    password_hash=generate_password_hash('student123'),
                    role='student',
                    is_active=True,
                    is_verified=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(student_user)
                print("✅ Student user created")
            
            # Commit changes
            db.session.commit()
            print("✅ Database initialization completed!")
            print("\n📧 Test Users:")
            print("   Admin: admin@test.com / admin123")
            print("   Teacher: teacher@test.com / teacher123")
            print("   Student: student@test.com / student123")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    init_database()
