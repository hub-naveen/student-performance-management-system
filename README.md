# 📚 Student Performance Management System

A comprehensive web application built with Streamlit for managing and analyzing student performance data using machine learning.

## 🚀 Features

### 🔐 Authentication & Role-Based Access
- **Student Portal**: View personal performance, predictions, and recommendations
- **Teacher Portal**: Manage student data, input performance records, and view analytics
- **Admin Portal**: Full system access, user management, and comprehensive analytics

### 🤖 Machine Learning Capabilities
- **Performance Classification**: Predicts if a student is "At Risk", "Average", or "High Performance"
- **Grade Prediction**: Estimates numerical scores based on various factors
- **Personalized Recommendations**: AI-generated suggestions for improvement

### 📊 Analytics & Visualization
- Interactive dashboards with Plotly charts
- Performance trends and comparisons
- Attendance tracking and analysis
- Subject-wise performance breakdown

### 📝 Data Management
- Student profile management
- Performance record tracking
- Attendance monitoring
- Notification system
- Recommendation engine

## 🏗️ Project Structure

```
StudentPerformanceApp/
├── app.py                    # Main Streamlit entry point
├── setup.py                  # Database initialization script
├── student_performance.db    # SQLite database
├── model_data/              # ML model files (.pkl, .csv)
├── model/
│   └── predictor.py         # ML logic and model handling
├── auth/
│   └── login.py            # Authentication system
├── data/
│   └── database.py         # Database schema and queries
├── pages/
│   ├── dashboard.py        # Dashboard pages
│   ├── profile.py          # Profile management
│   └── input_data.py       # Data input pages
├── utils/
│   └── helpers.py          # Utility functions
├── assets/
│   └── style.css           # Custom CSS styling
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd StudentPerformanceApp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database** (optional - sample data included)
   ```bash
   python setup.py
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   Open your browser and go to: `http://localhost:8501`

## 🔐 Default Login Credentials

### Students
- **Username:** `student1` | **Password:** `Student123!`
- **Username:** `student2` | **Password:** `Student123!`
- **Username:** `student3` | **Password:** `Student123!`

### Teachers
- **Username:** `teacher1` | **Password:** `Teacher123!`
- **Username:** `teacher2` | **Password:** `Teacher123!`

### Admin
- **Username:** `admin1` | **Password:** `Admin123!`

## 🎯 Key Features by Role

### 👨‍🎓 Student Features
- View personal performance dashboard
- Access performance predictions
- Receive personalized recommendations
- Track attendance history
- View notifications

### 👨‍🏫 Teacher Features
- Manage student profiles
- Input performance records
- Track attendance
- View class analytics
- Generate performance reports
- Send notifications to students

### 👨‍💼 Admin Features
- Full system administration
- User management
- Comprehensive analytics
- System-wide reports
- Database management

## 🤖 Machine Learning Models

The application uses two trained Random Forest models:

1. **Performance Classifier**: Categorizes students into performance levels
2. **Grade Predictor**: Predicts numerical scores

### Model Features
- Study time
- Previous scores
- Attendance rate
- Parental education level
- Internet access
- Family support
- And more...

## 📊 Technologies Used

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: SQLite
- **ML Framework**: scikit-learn
- **Visualization**: Plotly
- **Authentication**: bcrypt
- **Data Processing**: Pandas, NumPy

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_PATH=student_performance.db
MODEL_PATH=model_data/
```

### Customization
- Modify `assets/style.css` for custom styling
- Update `data/database.py` for database schema changes
- Adjust ML models in `model/predictor.py`

## 📈 Performance Metrics

The ML models achieve:
- **Classification Accuracy**: ~85%
- **Regression R² Score**: ~0.78
- **Prediction Confidence**: High for most cases

## 🚀 Deployment

### Local Deployment
```bash
streamlit run app.py
```

### Cloud Deployment
The application can be deployed on:
- Streamlit Cloud
- Heroku
- AWS
- Google Cloud Platform

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- scikit-learn for ML capabilities
- Plotly for interactive visualizations
- The educational community for feedback and testing

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Made with ❤️ for Educational Excellence** 