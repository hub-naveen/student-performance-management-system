#!/usr/bin/env python3
"""
Script to add sample student data for testing
"""

from app import app, db, StudentProfile
from datetime import datetime

def add_sample_students():
    """Add sample student data"""
    with app.app_context():
        try:
            # Sample student data
            sample_students = [
                {
                    'student_id': 'STU0001',
                    'first_name': 'John',
                    'last_name': 'Doe',
                    'gender': 'Male',
                    'age': 16,
                    'teacher_feedback': 'Good',
                    'attendance': 85,
                    'hours_studied': 25,
                    'previous_scores': 78,
                    'parental_involvement': 'High',
                    'access_to_resources': 'Good',
                    'extracurricular_activities': 'Yes',
                    'sleep_hours': 8,
                    'physical_activity': 3,
                    'internet_access': 'Yes',
                    'tutoring_sessions': 2,
                    'family_income': 'Medium',
                    'school_type': 'Public',
                    'peer_influence': 'Positive',
                    'learning_disabilities': 'No',
                    'parental_education_level': 'High School',
                    'distance_from_home': 'Near'
                },
                {
                    'student_id': 'STU0002',
                    'first_name': 'Jane',
                    'last_name': 'Smith',
                    'gender': 'Female',
                    'age': 17,
                    'teacher_feedback': 'Excellent',
                    'attendance': 95,
                    'hours_studied': 35,
                    'previous_scores': 92,
                    'parental_involvement': 'High',
                    'access_to_resources': 'Excellent',
                    'extracurricular_activities': 'Yes',
                    'sleep_hours': 9,
                    'physical_activity': 4,
                    'internet_access': 'Yes',
                    'tutoring_sessions': 1,
                    'family_income': 'High',
                    'school_type': 'Private',
                    'peer_influence': 'Positive',
                    'learning_disabilities': 'No',
                    'parental_education_level': 'College',
                    'distance_from_home': 'Near'
                },
                {
                    'student_id': 'STU0003',
                    'first_name': 'Mike',
                    'last_name': 'Johnson',
                    'gender': 'Male',
                    'age': 16,
                    'teacher_feedback': 'Average',
                    'attendance': 75,
                    'hours_studied': 15,
                    'previous_scores': 65,
                    'parental_involvement': 'Low',
                    'access_to_resources': 'Limited',
                    'extracurricular_activities': 'No',
                    'sleep_hours': 6,
                    'physical_activity': 1,
                    'internet_access': 'No',
                    'tutoring_sessions': 0,
                    'family_income': 'Low',
                    'school_type': 'Public',
                    'peer_influence': 'Negative',
                    'learning_disabilities': 'No',
                    'parental_education_level': 'High School',
                    'distance_from_home': 'Far'
                }
            ]
            
            # Add students to database
            for student_data in sample_students:
                # Check if student already exists
                existing_student = StudentProfile.query.get(student_data['student_id'])
                if existing_student:
                    print(f"Student {student_data['student_id']} already exists, skipping...")
                    continue
                
                student = StudentProfile(**student_data)
                db.session.add(student)
                print(f"✅ Added student: {student_data['first_name']} {student_data['last_name']}")
            
            db.session.commit()
            print(f"\n✅ Successfully added {len(sample_students)} sample students!")
            
        except Exception as e:
            print(f"❌ Error adding sample students: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_sample_students()
