import streamlit as st
import pandas as pd
import numpy as np
import pickle
import warnings

warnings.filterwarnings('ignore')

@st.cache_resource
def load_models():
    """Load all trained models and preprocessing objects"""
    try:
        # Load models
        with open('model_data/rf_performance_classifier.pkl', 'rb') as f:
            classifier = pickle.load(f)
        
        with open('model_data/rf_grade_predictor.pkl', 'rb') as f:
            regressor = pickle.load(f)
        
        # Load preprocessing objects
        with open('model_data/label_encoders.pkl', 'rb') as f:
            label_encoders = pickle.load(f)
        
        with open('model_data/scaler_classifier.pkl', 'rb') as f:
            scaler_classifier = pickle.load(f)
        
        with open('model_data/scaler_regressor.pkl', 'rb') as f:
            scaler_regressor = pickle.load(f)
        
        with open('model_data/feature_importance.pkl', 'rb') as f:
            feature_importance = pickle.load(f)
        
        return classifier, regressor, label_encoders, scaler_classifier, scaler_regressor, feature_importance
    except Exception as e:
        st.error(f"Error loading models: {str(e)}")
        return None, None, None, None, None, None

@st.cache_data
def load_data():
    """Load the dataset"""
    try:
        df = pd.read_csv('model_data/cleaned_dataset.csv')
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def preprocess_input(data_dict, label_encoders):
    """Preprocess input data for prediction"""
    # Create DataFrame from input
    df_input = pd.DataFrame([data_dict])
    
    # Encode categorical variables
    for col, encoder in label_encoders.items():
        if col in df_input.columns:
            # Handle unseen categories
            if df_input[col].iloc[0] in encoder.classes_:
                df_input[col] = encoder.transform([df_input[col].iloc[0]])
            else:
                # Use most frequent category for unseen values
                df_input[col] = encoder.transform([encoder.classes_[0]])
    
    return df_input

def make_predictions(input_data, classifier, regressor, label_encoders, scaler_classifier, scaler_regressor):
    """Make predictions using both models"""
    try:
        # Preprocess input
        processed_input = preprocess_input(input_data, label_encoders)
        
        # Scale features for classifier
        scaled_input_classifier = scaler_classifier.transform(processed_input)
        
        # Scale features for regressor
        scaled_input_regressor = scaler_regressor.transform(processed_input)
        
        # Make predictions
        performance_category = classifier.predict(scaled_input_classifier)[0]
        predicted_score = regressor.predict(scaled_input_regressor)[0]
        
        # Get prediction probabilities for classifier
        performance_probs = classifier.predict_proba(scaled_input_classifier)[0]
        
        return performance_category, predicted_score, performance_probs
    except Exception as e:
        st.error(f"Error making predictions: {str(e)}")
        return None, None, None

def get_performance_label(category):
    """Convert numeric category to label"""
    labels = {0: "At Risk", 1: "Average", 2: "High Performance"}
    return labels.get(category, "Unknown")
