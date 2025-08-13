import streamlit as st
from datetime import datetime
from data.database import db
from auth.login import get_current_user, require_role

def show_performance_input_page():
    """Show performance data input page for teachers"""
    require_role(['teacher', 'admin'])
    
    st.markdown("## 📝 Performance Data Input")
    
    # Get all students
    students = db.get_all_students()
    
    if students.empty:
        st.info("No students found. Please add students first.")
        return
    
    # Select student
    student_options = {f"{row['first_name']} {row['last_name']} ({row['student_id']})": row['student_id'] 
                      for _, row in students.iterrows()}
    selected_student = st.selectbox("Select Student", list(student_options.keys()))
    student_id = student_options[selected_student]
    
    # Performance input form
    with st.form("performance_form"):
        st.subheader("Performance Record")
        
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.selectbox("Subject", ["Mathematics", "Science", "English", "History", "Geography", "Physics", "Chemistry", "Biology"])
            exam_type = st.selectbox("Exam Type", ["Quiz", "Midterm", "Final", "Assignment", "Project"])
            score = st.number_input("Score", min_value=0.0, max_value=100.0, value=75.0, step=0.1)
            max_score = st.number_input("Maximum Score", min_value=1.0, max_value=100.0, value=100.0, step=0.1)
        
        with col2:
            date_taken = st.date_input("Date Taken", value=datetime.now().date())
            notes = st.text_area("Notes (Optional)")
        
        submitted = st.form_submit_button("Add Performance Record")
        
        if submitted:
            user = get_current_user()
            db.add_performance_record(
                student_id=student_id,
                subject=subject,
                exam_type=exam_type,
                score=score,
                max_score=max_score,
                date_taken=date_taken,
                recorded_by=user['id'],
                notes=notes
            )
            st.success("Performance record added successfully!")

def show_attendance_input_page():
    """Show attendance input page for teachers"""
    require_role(['teacher', 'admin'])
    
    st.markdown("## 📅 Attendance Management")
    
    # Get all students
    students = db.get_all_students()
    
    if students.empty:
        st.info("No students found. Please add students first.")
        return
    
    # Select student
    student_options = {f"{row['first_name']} {row['last_name']} ({row['student_id']})": row['student_id'] 
                      for _, row in students.iterrows()}
    selected_student = st.selectbox("Select Student", list(student_options.keys()))
    student_id = student_options[selected_student]
    
    # Attendance input form
    with st.form("attendance_form"):
        st.subheader("Attendance Record")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", value=datetime.now().date())
            status = st.selectbox("Status", ["present", "absent", "late"])
        
        with col2:
            notes = st.text_area("Notes (Optional)")
        
        submitted = st.form_submit_button("Add Attendance Record")
        
        if submitted:
            user = get_current_user()
            db.add_attendance_record(
                student_id=student_id,
                date=date,
                status=status,
                recorded_by=user['id'],
                notes=notes
            )
            st.success("Attendance record added successfully!")
