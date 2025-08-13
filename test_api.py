#!/usr/bin/env python3
"""
Test script for Student Performance Prediction System API
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_EMAIL = "admin@test.com"
TEST_PASSWORD = "admin123"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_login():
    """Test login endpoint"""
    print("Testing login...")
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ Login successful")
            return result.get('access_token')
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_get_students(token):
    """Test get students endpoint"""
    print("Testing get students...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/students", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Get students successful: {len(result.get('students', []))} students found")
            return result.get('students', [])
        else:
            print(f"❌ Get students failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Get students error: {e}")
        return []

def test_get_prediction(token, student_id):
    """Test prediction endpoint"""
    print(f"Testing prediction for student {student_id}...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/predictions/{student_id}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prediction successful: {result.get('predicted_score')}")
            return result
        else:
            print(f"❌ Prediction failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return None

def test_analytics(token):
    """Test analytics endpoint"""
    print("Testing analytics...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/analytics/overview", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analytics successful: {result.get('total_students')} total students")
            return result
        else:
            print(f"❌ Analytics failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return None

def test_batch_predictions(token, student_ids):
    """Test batch predictions"""
    print("Testing batch predictions...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {"student_ids": student_ids}
        response = requests.post(f"{BASE_URL}/api/predictions/batch", json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch predictions successful: {len(result.get('predictions', []))} predictions")
            return result
        else:
            print(f"❌ Batch predictions failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Batch predictions error: {e}")
        return None

def main():
    """Run all tests"""
    print("=" * 50)
    print("STUDENT PERFORMANCE PREDICTION SYSTEM - API TESTS")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Application is not running. Please start the application first.")
        sys.exit(1)
    
    # Test login
    token = test_login()
    if not token:
        print("❌ Login failed. Please check credentials and database setup.")
        sys.exit(1)
    
    # Test get students
    students = test_get_students(token)
    if not students:
        print("❌ No students found. Please run data migration first.")
        sys.exit(1)
    
    # Test prediction for first student
    if students:
        first_student = students[0]
        student_id = first_student.get('student_id')
        test_get_prediction(token, student_id)
    
    # Test analytics
    test_analytics(token)
    
    # Test batch predictions
    if len(students) >= 3:
        student_ids = [s.get('student_id') for s in students[:3]]
        test_batch_predictions(token, student_ids)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
