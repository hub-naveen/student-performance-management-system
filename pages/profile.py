import streamlit as st
from data.database import db
from auth.login import get_current_user

def show_student_profile_page():
    """Show student profile management page"""
    user = get_current_user()
    if not user:
        return
    
    st.markdown("## 👤 Student Profile")
    
    # Get existing profile
    profile = db.get_student_profile(user['id'])
    
    if profile:
        st.success("Profile found! You can edit your information below.")
        
        # Display current profile
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Student ID:** {profile[2]}")
            st.markdown(f"**Name:** {profile[3]} {profile[4]}")
        
        with col2:
            st.markdown(f"**Age:** {profile[5]}")
            st.markdown(f"**Gender:** {profile[6]}")
    
    # Profile form
    with st.form("profile_form"):
        st.subheader("Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=profile[3] if profile else "")
            last_name = st.text_input("Last Name", value=profile[4] if profile else "")
            age = st.number_input("Age", min_value=10, max_value=25, value=profile[5] if profile else 16)
            gender = st.selectbox("Gender", ["Male", "Female"], index=0 if not profile or profile[6] == "Male" else 1)
        
        with col2:
            grade_level = st.selectbox("Grade Level", ["9th", "10th", "11th", "12th"], 
                                     index=0 if not profile else ["9th", "10th", "11th", "12th"].index(profile[7]))
            school_name = st.text_input("School Name", value=profile[8] if profile else "")
            student_id = st.text_input("Student ID", value=profile[2] if profile else "")
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            if not all([first_name, last_name, student_id, school_name]):
                st.error("Please fill in all required fields")
                return
            
            student_data = {
                'student_id': student_id,
                'first_name': first_name,
                'last_name': last_name,
                'age': age,
                'gender': gender,
                'grade_level': grade_level,
                'school_name': school_name
            }
            
            db.create_student_profile(user['id'], student_data)
            st.success("Profile saved successfully!")

def show_student_management_page():
    """Show student management page for teachers/admins"""
    from auth.login import require_role
    require_role(['teacher', 'admin'])
    
    st.markdown("## 👥 Student Management")
    
    # Get all students
    students = db.get_all_students()
    
    if students.empty:
        st.info("No students found in the system.")
        return
    
    # Search and filter
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search by name or ID")
    
    with col2:
        grade_filter = st.selectbox("Filter by grade", ["All"] + list(students['grade_level'].unique()))
    
    # Apply filters
    filtered_students = students.copy()
    
    if search_term:
        filtered_students = filtered_students[
            filtered_students['first_name'].str.contains(search_term, case=False) |
            filtered_students['last_name'].str.contains(search_term, case=False) |
            filtered_students['student_id'].str.contains(search_term, case=False)
        ]
    
    if grade_filter != "All":
        filtered_students = filtered_students[filtered_students['grade_level'] == grade_filter]
    
    # Display students
    for _, student in filtered_students.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.markdown(f"**{student['first_name']} {student['last_name']}**")
                st.markdown(f"*{student['student_id']}*")
            
            with col2:
                st.markdown(f"**Grade:** {student['grade_level']}")
                st.markdown(f"**Age:** {student['age']}")
            
            with col3:
                st.markdown(f"**Gender:** {student['gender']}")
                st.markdown(f"**School:** {student['school_name']}")
            
            with col4:
                if st.button(f"View Details", key=f"view_{student['student_id']}"):
                    st.session_state['selected_student'] = student['student_id']
                    st.rerun()
                
                if st.button(f"Add Performance", key=f"perf_{student['student_id']}"):
                    st.session_state['add_performance_for'] = student['student_id']
                    st.rerun()
        
        st.divider()
