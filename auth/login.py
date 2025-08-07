import streamlit as st
import re
from data.database import db

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
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Username is valid"

def login_page():
    """Display login page"""
    st.markdown("## 🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return None
            
            user = db.authenticate_user(username, password)
            if user:
                st.success(f"Welcome back, {user['username']}!")
                st.session_state['user'] = user
                st.session_state['authenticated'] = True
                st.rerun()
            else:
                st.error("Invalid username or password")
                return None
    
    # Link to registration
    st.markdown("Don't have an account? [Register here](#register)")

def register_page():
    """Display registration page"""
    st.markdown("## 📝 Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        role = st.selectbox("Role", ["student", "teacher", "admin"])
        
        submitted = st.form_submit_button("Register")
        
        if submitted:
            # Validate inputs
            if not all([username, email, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            # Validate username
            username_valid, username_msg = validate_username(username)
            if not username_valid:
                st.error(username_msg)
                return
            
            # Validate email
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            # Validate password
            password_valid, password_msg = validate_password(password)
            if not password_valid:
                st.error(password_msg)
                return
            
            # Check password confirmation
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            # Create user
            success = db.create_user(username, email, password, role)
            if success:
                st.success("Registration successful! Please login.")
                st.session_state['show_login'] = True
            else:
                st.error("Username or email already exists")
    
    # Link to login
    st.markdown("Already have an account? [Login here](#login)")

def logout():
    """Logout user"""
    if 'user' in st.session_state:
        del st.session_state['user']
    if 'authenticated' in st.session_state:
        del st.session_state['authenticated']
    st.rerun()

def check_authentication():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        return False
    return True

def get_current_user():
    """Get current user information"""
    if check_authentication():
        return st.session_state.get('user')
    return None

def require_auth():
    """Decorator to require authentication"""
    if not check_authentication():
        st.error("Please login to access this page")
        st.stop()

def require_role(required_roles):
    """Decorator to require specific role(s)"""
    require_auth()
    user = get_current_user()
    if user['role'] not in required_roles:
        st.error("You don't have permission to access this page")
        st.stop()

def show_auth_pages():
    """Show authentication pages based on session state"""
    if 'show_login' in st.session_state and st.session_state['show_login']:
        del st.session_state['show_login']
        login_page()
    else:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            login_page()
        
        with tab2:
            register_page()
