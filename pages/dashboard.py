import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from data.database import db

def show_student_dashboard(student_id):
    """Show student dashboard with performance analytics"""
    st.markdown("## 📊 Student Dashboard")
    
    # Get student performance data
    performance_data = db.get_student_performance(student_id)
    attendance_data = db.get_student_attendance(student_id)
    performance_summary = db.get_performance_summary(student_id)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not performance_data.empty:
            avg_score = performance_data['score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}%")
        else:
            st.metric("Average Score", "N/A")
    
    with col2:
        if not performance_data.empty:
            total_exams = len(performance_data)
            st.metric("Total Exams", total_exams)
        else:
            st.metric("Total Exams", "0")
    
    with col3:
        if not attendance_data.empty:
            attendance_rate = (len(attendance_data[attendance_data['status'] == 'present']) / len(attendance_data)) * 100
            st.metric("Attendance Rate", f"{attendance_rate:.1f}%")
        else:
            st.metric("Attendance Rate", "N/A")
    
    with col4:
        if not performance_data.empty:
            recent_trend = performance_data.head(5)['score'].mean() - performance_data.tail(5)['score'].mean()
            trend_icon = "📈" if recent_trend > 0 else "📉"
            st.metric("Recent Trend", f"{trend_icon} {abs(recent_trend):.1f}%")
        else:
            st.metric("Recent Trend", "N/A")
    
    st.divider()
    
    # Performance over time
    if not performance_data.empty:
        st.subheader("📈 Performance Over Time")
        
        # Convert date_taken to datetime for better plotting
        performance_data['date_taken'] = pd.to_datetime(performance_data['date_taken'])
        
        fig = px.line(performance_data, x='date_taken', y='score', 
                     title="Score Trend Over Time",
                     labels={'date_taken': 'Date', 'score': 'Score (%)'})
        fig.update_layout(xaxis_title="Date", yaxis_title="Score (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Subject-wise performance
        if not performance_summary.empty:
            st.subheader("📚 Performance by Subject")
            
            fig = px.bar(performance_summary, x='subject', y='avg_score',
                        title="Average Score by Subject",
                        labels={'subject': 'Subject', 'avg_score': 'Average Score (%)'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Attendance chart
    if not attendance_data.empty:
        st.subheader("📅 Attendance Overview")
        
        attendance_data['date'] = pd.to_datetime(attendance_data['date'])
        attendance_by_month = attendance_data.groupby(attendance_data['date'].dt.to_period('M')).agg({
            'status': lambda x: (x == 'present').sum() / len(x) * 100
        }).reset_index()
        attendance_by_month['date'] = attendance_by_month['date'].astype(str)
        
        fig = px.line(attendance_by_month, x='date', y='status',
                     title="Monthly Attendance Rate",
                     labels={'date': 'Month', 'status': 'Attendance Rate (%)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("🕒 Recent Activity")
    
    if not performance_data.empty:
        recent_exams = performance_data.head(5)
        
        for _, exam in recent_exams.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{exam['subject']} - {exam['exam_type']}**")
                    st.markdown(f"*{exam['date_taken']}*")
                
                with col2:
                    st.metric("Score", f"{exam['score']:.1f}%")
                
                with col3:
                    if exam['score'] >= 90:
                        st.markdown("🟢 Excellent")
                    elif exam['score'] >= 80:
                        st.markdown("🟡 Good")
                    elif exam['score'] >= 70:
                        st.markdown("🟠 Average")
                    else:
                        st.markdown("🔴 Needs Improvement")
            
            st.divider()

def show_teacher_dashboard():
    """Show teacher dashboard with class analytics"""
    st.markdown("## 👨‍🏫 Teacher Dashboard")
    
    # Get all students
    students = db.get_all_students()
    
    if students.empty:
        st.info("No students found in the system.")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = len(students)
        st.metric("Total Students", total_students)
    
    with col2:
        # Calculate average performance across all students
        all_performance = []
        for _, student in students.iterrows():
            student_perf = db.get_student_performance(student['student_id'])
            if not student_perf.empty:
                all_performance.append(student_perf['score'].mean())
        
        if all_performance:
            class_avg = sum(all_performance) / len(all_performance)
            st.metric("Class Average", f"{class_avg:.1f}%")
        else:
            st.metric("Class Average", "N/A")
    
    with col3:
        # Count students at risk (assuming recent performance < 70)
        at_risk_count = 0
        for _, student in students.iterrows():
            student_perf = db.get_student_performance(student['student_id'])
            if not student_perf.empty and student_perf['score'].mean() < 70:
                at_risk_count += 1
        
        st.metric("Students at Risk", at_risk_count)
    
    with col4:
        # Average attendance
        all_attendance = []
        for _, student in students.iterrows():
            student_attendance = db.get_student_attendance(student['student_id'])
            if not student_attendance.empty:
                attendance_rate = (len(student_attendance[student_attendance['status'] == 'present']) / len(student_attendance)) * 100
                all_attendance.append(attendance_rate)
        
        if all_attendance:
            avg_attendance = sum(all_attendance) / len(all_attendance)
            st.metric("Avg Attendance", f"{avg_attendance:.1f}%")
        else:
            st.metric("Avg Attendance", "N/A")
    
    st.divider()
    
    # Class performance distribution
    st.subheader("📊 Class Performance Distribution")
    
    all_scores = []
    for _, student in students.iterrows():
        student_perf = db.get_student_performance(student['student_id'])
        if not student_perf.empty:
            all_scores.extend(student_perf['score'].tolist())
    
    if all_scores:
        fig = px.histogram(x=all_scores, nbins=20,
                          title="Distribution of All Student Scores",
                          labels={'x': 'Score (%)', 'y': 'Number of Exams'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Student list with performance
    st.subheader("👥 Student Performance Overview")
    
    student_performance_data = []
    for _, student in students.iterrows():
        student_perf = db.get_student_performance(student['student_id'])
        student_attendance = db.get_student_attendance(student['student_id'])
        
        avg_score = student_perf['score'].mean() if not student_perf.empty else None
        attendance_rate = None
        if not student_attendance.empty:
            attendance_rate = (len(student_attendance[student_attendance['status'] == 'present']) / len(student_attendance)) * 100
        
        student_performance_data.append({
            'student_id': student['student_id'],
            'name': f"{student['first_name']} {student['last_name']}",
            'avg_score': avg_score,
            'attendance_rate': attendance_rate,
            'total_exams': len(student_perf) if not student_perf.empty else 0
        })
    
    performance_df = pd.DataFrame(student_performance_data)
    
    if not performance_df.empty:
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            min_score = st.slider("Minimum Score", 0, 100, 0)
        
        with col2:
            min_attendance = st.slider("Minimum Attendance", 0, 100, 0)
        
        # Apply filters
        filtered_df = performance_df[
            (performance_df['avg_score'] >= min_score) &
            (performance_df['attendance_rate'] >= min_attendance)
        ]
        
        # Display student table
        for _, student in filtered_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{student['name']}**")
                    st.markdown(f"*{student['student_id']}*")
                
                with col2:
                    if student['avg_score'] is not None:
                        st.metric("Avg Score", f"{student['avg_score']:.1f}%")
                    else:
                        st.metric("Avg Score", "N/A")
                
                with col3:
                    if student['attendance_rate'] is not None:
                        st.metric("Attendance", f"{student['attendance_rate']:.1f}%")
                    else:
                        st.metric("Attendance", "N/A")
                
                with col4:
                    st.metric("Exams", student['total_exams'])
            
            st.divider()

def show_admin_dashboard():
    """Show admin dashboard with system analytics"""
    st.markdown("## ⚙️ Admin Dashboard")
    
    # System overview
    students = db.get_all_students()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = len(students)
        st.metric("Total Students", total_students)
    
    with col2:
        # Count by grade level
        if not students.empty:
            grade_counts = students['grade_level'].value_counts()
            most_common_grade = grade_counts.index[0] if not grade_counts.empty else "N/A"
            st.metric("Most Common Grade", most_common_grade)
        else:
            st.metric("Most Common Grade", "N/A")
    
    with col3:
        # Gender distribution
        if not students.empty:
            gender_counts = students['gender'].value_counts()
            st.metric("Male Students", gender_counts.get('Male', 0))
        else:
            st.metric("Male Students", 0)
    
    with col4:
        if not students.empty:
            st.metric("Female Students", gender_counts.get('Female', 0))
        else:
            st.metric("Female Students", 0)
    
    st.divider()
    
    # Data quality metrics
    st.subheader("📊 Data Quality Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance records count
        total_performance_records = 0
        for _, student in students.iterrows():
            student_perf = db.get_student_performance(student['student_id'])
            total_performance_records += len(student_perf)
        
        st.metric("Total Performance Records", total_performance_records)
    
    with col2:
        # Average records per student
        if total_students > 0:
            avg_records = total_performance_records / total_students
            st.metric("Avg Records per Student", f"{avg_records:.1f}")
        else:
            st.metric("Avg Records per Student", "0")
    
    # Grade level distribution
    if not students.empty:
        st.subheader("📚 Grade Level Distribution")
        
        grade_counts = students['grade_level'].value_counts()
        fig = px.pie(values=grade_counts.values, names=grade_counts.index,
                     title="Students by Grade Level")
        st.plotly_chart(fig, use_container_width=True)
    
    # Gender distribution
    if not students.empty:
        st.subheader("👥 Gender Distribution")
        
        gender_counts = students['gender'].value_counts()
        fig = px.bar(x=gender_counts.index, y=gender_counts.values,
                     title="Students by Gender",
                     labels={'x': 'Gender', 'y': 'Number of Students'})
        st.plotly_chart(fig, use_container_width=True)

def show_analytics_page():
    """Show general analytics page"""
    st.markdown("## 📈 Analytics Dashboard")
    
    # Get all data
    students = db.get_all_students()
    
    if students.empty:
        st.info("No data available for analytics.")
        return
    
    # Performance analytics
    st.subheader("🎯 Performance Analytics")
    
    all_performance_data = []
    for _, student in students.iterrows():
        student_perf = db.get_student_performance(student['student_id'])
        if not student_perf.empty:
            for _, record in student_perf.iterrows():
                all_performance_data.append({
                    'student_id': student['student_id'],
                    'student_name': f"{student['first_name']} {student['last_name']}",
                    'subject': record['subject'],
                    'score': record['score'],
                    'exam_type': record['exam_type'],
                    'date_taken': record['date_taken']
                })
    
    if all_performance_data:
        performance_df = pd.DataFrame(all_performance_data)
        
        # Overall performance trends
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            fig = px.histogram(performance_df, x='score', nbins=20,
                              title="Overall Score Distribution",
                              labels={'score': 'Score (%)', 'y': 'Number of Exams'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Performance by subject
            subject_avg = performance_df.groupby('subject')['score'].mean().sort_values(ascending=False)
            fig = px.bar(x=subject_avg.index, y=subject_avg.values,
                        title="Average Performance by Subject",
                        labels={'x': 'Subject', 'y': 'Average Score (%)'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance trends over time
        st.subheader("📈 Performance Trends")
        
        performance_df['date_taken'] = pd.to_datetime(performance_df['date_taken'])
        monthly_avg = performance_df.groupby(performance_df['date_taken'].dt.to_period('M'))['score'].mean()
        
        fig = px.line(x=monthly_avg.index.astype(str), y=monthly_avg.values,
                     title="Monthly Average Performance",
                     labels={'x': 'Month', 'y': 'Average Score (%)'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Attendance analytics
    st.subheader("📅 Attendance Analytics")
    
    all_attendance_data = []
    for _, student in students.iterrows():
        student_attendance = db.get_student_attendance(student['student_id'])
        if not student_attendance.empty:
            for _, record in student_attendance.iterrows():
                all_attendance_data.append({
                    'student_id': student['student_id'],
                    'student_name': f"{student['first_name']} {student['last_name']}",
                    'status': record['status'],
                    'date': record['date']
                })
    
    if all_attendance_data:
        attendance_df = pd.DataFrame(all_attendance_data)
        
        # Attendance status distribution
        status_counts = attendance_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                     title="Attendance Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
