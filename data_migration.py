#!/usr/bin/env python3
"""
Data Migration Script for Student Performance Prediction System
Imports existing CSV data into PostgreSQL database
"""

import pandas as pd
import sys
import os
from datetime import datetime
from app import app, db, User, StudentProfile
from werkzeug.security import generate_password_hash
import uuid

def clean_data(df):
    """Clean and prepare data for import"""
    # Remove duplicate columns (there's a duplicate Physical_Activity column)
    if 'Physical_Activity.1' in df.columns:
        df = df.drop('Physical_Activity.1', axis=1)
    
    # Handle missing values
    df = df.fillna({
        'age': df['age'].median(),
        'Teacher_Feedback': 'Medium',
        'Parental_Education_Level': 'High School',
        'Distance_from_Home': 'Near'
    })
    
    # Convert data types
    df['age'] = df['age'].astype(int)
    df['Attendance'] = df['Attendance'].astype(int)
    df['Hours_Studied'] = df['Hours_Studied'].astype(int)
    df['Previous_Scores'] = df['Previous_Scores'].astype(int)
    df['Sleep_Hours'] = df['Sleep_Hours'].astype(int)
    df['Physical_Activity'] = df['Physical_Activity'].astype(int)
    df['Tutoring_Sessions'] = df['Tutoring_Sessions'].astype(int)
    
    return df

def create_sample_users():
    """Create sample users for testing"""
    users_data = [
        {
            'email': 'admin@school.edu',
            'password': 'Admin123!',
            'role': 'administrator',
            'is_verified': True
        },
        {
            'email': 'teacher1@school.edu',
            'password': 'Teacher123!',
            'role': 'teacher',
            'is_verified': True
        },
        {
            'email': 'teacher2@school.edu',
            'password': 'Teacher123!',
            'role': 'teacher',
            'is_verified': True
        },
        {
            'email': 'student1@school.edu',
            'password': 'Student123!',
            'role': 'student',
            'is_verified': True
        },
        {
            'email': 'student2@school.edu',
            'password': 'Student123!',
            'role': 'student',
            'is_verified': True
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if existing_user:
            created_users.append(existing_user)
            continue
        
        user = User(
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            role=user_data['role'],
            is_verified=user_data['is_verified']
        )
        db.session.add(user)
        created_users.append(user)
    
    db.session.commit()
    return created_users

def import_student_data(csv_file_path):
    """Import student data from CSV file"""
    try:
        print(f"Reading CSV file: {csv_file_path}")
        df = pd.read_csv(csv_file_path)
        
        print(f"Original data shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Clean data
        df = clean_data(df)
        print(f"Cleaned data shape: {df.shape}")
        
        # Create sample users first
        print("Creating sample users...")
        users = create_sample_users()
        
        # Map user roles to student IDs for linking
        student_users = [u for u in users if u.role == 'student']
        
        # Import students
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if student already exists
                existing_student = StudentProfile.query.get(row['student_id'])
                if existing_student:
                    print(f"Skipping existing student: {row['student_id']}")
                    skipped_count += 1
                    continue
                
                # Link to user if available
                user_id = None
                if student_users and index < len(student_users):
                    user_id = student_users[index].user_id
                
                # Create student profile
                student = StudentProfile(
                    student_id=row['student_id'],
                    user_id=user_id,
                    first_name=f"Student{row['student_id']}",  # Generate names since not in CSV
                    last_name="Doe",
                    gender=row['Gender'],
                    age=row['age'],
                    teacher_feedback=row['Teacher_Feedback'],
                    attendance=row['Attendance'],
                    hours_studied=row['Hours_Studied'],
                    previous_scores=row['Previous_Scores'],
                    parental_involvement=row['Parental_Involvement'],
                    access_to_resources=row['Access_to_Resources'],
                    extracurricular_activities=row['Extracurricular_Activities'],
                    sleep_hours=row['Sleep_Hours'],
                    physical_activity=row['Physical_Activity'],
                    internet_access=row['Internet_Access'],
                    tutoring_sessions=row['Tutoring_Sessions'],
                    family_income=row['Family_Income'],
                    school_type=row['School_Type'],
                    peer_influence=row['Peer_Influence'],
                    learning_disabilities=row['Learning_Disabilities'],
                    parental_education_level=row['Parental_Education_Level'],
                    distance_from_home=row['Distance_from_Home']
                )
                
                db.session.add(student)
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"Imported {imported_count} students...")
                    db.session.commit()
                
            except Exception as e:
                error_msg = f"Error importing student {row['student_id']}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)
                continue
        
        # Final commit
        db.session.commit()
        
        print(f"\nMigration completed!")
        print(f"Imported: {imported_count} students")
        print(f"Skipped: {skipped_count} students (already existed)")
        print(f"Errors: {len(errors)}")
        
        if errors:
            print("\nErrors encountered:")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        return imported_count, skipped_count, errors
        
    except Exception as e:
        print(f"Migration failed: {e}")
        db.session.rollback()
        return 0, 0, [str(e)]

def main():
    """Main migration function"""
    csv_file = 'StudentPerformance.csv'
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        print("Please ensure the CSV file is in the current directory.")
        sys.exit(1)
    
    print("Starting data migration...")
    print("=" * 50)
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Import data
        imported, skipped, errors = import_student_data(csv_file)
        
        # Print summary
        print("\n" + "=" * 50)
        print("MIGRATION SUMMARY")
        print("=" * 50)
        print(f"Total students imported: {imported}")
        print(f"Students skipped (already existed): {skipped}")
        print(f"Errors encountered: {len(errors)}")
        
        if imported > 0:
            print(f"\n✅ Migration successful! {imported} students imported.")
        else:
            print(f"\n❌ Migration failed. No students imported.")
            sys.exit(1)

if __name__ == '__main__':
    main()
