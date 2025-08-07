# 📚 Student Performance Management System

A comprehensive Streamlit web application for predicting and improving student academic performance with role-based access, real-time analytics, and personalized recommendations.

## 🚀 Features

### ✅ **User Authentication & Management**
- **Secure Login/Registration**: bcrypt-hashed passwords with email validation
- **Role-Based Access**: Students, Teachers, and Admins with different permissions
- **Session Management**: Secure user sessions with automatic logout

### ✅ **Student Profile Management**
- **Complete Profiles**: Students can create/edit profiles with academic history
- **Profile Validation**: Input validation and data integrity checks
- **Academic Records**: Track grades, attendance, and performance metrics

### ✅ **Performance Data Management**
- **Teacher Input**: Teachers can enter student scores, attendance, and notes
- **Multiple Subjects**: Support for various subjects and exam types
- **Historical Tracking**: Complete performance history with trends
- **Data Validation**: Input sanitization and validation

### ✅ **ML Prediction System**
- **Dual Model Architecture**: 
  - Random Forest Classifier for performance categories (At Risk, Average, High Performance)
  - Random Forest Regressor for score prediction
- **Real-time Predictions**: Instant results with confidence levels
- **Feature Importance**: Model insights and interpretability

### ✅ **Personalized Recommendations**
- **AI-Generated**: Based on performance predictions and student data
- **Priority Levels**: High, Medium, Low priority recommendations
- **Actionable Items**: Specific, actionable improvement suggestions
- **Progress Tracking**: Mark recommendations as completed

### ✅ **Smart Notifications**
- **Real-time Alerts**: Students see alerts for upcoming deadlines and weak areas
- **Teacher Alerts**: Teachers get notifications for students at risk
- **Performance Notifications**: Automatic alerts based on performance trends
- **Attendance Warnings**: Low attendance notifications

### ✅ **Advanced Analytics Dashboard**
- **Role-Specific Dashboards**: Different views for students, teachers, and admins
- **Interactive Charts**: Plotly-powered visualizations
- **Performance Trends**: Time-series analysis and trend detection
- **Class Analytics**: Teacher views of class performance
- **System Analytics**: Admin views of system-wide metrics

### ✅ **Modern UI/UX**
- **Dark Theme**: Clean, modern interface
- **Responsive Design**: Works on desktop and mobile
- **Sidebar Navigation**: Easy navigation with role-based menus
- **Real-time Updates**: Live data updates and notifications

## 🛠️ Tech Stack

- **Frontend/UI**: Streamlit with custom CSS
- **Backend**: Python with SQLite database
- **Authentication**: bcrypt password hashing
- **ML Models**: scikit-learn Random Forest
- **Visualization**: Plotly for interactive charts
- **Data Processing**: Pandas and NumPy
- **Deployment**: Streamlit Cloud ready

## 📋 Pages & Features by Role

### 👨‍🎓 **Student Features**
- **Dashboard**: Personal performance overview with charts
- **Profile Management**: Edit personal information
- **Performance Tracking**: View grades and attendance
- **Recommendations**: Personalized improvement suggestions
- **Notifications**: Real-time alerts and updates
- **Predictions**: Try performance prediction tool

### 👨‍🏫 **Teacher Features**
- **Class Dashboard**: Overview of all students
- **Student Management**: View and manage student profiles
- **Performance Input**: Add grades and attendance records
- **Analytics**: Class performance analysis
- **Recommendations**: Generate and track student recommendations
- **Notifications**: Alerts for at-risk students

### ⚙️ **Admin Features**
- **System Dashboard**: Overall system analytics
- **User Management**: Manage all users and roles
- **Data Analytics**: System-wide performance metrics
- **Settings**: System configuration options

## 🛠️ Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure your model files are in the correct location**:
   ```
   MODEL_1/
   ├── rf_performance_classifier.pkl
   ├── rf_grade_predictor.pkl
   ├── label_encoders.pkl
   ├── scaler_classifier.pkl
   ├── scaler_regressor.pkl
   ├── feature_importance.pkl
   └── cleaned_dataset.csv
   ```

## 🚀 Running the Application

1. **Navigate to the project directory**:
   ```bash
   cd Student-Performance
   ```

2. **Run the main application**:
   ```bash
   streamlit run main_app.py
   ```

3. **Open your browser** and go to the URL shown in the terminal (usually `http://localhost:8501`)

## 📊 How to Use

### 🔐 **Getting Started**
1. **Register**: Create an account with your role (student/teacher/admin)
2. **Login**: Use your credentials to access the system
3. **Complete Profile**: Students should complete their profile information

### 🎯 **Making Predictions**
1. Navigate to "🎯 Predict Performance"
2. Fill in student information:
   - **Demographics**: Gender, Age
   - **Academic Factors**: Teacher Feedback, Attendance, Hours Studied
   - **Support Factors**: Parental Involvement, Access to Resources
   - **Lifestyle**: Sleep Hours, Physical Activity, Extracurricular Activities
   - **Environmental**: Internet Access, Family Income, School Type
3. Click "🚀 Predict Performance" to get results
4. View predicted performance category and score with confidence levels

### 📝 **Adding Performance Data (Teachers)**
1. Navigate to "📝 Add Performance"
2. Select a student from the dropdown
3. Fill in subject, exam type, score, and date
4. Add optional notes
5. Submit to save the record

### 📅 **Managing Attendance (Teachers)**
1. Navigate to "📅 Attendance"
2. Select a student and date
3. Mark attendance status (present/absent/late)
4. Add optional notes
5. Submit to save the record

### 💡 **Using Recommendations**
1. Navigate to "💡 Recommendations"
2. View current recommendations for the student
3. Filter by priority level
4. Mark recommendations as completed
5. Generate new recommendations based on latest data

## 🎯 Prediction Features

The application predicts:

1. **Performance Category**:
   - **At Risk** (< 60% confidence)
   - **Average** (60-80% confidence)
   - **High Performance** (> 80% confidence)

2. **Predicted Score**: Numerical score out of 100

3. **Confidence Levels**: Probability distribution across all categories

4. **Personalized Recommendations**: Based on prediction results

## 📈 Analytics Features

### **Student Analytics**
- Performance trends over time
- Subject-wise performance breakdown
- Attendance patterns
- Recent activity tracking

### **Teacher Analytics**
- Class performance overview
- Student comparison tools
- Risk assessment metrics
- Performance distribution analysis

### **Admin Analytics**
- System-wide metrics
- User activity tracking
- Data quality metrics
- Grade level and gender distributions

## 🔧 Database Schema

The system uses SQLite with the following tables:

- **users**: User accounts and authentication
- **student_profiles**: Student personal information
- **performance_records**: Academic performance data
- **attendance_records**: Attendance tracking
- **notifications**: System notifications
- **recommendations**: Personalized recommendations

## 🎨 UI Features

- **Responsive Design**: Works on desktop and mobile devices
- **Interactive Visualizations**: Plotly charts for data exploration
- **Real-time Updates**: Live data updates and notifications
- **Error Handling**: Graceful handling of missing data and errors
- **Caching**: Efficient loading of models and data
- **Custom Styling**: Modern, clean interface with custom CSS

## 🔧 Troubleshooting

### Common Issues

1. **Model Loading Error**:
   - Ensure all `.pkl` files are in the `MODEL_1/` directory
   - Check file permissions

2. **Missing Dependencies**:
   ```bash
   pip install --upgrade streamlit pandas numpy scikit-learn plotly bcrypt
   ```

3. **Database Issues**:
   - The system automatically creates the database on first run
   - Check file permissions for the database file

4. **Port Already in Use**:
   ```bash
   streamlit run main_app.py --server.port 8502
   ```

5. **Authentication Issues**:
   - Clear browser cache and cookies
   - Restart the Streamlit server

## 📝 File Structure

```
Student-Performance/
├── main_app.py              # Main Streamlit application
├── database.py              # Database management module
├── auth.py                  # Authentication module
├── notifications.py         # Notifications system
├── recommendations.py       # Recommendations engine
├── dashboard.py             # Analytics dashboard
├── app.py                   # Original prediction app
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── MODEL_1/                # Model files and data
    ├── rf_performance_classifier.pkl
    ├── rf_grade_predictor.pkl
    ├── label_encoders.pkl
    ├── scaler_classifier.pkl
    ├── scaler_regressor.pkl
    ├── feature_importance.pkl
    ├── cleaned_dataset.csv
    └── model_training.ipynb
```

## 🔒 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **Input Validation**: Comprehensive input sanitization
- **Role-Based Access**: Secure permission system
- **Session Management**: Secure user sessions
- **SQL Injection Protection**: Parameterized queries

## 🚀 Deployment

### Streamlit Cloud
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Deploy automatically

### Local Deployment
```bash
streamlit run main_app.py --server.port 8501 --server.address 0.0.0.0
```

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the application
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure you have the necessary permissions for any data used.

## 🆘 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Verify all model files are present
3. Ensure all dependencies are installed
4. Check the console for error messages
5. Review the database connection

---

**Happy Learning! 🎓📊**

*Built with ❤️ using Streamlit, Python, and Machine Learning* 