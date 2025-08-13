-- Student Performance Prediction System Database Schema
-- PostgreSQL Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_role AS ENUM ('student', 'teacher', 'administrator');
CREATE TYPE gender_type AS ENUM ('Male', 'Female');
CREATE TYPE feedback_level AS ENUM ('Low', 'Medium', 'High');
CREATE TYPE involvement_level AS ENUM ('Low', 'Medium', 'High');
CREATE TYPE resource_level AS ENUM ('Low', 'Medium', 'High');
CREATE TYPE activity_status AS ENUM ('Yes', 'No');
CREATE TYPE internet_access AS ENUM ('Yes', 'No');
CREATE TYPE income_level AS ENUM ('Low', 'Medium', 'High');
CREATE TYPE school_type AS ENUM ('Public', 'Private');
CREATE TYPE peer_influence AS ENUM ('Positive', 'Negative', 'Neutral');
CREATE TYPE disability_status AS ENUM ('Yes', 'No');
CREATE TYPE education_level AS ENUM ('High School', 'College', 'Postgraduate');
CREATE TYPE distance_level AS ENUM ('Near', 'Moderate', 'Far');
CREATE TYPE notification_type AS ENUM ('performance_alert', 'prediction_update', 'system_notification');
CREATE TYPE notification_status AS ENUM ('unread', 'read', 'archived');

-- Users table (for authentication and role management)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Student profiles table
CREATE TABLE student_profiles (
    student_id VARCHAR(20) PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender gender_type,
    age INTEGER CHECK (age >= 10 AND age <= 25),
    teacher_feedback feedback_level,
    attendance INTEGER CHECK (attendance >= 0 AND attendance <= 100),
    hours_studied INTEGER CHECK (hours_studied >= 0 AND hours_studied <= 50),
    previous_scores INTEGER CHECK (previous_scores >= 0 AND previous_scores <= 100),
    parental_involvement involvement_level,
    access_to_resources resource_level,
    extracurricular_activities activity_status,
    sleep_hours INTEGER CHECK (sleep_hours >= 0 AND sleep_hours <= 24),
    physical_activity INTEGER CHECK (physical_activity >= 0 AND physical_activity <= 10),
    internet_access internet_access,
    tutoring_sessions INTEGER CHECK (tutoring_sessions >= 0 AND tutoring_sessions <= 10),
    family_income income_level,
    school_type school_type,
    peer_influence peer_influence,
    learning_disabilities disability_status,
    parental_education_level education_level,
    distance_from_home distance_level,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teachers table
CREATE TABLE teachers (
    teacher_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    subject_specialization VARCHAR(100),
    years_of_experience INTEGER CHECK (years_of_experience >= 0),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Administrators table
CREATE TABLE administrators (
    admin_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    access_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance records table (for tracking historical performance)
CREATE TABLE performance_records (
    record_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(20) REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    exam_type VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    score INTEGER CHECK (score >= 0 AND score <= 100),
    max_score INTEGER DEFAULT 100,
    exam_date DATE NOT NULL,
    teacher_id UUID REFERENCES teachers(teacher_id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignments table
CREATE TABLE assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100) NOT NULL,
    due_date DATE NOT NULL,
    max_score INTEGER DEFAULT 100,
    teacher_id UUID REFERENCES teachers(teacher_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assignment submissions table
CREATE TABLE assignment_submissions (
    submission_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assignment_id UUID REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    student_id VARCHAR(20) REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    score INTEGER CHECK (score >= 0),
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feedback TEXT,
    graded_by UUID REFERENCES teachers(teacher_id)
);

-- Participation records table
CREATE TABLE participation_records (
    participation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(20) REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    participation_date DATE NOT NULL,
    participation_score INTEGER CHECK (participation_score >= 0 AND participation_score <= 100),
    notes TEXT,
    recorded_by UUID REFERENCES teachers(teacher_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predictions table (for storing ML model predictions)
CREATE TABLE predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(20) REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    predicted_score DECIMAL(5,2) CHECK (predicted_score >= 0 AND predicted_score <= 100),
    confidence_level DECIMAL(3,2) CHECK (confidence_level >= 0 AND confidence_level <= 1),
    prediction_date DATE NOT NULL,
    model_version VARCHAR(50),
    features_used JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Recommendations table
CREATE TABLE recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(20) REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    recommendation_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    priority_level INTEGER CHECK (priority_level >= 1 AND priority_level <= 5),
    is_implemented BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    notification_type notification_type NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status notification_status DEFAULT 'unread',
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP
);

-- Alerts table (for performance alerts)
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id VARCHAR(20) REFERENCES student_profiles(student_id) ON DELETE CASCADE,
    alert_type VARCHAR(100) NOT NULL,
    severity_level INTEGER CHECK (severity_level >= 1 AND severity_level <= 5),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(user_id),
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User sessions table (for session management)
CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for optimal performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX idx_performance_records_student_id ON performance_records(student_id);
CREATE INDEX idx_performance_records_exam_date ON performance_records(exam_date);
CREATE INDEX idx_predictions_student_id ON predictions(student_id);
CREATE INDEX idx_predictions_date ON predictions(prediction_date);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_alerts_student_id ON alerts(student_id);
CREATE INDEX idx_alerts_resolved ON alerts(is_resolved);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(token_hash);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_profiles_updated_at BEFORE UPDATE ON student_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teachers_updated_at BEFORE UPDATE ON teachers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_administrators_updated_at BEFORE UPDATE ON administrators
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assignments_updated_at BEFORE UPDATE ON assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at BEFORE UPDATE ON recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE VIEW student_performance_summary AS
SELECT 
    sp.student_id,
    sp.first_name,
    sp.last_name,
    sp.gender,
    sp.age,
    AVG(pr.score) as average_score,
    COUNT(pr.record_id) as total_exams,
    MAX(pr.exam_date) as last_exam_date,
    p.predicted_score as latest_prediction,
    p.confidence_level
FROM student_profiles sp
LEFT JOIN performance_records pr ON sp.student_id = pr.student_id
LEFT JOIN predictions p ON sp.student_id = p.student_id 
    AND p.prediction_date = (SELECT MAX(prediction_date) FROM predictions WHERE student_id = sp.student_id)
GROUP BY sp.student_id, sp.first_name, sp.last_name, sp.gender, sp.age, p.predicted_score, p.confidence_level;

CREATE VIEW active_alerts_summary AS
SELECT 
    sp.student_id,
    sp.first_name,
    sp.last_name,
    COUNT(a.alert_id) as active_alerts,
    MAX(a.severity_level) as highest_severity
FROM student_profiles sp
LEFT JOIN alerts a ON sp.student_id = a.student_id AND a.is_resolved = FALSE
GROUP BY sp.student_id, sp.first_name, sp.last_name;

-- Sample data insertion queries for testing
-- Insert sample users
INSERT INTO users (email, password_hash, role, is_verified) VALUES
('admin@school.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8eO', 'administrator', TRUE),
('teacher1@school.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8eO', 'teacher', TRUE),
('student1@school.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8eO', 'student', TRUE);

-- Insert sample student profiles (based on your dataset)
INSERT INTO student_profiles (
    student_id, user_id, first_name, last_name, gender, age, teacher_feedback,
    attendance, hours_studied, previous_scores, parental_involvement,
    access_to_resources, extracurricular_activities, sleep_hours, physical_activity,
    internet_access, tutoring_sessions, family_income, school_type, peer_influence,
    learning_disabilities, parental_education_level, distance_from_home
) VALUES
('STU0001', (SELECT user_id FROM users WHERE email = 'student1@school.edu'), 'John', 'Doe', 'Male', 18, 'Medium', 84, 23, 73, 'Low', 'High', 'No', 7, 3, 'Yes', 0, 'Low', 'Public', 'Positive', 'No', 'High School', 'Near'),
('STU0002', NULL, 'Jane', 'Smith', 'Female', 17, 'Medium', 64, 19, 59, 'Low', 'Medium', 'No', 8, 4, 'Yes', 2, 'Medium', 'Public', 'Negative', 'No', 'College', 'Moderate'),
('STU0003', NULL, 'Mike', 'Johnson', 'Male', 15, 'Medium', 98, 24, 91, 'Medium', 'Medium', 'Yes', 7, 4, 'Yes', 2, 'Medium', 'Public', 'Neutral', 'No', 'Postgraduate', 'Near');

-- Insert sample teachers
INSERT INTO teachers (user_id, first_name, last_name, subject_specialization, years_of_experience, department) VALUES
((SELECT user_id FROM users WHERE email = 'teacher1@school.edu'), 'Sarah', 'Wilson', 'Mathematics', 8, 'Science');

-- Insert sample administrators
INSERT INTO administrators (user_id, first_name, last_name, department, access_level) VALUES
((SELECT user_id FROM users WHERE email = 'admin@school.edu'), 'Robert', 'Brown', 'Administration', 'Full');

-- Insert sample performance records
INSERT INTO performance_records (student_id, exam_type, subject, score, exam_date, teacher_id) VALUES
('STU0001', 'Midterm', 'Mathematics', 85, '2024-01-15', (SELECT teacher_id FROM teachers LIMIT 1)),
('STU0001', 'Final', 'Mathematics', 78, '2024-02-15', (SELECT teacher_id FROM teachers LIMIT 1)),
('STU0002', 'Midterm', 'Mathematics', 72, '2024-01-15', (SELECT teacher_id FROM teachers LIMIT 1));

-- Insert sample predictions
INSERT INTO predictions (student_id, predicted_score, confidence_level, prediction_date, model_version) VALUES
('STU0001', 82.5, 0.85, CURRENT_DATE, 'v1.0'),
('STU0002', 68.3, 0.72, CURRENT_DATE, 'v1.0'),
('STU0003', 89.1, 0.91, CURRENT_DATE, 'v1.0');

-- Insert sample recommendations
INSERT INTO recommendations (student_id, recommendation_type, title, description, priority_level) VALUES
('STU0001', 'Study Strategy', 'Increase Study Hours', 'Consider increasing study hours from 23 to 30 hours per week to improve performance', 3),
('STU0002', 'Attendance', 'Improve Attendance', 'Current attendance of 64% needs improvement. Aim for at least 85%', 4);

-- Insert sample notifications
INSERT INTO notifications (user_id, notification_type, title, message, related_entity_type, related_entity_id) VALUES
((SELECT user_id FROM users WHERE email = 'student1@school.edu'), 'prediction_update', 'New Performance Prediction', 'Your predicted score has been updated to 82.5', 'prediction', (SELECT prediction_id FROM predictions WHERE student_id = 'STU0001' LIMIT 1));

-- Insert sample alerts
INSERT INTO alerts (student_id, alert_type, severity_level, title, description) VALUES
('STU0002', 'Low Attendance', 3, 'Attendance Alert', 'Student attendance has dropped below 70%', 'STU0001', 'Performance Decline', 2, 'Performance Alert', 'Recent scores show a declining trend');
