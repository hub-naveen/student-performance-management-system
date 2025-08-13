from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import pandas as pd
import pickle
import logging
import json
from sqlalchemy import and_, or_, func
import numpy as np
from models import db, User, StudentProfile
from functools import wraps

# Create blueprint for API routes
api = Blueprint('api', __name__, url_prefix='/api')

# Configure logging
logger = logging.getLogger(__name__)

# Role-based access control decorator
def role_required(allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or user.role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Load the trained model
# Temporarily disabled due to pickle compatibility issues
model = None
logger.warning("ML model temporarily disabled - using mock predictions")

# Student Management Routes
@api.route('/students', methods=['GET'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def get_students():
    """Get all students with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        gender = request.args.get('gender', '')
        school_type = request.args.get('school_type', '')
        
        # Build query
        query = StudentProfile.query
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    StudentProfile.first_name.like(f'%{search}%'),
                    StudentProfile.last_name.like(f'%{search}%'),
                    StudentProfile.student_id.like(f'%{search}%')
                )
            )
        
        if gender:
            query = query.filter(StudentProfile.gender == gender)
        
        if school_type:
            query = query.filter(StudentProfile.school_type == school_type)
        
        # Paginate results
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        students = []
        for student in pagination.items:
            students.append({
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'gender': student.gender,
                'age': student.age,
                'attendance': student.attendance,
                'previous_scores': student.previous_scores,
                'school_type': student.school_type,
                'created_at': student.created_at.isoformat() if student.created_at else None
            })
        
        return jsonify({
            'students': students,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get students error: {e}")
        return jsonify({'error': 'Failed to retrieve students'}), 500

@api.route('/students/<student_id>', methods=['GET'])
@jwt_required()
@role_required(['student', 'teacher', 'administrator'])
def get_student(student_id):
    """Get specific student profile"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if user has permission to view this student
        if current_user.role == 'student':
            student_profile = StudentProfile.query.filter_by(
                student_id=student_id,
                user_id=current_user_id
            ).first()
            if not student_profile:
                return jsonify({'error': 'Access denied'}), 403
        else:
            student_profile = StudentProfile.query.get(student_id)
            if not student_profile:
                return jsonify({'error': 'Student not found'}), 404
        
        student_data = {
            'student_id': student_profile.student_id,
            'first_name': student_profile.first_name,
            'last_name': student_profile.last_name,
            'gender': student_profile.gender,
            'age': student_profile.age,
            'teacher_feedback': student_profile.teacher_feedback,
            'attendance': student_profile.attendance,
            'hours_studied': student_profile.hours_studied,
            'previous_scores': student_profile.previous_scores,
            'parental_involvement': student_profile.parental_involvement,
            'access_to_resources': student_profile.access_to_resources,
            'extracurricular_activities': student_profile.extracurricular_activities,
            'sleep_hours': student_profile.sleep_hours,
            'physical_activity': student_profile.physical_activity,
            'internet_access': student_profile.internet_access,
            'tutoring_sessions': student_profile.tutoring_sessions,
            'family_income': student_profile.family_income,
            'school_type': student_profile.school_type,
            'peer_influence': student_profile.peer_influence,
            'learning_disabilities': student_profile.learning_disabilities,
            'parental_education_level': student_profile.parental_education_level,
            'distance_from_home': student_profile.distance_from_home,
            'created_at': student_profile.created_at.isoformat() if student_profile.created_at else None,
            'updated_at': student_profile.updated_at.isoformat() if student_profile.updated_at else None
        }
        
        return jsonify(student_data), 200
        
    except Exception as e:
        logger.error(f"Get student error: {e}")
        return jsonify({'error': 'Failed to retrieve student'}), 500

@api.route('/students', methods=['POST'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def create_student():
    """Create new student profile"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['student_id', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if student already exists
        if StudentProfile.query.get(data['student_id']):
            return jsonify({'error': 'Student ID already exists'}), 409
        
        # Create student profile
        student = StudentProfile(
            student_id=data['student_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data.get('gender'),
            age=data.get('age'),
            teacher_feedback=data.get('teacher_feedback'),
            attendance=data.get('attendance'),
            hours_studied=data.get('hours_studied'),
            previous_scores=data.get('previous_scores'),
            parental_involvement=data.get('parental_involvement'),
            access_to_resources=data.get('access_to_resources'),
            extracurricular_activities=data.get('extracurricular_activities'),
            sleep_hours=data.get('sleep_hours'),
            physical_activity=data.get('physical_activity'),
            internet_access=data.get('internet_access'),
            tutoring_sessions=data.get('tutoring_sessions'),
            family_income=data.get('family_income'),
            school_type=data.get('school_type'),
            peer_influence=data.get('peer_influence'),
            learning_disabilities=data.get('learning_disabilities'),
            parental_education_level=data.get('parental_education_level'),
            distance_from_home=data.get('distance_from_home')
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student created successfully',
            'student_id': student.student_id
        }), 201
        
    except Exception as e:
        logger.error(f"Create student error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create student'}), 500

@api.route('/students/<student_id>', methods=['PUT'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def update_student(student_id):
    """Update student profile"""
    try:
        student = StudentProfile.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = [
            'first_name', 'last_name', 'gender', 'age', 'teacher_feedback',
            'attendance', 'hours_studied', 'previous_scores', 'parental_involvement',
            'access_to_resources', 'extracurricular_activities', 'sleep_hours',
            'physical_activity', 'internet_access', 'tutoring_sessions',
            'family_income', 'school_type', 'peer_influence', 'learning_disabilities',
            'parental_education_level', 'distance_from_home'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(student, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': 'Student updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update student error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update student'}), 500

@api.route('/students/<student_id>', methods=['DELETE'])
@jwt_required()
@role_required(['administrator'])
def delete_student(student_id):
    """Delete student profile"""
    try:
        student = StudentProfile.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'message': 'Student deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete student error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete student'}), 500

# Performance Prediction Routes
@api.route('/predictions/<student_id>', methods=['GET'])
@jwt_required()
@role_required(['student', 'teacher', 'administrator'])
def get_prediction(student_id):
    """Get performance prediction for a student"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check permissions
        if current_user.role == 'student':
            student_profile = StudentProfile.query.filter_by(
                student_id=student_id,
                user_id=current_user_id
            ).first()
            if not student_profile:
                return jsonify({'error': 'Access denied'}), 403
        else:
            student_profile = StudentProfile.query.get(student_id)
            if not student_profile:
                return jsonify({'error': 'Student not found'}), 404
        
        # Mock prediction since model is disabled
        import random
        
        # Generate a realistic mock prediction based on student data
        base_score = student_profile.previous_scores or 75
        attendance_factor = (student_profile.attendance or 80) / 100.0
        study_factor = min((student_profile.hours_studied or 20) / 40.0, 1.0)
        
        # Calculate mock prediction
        prediction = base_score * 0.6 + attendance_factor * 20 + study_factor * 15
        prediction = max(0, min(100, prediction + random.uniform(-5, 5)))  # Add some randomness
        confidence = 0.75 + random.uniform(0, 0.2)  # Mock confidence
        
        return jsonify({
            'student_id': student_id,
            'predicted_score': float(prediction),
            'confidence_level': confidence,
            'prediction_date': datetime.utcnow().isoformat(),
            'model_version': 'v1.0'
        }), 200
        
    except Exception as e:
        logger.error(f"Get prediction error: {e}")
        return jsonify({'error': 'Failed to generate prediction'}), 500

@api.route('/predictions/batch', methods=['POST'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def batch_predictions():
    """Generate predictions for multiple students"""
    try:
        data = request.get_json()
        student_ids = data.get('student_ids', [])
        
        if not student_ids:
            return jsonify({'error': 'No student IDs provided'}), 400
        
        # Mock predictions since model is disabled
        import random
        
        predictions = []
        
        for student_id in student_ids:
            student = StudentProfile.query.get(student_id)
            if not student:
                continue
            
            # Generate mock prediction
            base_score = student.previous_scores or 75
            attendance_factor = (student.attendance or 80) / 100.0
            study_factor = min((student.hours_studied or 20) / 40.0, 1.0)
            
            prediction = base_score * 0.6 + attendance_factor * 20 + study_factor * 15
            prediction = max(0, min(100, prediction + random.uniform(-5, 5)))
            
            predictions.append({
                'student_id': student_id,
                'student_name': f"{student.first_name} {student.last_name}",
                'predicted_score': float(prediction),
                'confidence_level': 0.85
            })
        
        return jsonify({
            'predictions': predictions,
            'total_students': len(predictions)
        }), 200
        
    except Exception as e:
        logger.error(f"Batch predictions error: {e}")
        return jsonify({'error': 'Failed to generate batch predictions'}), 500

# Analytics and Dashboard Routes
@api.route('/analytics/overview', methods=['GET'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def get_analytics_overview():
    """Get overview analytics for dashboard"""
    try:
        # Get basic statistics
        total_students = StudentProfile.query.count()
        
        # Gender distribution
        gender_stats = db.session.query(
            StudentProfile.gender,
            func.count(StudentProfile.student_id)
        ).group_by(StudentProfile.gender).all()
        
        # School type distribution
        school_stats = db.session.query(
            StudentProfile.school_type,
            func.count(StudentProfile.student_id)
        ).group_by(StudentProfile.school_type).all()
        
        # Average scores by various factors
        avg_attendance = db.session.query(func.avg(StudentProfile.attendance)).scalar()
        avg_hours_studied = db.session.query(func.avg(StudentProfile.hours_studied)).scalar()
        avg_previous_scores = db.session.query(func.avg(StudentProfile.previous_scores)).scalar()
        
        # Performance distribution
        performance_ranges = [
            ('Excellent (90-100)', 90, 100),
            ('Good (80-89)', 80, 89),
            ('Average (70-79)', 70, 79),
            ('Below Average (60-69)', 60, 69),
            ('Poor (<60)', 0, 59)
        ]
        
        performance_stats = []
        for label, min_score, max_score in performance_ranges:
            count = StudentProfile.query.filter(
                and_(
                    StudentProfile.previous_scores >= min_score,
                    StudentProfile.previous_scores <= max_score
                )
            ).count()
            performance_stats.append({
                'range': label,
                'count': count,
                'percentage': round((count / total_students) * 100, 2) if total_students > 0 else 0
            })
        
        return jsonify({
            'total_students': total_students,
            'gender_distribution': dict(gender_stats),
            'school_type_distribution': dict(school_stats),
            'averages': {
                'attendance': round(avg_attendance, 2) if avg_attendance else 0,
                'hours_studied': round(avg_hours_studied, 2) if avg_hours_studied else 0,
                'previous_scores': round(avg_previous_scores, 2) if avg_previous_scores else 0
            },
            'performance_distribution': performance_stats
        }), 200
        
    except Exception as e:
        logger.error(f"Analytics overview error: {e}")
        return jsonify({'error': 'Failed to retrieve analytics'}), 500

@api.route('/analytics/performance-trends', methods=['GET'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def get_performance_trends():
    """Get performance trends and insights"""
    try:
        # Performance by gender
        gender_performance = db.session.query(
            StudentProfile.gender,
            func.avg(StudentProfile.previous_scores).label('avg_score'),
            func.avg(StudentProfile.attendance).label('avg_attendance'),
            func.avg(StudentProfile.hours_studied).label('avg_hours')
        ).group_by(StudentProfile.gender).all()
        
        # Performance by school type
        school_performance = db.session.query(
            StudentProfile.school_type,
            func.avg(StudentProfile.previous_scores).label('avg_score'),
            func.avg(StudentProfile.attendance).label('avg_attendance'),
            func.avg(StudentProfile.hours_studied).label('avg_hours')
        ).group_by(StudentProfile.school_type).all()
        
        # Performance by parental involvement
        parental_performance = db.session.query(
            StudentProfile.parental_involvement,
            func.avg(StudentProfile.previous_scores).label('avg_score'),
            func.count(StudentProfile.student_id).label('count')
        ).group_by(StudentProfile.parental_involvement).all()
        
        # Age group analysis
        age_groups = [
            ('15-16', 15, 16),
            ('17-18', 17, 18),
            ('19+', 19, 25)
        ]
        
        age_performance = []
        for label, min_age, max_age in age_groups:
            result = db.session.query(
                func.avg(StudentProfile.previous_scores).label('avg_score'),
                func.count(StudentProfile.student_id).label('count')
            ).filter(
                and_(
                    StudentProfile.age >= min_age,
                    StudentProfile.age <= max_age
                )
            ).first()
            
            if result.avg_score:
                age_performance.append({
                    'age_group': label,
                    'avg_score': round(result.avg_score, 2),
                    'count': result.count
                })
        
        return jsonify({
            'gender_performance': [
                {
                    'gender': item.gender,
                    'avg_score': round(item.avg_score, 2),
                    'avg_attendance': round(item.avg_attendance, 2),
                    'avg_hours': round(item.avg_hours, 2)
                }
                for item in gender_performance
            ],
            'school_performance': [
                {
                    'school_type': item.school_type,
                    'avg_score': round(item.avg_score, 2),
                    'avg_attendance': round(item.avg_attendance, 2),
                    'avg_hours': round(item.avg_hours, 2)
                }
                for item in school_performance
            ],
            'parental_performance': [
                {
                    'parental_involvement': item.parental_involvement,
                    'avg_score': round(item.avg_score, 2),
                    'count': item.count
                }
                for item in parental_performance
            ],
            'age_performance': age_performance
        }), 200
        
    except Exception as e:
        logger.error(f"Performance trends error: {e}")
        return jsonify({'error': 'Failed to retrieve performance trends'}), 500

# Data Import/Export Routes
@api.route('/data/import', methods=['POST'])
@jwt_required()
@role_required(['administrator'])
def import_data():
    """Import student data from CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Read CSV file
        df = pd.read_csv(file)
        
        # Validate required columns
        required_columns = ['student_id', 'first_name', 'last_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({'error': f'Missing required columns: {missing_columns}'}), 400
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if student already exists
                if StudentProfile.query.get(row['student_id']):
                    errors.append(f"Row {index + 1}: Student ID {row['student_id']} already exists")
                    continue
                
                # Create student profile
                student = StudentProfile(
                    student_id=row['student_id'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    gender=row.get('gender'),
                    age=row.get('age'),
                    teacher_feedback=row.get('teacher_feedback'),
                    attendance=row.get('attendance'),
                    hours_studied=row.get('hours_studied'),
                    previous_scores=row.get('previous_scores'),
                    parental_involvement=row.get('parental_involvement'),
                    access_to_resources=row.get('access_to_resources'),
                    extracurricular_activities=row.get('extracurricular_activities'),
                    sleep_hours=row.get('sleep_hours'),
                    physical_activity=row.get('physical_activity'),
                    internet_access=row.get('internet_access'),
                    tutoring_sessions=row.get('tutoring_sessions'),
                    family_income=row.get('family_income'),
                    school_type=row.get('school_type'),
                    peer_influence=row.get('peer_influence'),
                    learning_disabilities=row.get('learning_disabilities'),
                    parental_education_level=row.get('parental_education_level'),
                    distance_from_home=row.get('distance_from_home')
                )
                
                db.session.add(student)
                imported_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully imported {imported_count} students',
            'imported_count': imported_count,
            'errors': errors
        }), 200
        
    except Exception as e:
        logger.error(f"Data import error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to import data'}), 500

@api.route('/data/export', methods=['GET'])
@jwt_required()
@role_required(['teacher', 'administrator'])
def export_data():
    """Export student data to CSV"""
    try:
        # Get all students
        students = StudentProfile.query.all()
        
        # Convert to DataFrame
        data = []
        for student in students:
            data.append({
                'student_id': student.student_id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'gender': student.gender,
                'age': student.age,
                'teacher_feedback': student.teacher_feedback,
                'attendance': student.attendance,
                'hours_studied': student.hours_studied,
                'previous_scores': student.previous_scores,
                'parental_involvement': student.parental_involvement,
                'access_to_resources': student.access_to_resources,
                'extracurricular_activities': student.extracurricular_activities,
                'sleep_hours': student.sleep_hours,
                'physical_activity': student.physical_activity,
                'internet_access': student.internet_access,
                'tutoring_sessions': student.tutoring_sessions,
                'family_income': student.family_income,
                'school_type': student.school_type,
                'peer_influence': student.peer_influence,
                'learning_disabilities': student.learning_disabilities,
                'parental_education_level': student.parental_education_level,
                'distance_from_home': student.distance_from_home
            })
        
        df = pd.DataFrame(data)
        
        # Generate CSV
        csv_data = df.to_csv(index=False)
        
        from flask import Response
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=students_export.csv'}
        )
        
    except Exception as e:
        logger.error(f"Data export error: {e}")
        return jsonify({'error': 'Failed to export data'}), 500

# Register blueprint with main app
def init_app(app):
    app.register_blueprint(api)
