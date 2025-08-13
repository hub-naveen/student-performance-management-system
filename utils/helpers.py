import streamlit as st
from datetime import datetime, timedelta
from data.database import db
from model.predictor import load_models, make_predictions, get_performance_label

def show_notifications_sidebar():
    """Show notifications in sidebar"""
    user = st.session_state.get('user')
    if not user:
        return
    
    notifications = db.get_user_notifications(user['id'], unread_only=True)
    
    if not notifications.empty:
        st.sidebar.markdown("### 🔔 Notifications")
        
        for _, notification in notifications.iterrows():
            with st.sidebar.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    if notification['type'] == 'warning':
                        st.markdown("⚠️")
                    elif notification['type'] == 'error':
                        st.markdown("🚨")
                    elif notification['type'] == 'success':
                        st.markdown("✅")
                    else:
                        st.markdown("ℹ️")
                
                with col2:
                    st.markdown(f"**{notification['title']}**")
                    st.markdown(f"*{notification['message']}*")
                    
                    if st.button(f"Mark as read", key=f"read_{notification['id']}"):
                        db.mark_notification_read(notification['id'])
                        st.rerun()

def show_notifications_page():
    """Show full notifications page"""
    user = st.session_state.get('user')
    if not user:
        st.error("Please login to view notifications")
        return
    
    st.markdown("## 🔔 Notifications")
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        show_read = st.checkbox("Show read notifications", value=False)
    
    with col2:
        notification_type = st.selectbox(
            "Filter by type",
            ["All", "info", "warning", "error", "success"]
        )
    
    # Get notifications
    notifications = db.get_user_notifications(user['id'], unread_only=False)
    
    if not show_read:
        notifications = notifications[notifications['is_read']]
    
    if notification_type != "All":
        notifications = notifications[notifications['type'] == notification_type]
    
    if notifications.empty:
        st.info("No notifications found.")
        return
    
    # Display notifications
    for _, notification in notifications.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                if notification['type'] == 'warning':
                    st.markdown("⚠️")
                elif notification['type'] == 'error':
                    st.markdown("🚨")
                elif notification['type'] == 'success':
                    st.markdown("✅")
                else:
                    st.markdown("ℹ️")
            
            with col2:
                st.markdown(f"**{notification['title']}**")
                st.markdown(notification['message'])
                st.markdown(f"*{notification['created_at']}*")
            
            with col3:
                if not notification['is_read']:
                    if st.button("Mark as read", key=f"read_full_{notification['id']}"):
                        db.mark_notification_read(notification['id'])
                        st.rerun()
        
        st.divider()

def generate_performance_recommendations(student_id, performance_category, predicted_score, feature_importance=None):
    """Generate personalized recommendations based on performance prediction"""
    recommendations = []
    
    if performance_category == 0:  # At Risk
        recommendations.extend([
            {
                "type": "academic_support",
                "title": "Seek Academic Support",
                "description": "Consider meeting with a tutor or academic advisor to develop a study plan.",
                "priority": "high"
            },
            {
                "type": "study_habits",
                "title": "Improve Study Habits",
                "description": "Create a structured study schedule and find a quiet, dedicated study space.",
                "priority": "high"
            },
            {
                "type": "attendance",
                "title": "Improve Attendance",
                "description": "Regular attendance is crucial for academic success. Aim for 90%+ attendance.",
                "priority": "medium"
            },
            {
                "type": "resources",
                "title": "Access Learning Resources",
                "description": "Utilize school library, online resources, and educational apps for additional support.",
                "priority": "medium"
            }
        ])
    
    elif performance_category == 1:  # Average
        recommendations.extend([
            {
                "type": "goal_setting",
                "title": "Set Specific Goals",
                "description": "Set clear, achievable academic goals and track your progress regularly.",
                "priority": "medium"
            },
            {
                "type": "study_techniques",
                "title": "Enhance Study Techniques",
                "description": "Try different study methods like active recall, spaced repetition, and mind mapping.",
                "priority": "medium"
            },
            {
                "type": "time_management",
                "title": "Improve Time Management",
                "description": "Use a planner or digital tools to organize your time effectively.",
                "priority": "medium"
            }
        ])
    
    else:  # High Performance
        recommendations.extend([
            {
                "type": "advanced_learning",
                "title": "Pursue Advanced Learning",
                "description": "Consider taking advanced courses or participating in academic competitions.",
                "priority": "low"
            },
            {
                "type": "mentorship",
                "title": "Become a Mentor",
                "description": "Share your knowledge by helping other students who may be struggling.",
                "priority": "low"
            },
            {
                "type": "leadership",
                "title": "Develop Leadership Skills",
                "description": "Take on leadership roles in school clubs or academic organizations.",
                "priority": "low"
            }
        ])
    
    # Add specific recommendations based on predicted score
    if predicted_score < 70:
        recommendations.append({
            "type": "foundation",
            "title": "Strengthen Foundation",
            "description": "Focus on building strong fundamentals in core subjects.",
            "priority": "high"
        })
    
    elif predicted_score > 90:
        recommendations.append({
            "type": "excellence",
            "title": "Maintain Excellence",
            "description": "Continue your excellent work and consider challenging yourself further.",
            "priority": "low"
        })
    
    return recommendations

def save_recommendations_to_db(student_id, recommendations):
    """Save recommendations to database"""
    for rec in recommendations:
        db.add_recommendation(
            student_id=student_id,
            recommendation_type=rec["type"],
            title=rec["title"],
            description=rec["description"],
            priority=rec["priority"]
        )

def show_recommendations_page(student_id=None):
    """Display recommendations page"""
    user = st.session_state.get('user')
    if not user:
        st.error("Please login to view recommendations")
        return
    
    # If no student_id provided, use current user's student profile
    if not student_id and user['role'] == 'student':
        profile = db.get_student_profile(user['id'])
        if profile:
            student_id = profile[2]  # student_id column
    
    if not student_id:
        st.error("No student ID found")
        return
    
    st.markdown("## 💡 Personalized Recommendations")
    
    # Get existing recommendations
    recommendations = db.get_student_recommendations(student_id)
    
    if not recommendations.empty:
        st.subheader("📋 Current Recommendations")
        
        # Filter by priority
        priority_filter = st.selectbox("Filter by priority", ["All", "high", "medium", "low"])
        
        filtered_recs = recommendations
        if priority_filter != "All":
            filtered_recs = recommendations[recommendations['priority'] == priority_filter]
        
        for _, rec in filtered_recs.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    if rec['priority'] == 'high':
                        st.markdown("🔴")
                    elif rec['priority'] == 'medium':
                        st.markdown("🟡")
                    else:
                        st.markdown("🟢")
                
                with col2:
                    st.markdown(f"**{rec['title']}**")
                    st.markdown(rec['description'])
                    st.markdown(f"*Type: {rec['recommendation_type']}*")
                
                with col3:
                    if not rec['is_completed']:
                        if st.button("Mark Complete", key=f"complete_{rec['id']}"):
                            # Update completion status
                            conn = db.get_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE recommendations SET is_completed = TRUE WHERE id = ?', (rec['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
                    else:
                        st.markdown("✅ Complete")
        
        st.divider()
    
    # Generate new recommendations
    st.subheader("🎯 Generate New Recommendations")
    
    if st.button("Generate Recommendations"):
        # This would typically use actual student data
        # For demo purposes, we'll use sample data
        sample_recommendations = generate_performance_recommendations(
            student_id, 1, 75  # Average performance
        )
        
        save_recommendations_to_db(student_id, sample_recommendations)
        st.success("New recommendations generated!")
        st.rerun()

def show_recommendations_for_teacher(student_id):
    """Show recommendations for a specific student (teacher view)"""
    st.markdown(f"## 💡 Recommendations for Student {student_id}")
    
    recommendations = db.get_student_recommendations(student_id)
    
    if recommendations.empty:
        st.info("No recommendations found for this student.")
        return
    
    # Summary statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_recs = len(recommendations)
        st.metric("Total Recommendations", total_recs)
    
    with col2:
        completed_recs = len(recommendations[recommendations['is_completed']])
        st.metric("Completed", completed_recs)
    
    with col3:
        completion_rate = (completed_recs / total_recs * 100) if total_recs > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Display recommendations
    for _, rec in recommendations.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 1])
            
            with col1:
                if rec['priority'] == 'high':
                    st.markdown("🔴")
                elif rec['priority'] == 'medium':
                    st.markdown("🟡")
                else:
                    st.markdown("🟢")
            
            with col2:
                st.markdown(f"**{rec['title']}**")
                st.markdown(rec['description'])
                st.markdown(f"*Priority: {rec['priority']} | Type: {rec['recommendation_type']}*")
            
            with col3:
                if rec['is_completed']:
                    st.markdown("✅ Complete")
                else:
                    st.markdown("⏳ Pending")
        
        st.divider()

def show_prediction_page():
    """Show ML prediction page"""
    st.markdown("## 🎯 Performance Prediction")
    
    # Load models
    classifier, regressor, label_encoders, scaler_classifier, scaler_regressor, feature_importance = load_models()
    
    if classifier is None:
        st.error("Failed to load models. Please check the model files.")
        return
    
    # Create input form
    with st.form("prediction_form"):
        st.subheader("Student Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            age = st.slider("Age", 15, 20, 16)
            teacher_feedback = st.selectbox("Teacher Feedback", ["Low", "Medium", "High"])
            attendance = st.slider("Attendance (%)", 50, 100, 85)
            hours_studied = st.slider("Hours Studied", 5, 35, 20)
            previous_scores = st.slider("Previous Scores", 30, 100, 75)
        
        with col2:
            parental_involvement = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
            access_to_resources = st.selectbox("Access to Resources", ["Low", "Medium", "High"])
            extracurricular_activities = st.selectbox("Extracurricular Activities", ["No", "Yes"])
            sleep_hours = st.slider("Sleep Hours", 4, 12, 7)
            physical_activity = st.slider("Physical Activity (hours/week)", 0, 10, 3)
            internet_access = st.selectbox("Internet Access", ["No", "Yes"])
        
        col3, col4 = st.columns(2)
        
        with col3:
            tutoring_sessions = st.slider("Tutoring Sessions", 0, 10, 1)
            family_income = st.selectbox("Family Income", ["Low", "Medium", "High"])
            school_type = st.selectbox("School Type", ["Public", "Private"])
            peer_influence = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"])
        
        with col4:
            learning_disabilities = st.selectbox("Learning Disabilities", ["No", "Yes"])
            parental_education = st.selectbox("Parental Education Level", 
                                           ["High School", "College", "Postgraduate"])
            distance_from_home = st.selectbox("Distance from Home", ["Near", "Moderate", "Far"])
        
        submitted = st.form_submit_button("🚀 Predict Performance")
        
        if submitted:
            # Prepare input data
            input_data = {
                'Gender': gender,
                'age': age,
                'Teacher_Feedback': teacher_feedback,
                'Attendance': attendance,
                'Hours_Studied': hours_studied,
                'Previous_Scores': previous_scores,
                'Parental_Involvement': parental_involvement,
                'Access_to_Resources': access_to_resources,
                'Extracurricular_Activities': extracurricular_activities,
                'Sleep_Hours': sleep_hours,
                'Physical_Activity': physical_activity,
                'Physical_Activity.1': 'Low' if physical_activity <= 2 else 'Medium' if physical_activity <= 4 else 'High',
                'Internet_Access': internet_access,
                'Tutoring_Sessions': tutoring_sessions,
                'Family_Income': family_income,
                'School_Type': school_type,
                'Peer_Influence': peer_influence,
                'Learning_Disabilities': learning_disabilities,
                'Parental_Education_Level': parental_education,
                'Distance_from_Home': distance_from_home
            }
            
            # Make predictions
            performance_category, predicted_score, performance_probs = make_predictions(
                input_data, classifier, regressor, label_encoders, scaler_classifier, scaler_regressor
            )
            
            if performance_category is not None:
                # Display results
                st.markdown("---")
                st.markdown("## 📊 Prediction Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                    st.markdown(f"### 🎯 Performance Category")
                    performance_label = get_performance_label(performance_category)
                    
                    # Color coding for performance categories
                    if performance_category == 0:
                        st.error(f"**At Risk** ({performance_probs[0]:.1%} confidence)")
                    elif performance_category == 1:
                        st.warning(f"**Average** ({performance_probs[1]:.1%} confidence)")
                    else:
                        st.success(f"**High Performance** ({performance_probs[2]:.1%} confidence)")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                    st.markdown(f"### 📈 Predicted Score")
                    st.metric("Score", f"{predicted_score:.1f}/100")
                    
                    # Score interpretation
                    if predicted_score >= 80:
                        st.success("Excellent performance expected!")
                    elif predicted_score >= 60:
                        st.warning("Average performance expected.")
                    else:
                        st.error("Performance needs improvement.")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Generate recommendations
                if st.button("Generate Recommendations"):
                    recommendations = generate_performance_recommendations(
                        "STU0001", performance_category, predicted_score
                    )
                    save_recommendations_to_db("STU0001", recommendations)
                    st.success("Recommendations generated! Check the Recommendations page.")
