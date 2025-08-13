<<<<<<< HEAD
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from datetime import datetime, timedelta
import uuid
import os
import re
from functools import wraps
import logging
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from models import db, User, StudentProfile, UserSession

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///student_performance.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



# Utility functions
def generate_secure_token(length=32):
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    return True, "Password is valid"

def role_required(allowed_roles):
    """Decorator for role-based access control"""
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

def send_verification_email(email, token):
    """Send email verification"""
    try:
        msg = Message(
            'Email Verification - Student Performance System',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f'''
        Thank you for registering with the Student Performance Prediction System!
        
        Please verify your email by clicking the following link:
        {request.host_url}verify-email/{token}
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        Student Performance Team
        '''
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        return False

def send_password_reset_email(email, token):
    """Send password reset email"""
    try:
        msg = Message(
            'Password Reset - Student Performance System',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f'''
        You requested a password reset for your account.
        
        Click the following link to reset your password:
        {request.host_url}reset-password/{token}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, please ignore this email.
        
        Best regards,
        Student Performance Team
        '''
        mail.send(msg)
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        return False

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create new user
        verification_token = generate_secure_token()
        user = User(
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data['role'],
            email_verification_token=verification_token
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        if app.config['MAIL_USERNAME']:
            send_verification_email(data['email'], verification_token)
        
        return jsonify({
            'message': 'Registration successful. Please check your email for verification.',
            'user_id': user.user_id
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        if not user.is_verified:
            return jsonify({'error': 'Please verify your email before logging in'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.user_id)
        refresh_token = create_refresh_token(identity=user.user_id)
        
        # Store session
        session = UserSession(
            user_id=user.user_id,
            token_hash=access_token,
            expires_at=datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(session)
        db.session.commit()
        
        response = jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'user_id': user.user_id,
                'email': user.email,
                'role': user.role
            }
        })
        
        # Set secure cookies
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=3600
        )
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        current_user_id = get_jwt_identity()
        
        # Invalidate session
        UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).update({'is_active': False})
        
        db.session.commit()
        
        response = jsonify({'message': 'Logout successful'})
        response.delete_cookie('access_token')
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({'error': 'Logout failed'}), 500

@app.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        
        # Update session
        UserSession.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).update({
            'token_hash': new_access_token,
            'expires_at': datetime.utcnow() + app.config['JWT_ACCESS_TOKEN_EXPIRES']
        })
        
        db.session.commit()
        
        response = jsonify({
            'access_token': new_access_token
        })
        
        response.set_cookie(
            'access_token',
            new_access_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            max_age=3600
        )
        
        return response, 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return jsonify({'error': 'Token refresh failed'}), 500

@app.route('/api/auth/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Email verification endpoint"""
    try:
        user = User.query.filter_by(email_verification_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid verification token'}), 400
        
        user.is_verified = True
        user.email_verification_token = None
        db.session.commit()
        
        return jsonify({'message': 'Email verified successfully'}), 200
        
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        return jsonify({'error': 'Email verification failed'}), 500

@app.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Password reset request endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Email not found'}), 404
        
        # Generate reset token
        reset_token = generate_secure_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        db.session.commit()
        
        # Send reset email
        if app.config['MAIL_USERNAME']:
            send_password_reset_email(email, reset_token)
        
        return jsonify({'message': 'Password reset email sent'}), 200
        
    except Exception as e:
        logger.error(f"Password reset request error: {e}")
        return jsonify({'error': 'Password reset request failed'}), 500

@app.route('/api/auth/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Password reset endpoint"""
    try:
        data = request.get_json()
        new_password = data.get('new_password')
        
        if not new_password:
            return jsonify({'error': 'New password is required'}), 400
        
        # Validate password strength
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        user = User.query.filter_by(password_reset_token=token).first()
        if not user:
            return jsonify({'error': 'Invalid reset token'}), 400
        
        if user.password_reset_expires < datetime.utcnow():
            return jsonify({'error': 'Reset token has expired'}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'}), 200
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'error': 'Password reset failed'}), 500

# User profile routes
@app.route('/api/users/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = {
            'user_id': user.user_id,
            'email': user.email,
            'role': user.role,
            'is_verified': user.is_verified,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'created_at': user.created_at.isoformat()
        }
        
        # Add role-specific profile data
        if user.role == 'student':
            student_profile = StudentProfile.query.filter_by(user_id=user.user_id).first()
            if student_profile:
                profile_data['student_profile'] = {
                    'student_id': student_profile.student_id,
                    'first_name': student_profile.first_name,
                    'last_name': student_profile.last_name,
                    'gender': student_profile.gender,
                    'age': student_profile.age
                }
        
        return jsonify(profile_data), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

@app.route('/api/users/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data and data['email'] != user.email:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email already in use'}), 409
            
            user.email = data['email']
            user.is_verified = False
            user.email_verification_token = generate_secure_token()
        
        db.session.commit()
        
        # Send verification email if email changed
        if 'email' in data and data['email'] != user.email and app.config['MAIL_USERNAME']:
            send_verification_email(data['email'], user.email_verification_token)
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@app.route('/api/users/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Verify current password
        if not check_password_hash(user.password_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Update password
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        logger.error(f"Change password error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500

# Security middleware
@app.before_request
def security_headers():
    """Add security headers to all responses"""
    response = make_response()
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"

@app.before_request
def rate_limit():
    """Basic rate limiting"""
    # This is a simple implementation. In production, use Redis or similar
    pass

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

# Web interface route
@app.route('/', methods=['GET'])
def index():
    """Serve the main web interface"""
    try:
        with open('static/index.html', 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({'error': 'Web interface not found'}), 404

if __name__ == '__main__':
    # Import and register API routes
    from api_routes import init_app as init_api_routes
    
    with app.app_context():
        db.create_all()
        init_api_routes(app)
    app.run(debug=False, host='0.0.0.0', port=5000)
=======
import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta
import re

# Import our modules
from data.database import db
from auth.login import *
from utils.helpers import *
from pages.dashboard import *
from pages.profile import *
from pages.input_data import *

warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(
    page_title="Student Performance Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .prediction-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #1f77b4;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    
    # Header
    st.markdown('<h1 class="main-header">📚 Student Performance Management System</h1>', unsafe_allow_html=True)
    
    # Check authentication
    if not check_authentication():
        show_auth_pages()
        return
    
    # Get current user
    user = get_current_user()
    
    # Sidebar
    st.sidebar.title(f"Welcome, {user['username']}!")
    st.sidebar.markdown(f"**Role:** {user['role'].title()}")
    
    # Logout button
    if st.sidebar.button("Logout"):
        logout()
    
    # Show notifications in sidebar
    show_notifications_sidebar()
    
    # Navigation based on role
    if user['role'] == 'student':
        pages = [
            "🏠 Dashboard",
            "👤 My Profile", 
            "📊 My Performance",
            "💡 Recommendations",
            "🔔 Notifications",
            "🎯 Predict Performance"
        ]
    elif user['role'] == 'teacher':
        pages = [
            "🏠 Dashboard",
            "👥 Student Management",
            "📝 Add Performance",
            "📅 Attendance",
            "💡 Recommendations",
            "🔔 Notifications",
            "📈 Analytics"
        ]
    else:  # admin
        pages = [
            "🏠 Dashboard",
            "👥 Student Management", 
            "📝 Add Performance",
            "📅 Attendance",
            "💡 Recommendations",
            "🔔 Notifications",
            "📈 Analytics",
            "⚙️ System Settings"
        ]
    
    # Page selection
    page = st.sidebar.selectbox("Navigation", pages)
    
    # Route to appropriate page
    if page == "🏠 Dashboard":
        if user['role'] == 'student':
            # Get student profile to find student_id
            profile = db.get_student_profile(user['id'])
            if profile:
                show_student_dashboard(profile[2])  # student_id
            else:
                st.info("Please complete your profile first.")
        elif user['role'] == 'teacher':
            show_teacher_dashboard()
        else:
            show_admin_dashboard()
    
    elif page == "👤 My Profile":
        show_student_profile_page()
    
    elif page == "👥 Student Management":
        show_student_management_page()
    
    elif page == "📝 Add Performance":
        show_performance_input_page()
    
    elif page == "📅 Attendance":
        show_attendance_input_page()
    
    elif page == "📊 My Performance":
        require_role(['student'])
        profile = db.get_student_profile(user['id'])
        if profile:
            show_student_dashboard(profile[2])
        else:
            st.info("Please complete your profile first.")
    
    elif page == "💡 Recommendations":
        if user['role'] == 'student':
            profile = db.get_student_profile(user['id'])
            if profile:
                show_recommendations_page(profile[2])
            else:
                st.info("Please complete your profile first.")
        else:
            # For teachers/admins, show recommendations for selected student
            if 'selected_student' in st.session_state:
                show_recommendations_for_teacher(st.session_state['selected_student'])
            else:
                st.info("Please select a student from the Student Management page.")
    
    elif page == "🔔 Notifications":
        show_notifications_page()
    
    elif page == "🎯 Predict Performance":
        show_prediction_page()
    
    elif page == "📈 Analytics":
        require_role(['teacher', 'admin'])
        show_analytics_page()
    
    elif page == "⚙️ System Settings":
        require_role(['admin'])
        st.markdown("## ⚙️ System Settings")
        st.info("System settings page - Coming soon!")

if __name__ == "__main__":
    main()
>>>>>>> d36a3f2ff085038a4ab780def49f61e4a0914e9a
