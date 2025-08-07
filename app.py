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
