# Student Performance Prediction System

A comprehensive Flask-based web application for predicting student performance using machine learning. The system includes user authentication, role-based access control, REST API endpoints, and integration with a trained Random Forest model.

## Features

### 🔐 Authentication & Security
- **JWT-based authentication** with access and refresh tokens
- **Role-based access control** (Student, Teacher, Administrator)
- **Email verification** for new registrations
- **Password reset functionality** with secure tokens
- **Session management** with IP tracking
- **Security headers** and CSRF protection
- **Input validation** and sanitization

### 📊 Database Schema
- **PostgreSQL database** with comprehensive schema
- **User management** with role-based permissions
- **Student profiles** with academic and demographic data
- **Performance tracking** with historical records
- **Predictions and recommendations** storage
- **Notifications and alerts** system
- **Optimized indexes** for performance

### 🤖 Machine Learning Integration
- **Pre-trained Random Forest model** for performance prediction
- **Real-time predictions** for individual students
- **Batch prediction** capabilities
- **Model confidence scoring**
- **Feature importance tracking**

### 📈 Analytics & Dashboard
- **Performance analytics** with trend analysis
- **Student demographics** breakdown
- **Academic insights** by various factors
- **Export capabilities** for data analysis
- **Real-time statistics** and metrics

### 🔌 REST API
- **Comprehensive CRUD operations** for all entities
- **Pagination and filtering** for large datasets
- **Input validation** and error handling
- **Proper HTTP status codes** and responses
- **API documentation** with examples

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd student-performance-prediction-system
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Create PostgreSQL Database
```sql
CREATE DATABASE student_performance_db;
CREATE USER student_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE student_performance_db TO student_user;
```

#### Run Database Schema
```bash
psql -U student_user -d student_performance_db -f database_schema.sql
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://student_user:your_password@localhost/student_performance_db

# Email Configuration (for verification emails)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Optional: Redis for session management
REDIS_URL=redis://localhost:6379/0
```

### 6. Data Migration

Import your existing student data:

```bash
python data_migration.py
```

This will:
- Create sample users (admin, teachers, students)
- Import all students from `StudentPerformance.csv`
- Link students to user accounts where possible

## Usage

### Starting the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### Default Users

After running the migration, these users will be available:

| Email | Password | Role |
|-------|----------|------|
| admin@school.edu | Admin123! | Administrator |
| teacher1@school.edu | Teacher123! | Teacher |
| teacher2@school.edu | Teacher123! | Teacher |
| student1@school.edu | Student123! | Student |
| student2@school.edu | Student123! | Student |

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

### Student Management

#### Get All Students (Paginated)
```http
GET /api/students?page=1&per_page=20&search=john&gender=Male&school_type=Public
Authorization: Bearer <access_token>
```

#### Get Student Profile
```http
GET /api/students/STU0001
Authorization: Bearer <access_token>
```

#### Create Student
```http
POST /api/students
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "student_id": "STU9999",
  "first_name": "Jane",
  "last_name": "Smith",
  "gender": "Female",
  "age": 16,
  "attendance": 85,
  "hours_studied": 25,
  "previous_scores": 78
}
```

#### Update Student
```http
PUT /api/students/STU0001
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "attendance": 90,
  "hours_studied": 30
}
```

### Performance Prediction

#### Get Prediction for Student
```http
GET /api/predictions/STU0001
Authorization: Bearer <access_token>
```

Response:
```json
{
  "student_id": "STU0001",
  "predicted_score": 82.5,
  "confidence_level": 0.85,
  "prediction_date": "2024-01-15T10:30:00Z",
  "model_version": "v1.0"
}
```

#### Batch Predictions
```http
POST /api/predictions/batch
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "student_ids": ["STU0001", "STU0002", "STU0003"]
}
```

### Analytics

#### Get Overview Analytics
```http
GET /api/analytics/overview
Authorization: Bearer <access_token>
```

#### Get Performance Trends
```http
GET /api/analytics/performance-trends
Authorization: Bearer <access_token>
```

### Data Import/Export

#### Import CSV Data
```http
POST /api/data/import
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <csv_file>
```

#### Export Data
```http
GET /api/data/export
Authorization: Bearer <access_token>
```

## Role-Based Access Control

### Student Role
- View own profile and predictions
- Update personal information
- Access basic analytics

### Teacher Role
- View all student profiles
- Create and update student records
- Generate predictions for students
- Access detailed analytics
- Export student data

### Administrator Role
- Full system access
- User management
- Data import/export
- System configuration
- Delete student records

## Security Features

### Authentication Security
- **JWT tokens** with configurable expiration
- **Password hashing** using bcrypt
- **Email verification** for new accounts
- **Password reset** with secure tokens
- **Session tracking** with IP and user agent

### API Security
- **Input validation** and sanitization
- **SQL injection prevention** with ORM
- **XSS protection** with security headers
- **CSRF protection** with secure cookies
- **Rate limiting** (basic implementation)

### Data Security
- **Encrypted passwords** in database
- **Secure session storage**
- **Role-based permissions**
- **Audit logging** for sensitive operations

## Database Schema

The system uses a comprehensive PostgreSQL schema with the following main tables:

- **users**: Authentication and user management
- **student_profiles**: Student demographic and academic data
- **teachers**: Teacher information and specializations
- **administrators**: Admin user details
- **performance_records**: Historical performance tracking
- **predictions**: ML model predictions
- **recommendations**: Student improvement suggestions
- **notifications**: System notifications and alerts
- **alerts**: Performance alerts and warnings
- **user_sessions**: Session management

## Machine Learning Model

The system integrates with a pre-trained Random Forest model (`random_forest_student_performance_model.pkl`) that predicts student performance based on:

- **Demographic factors**: Age, gender, family income
- **Academic factors**: Previous scores, attendance, study hours
- **Environmental factors**: School type, parental involvement, resources
- **Health factors**: Sleep hours, physical activity
- **Social factors**: Peer influence, extracurricular activities

## Development

### Project Structure
```
student-performance-prediction-system/
├── app.py                 # Main Flask application
├── api_routes.py          # REST API endpoints
├── database_schema.sql    # PostgreSQL schema
├── data_migration.py      # Data import script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── StudentPerformance.csv # Student dataset
└── random_forest_student_performance_model.pkl # ML model
```

### Adding New Features

1. **New API Endpoints**: Add to `api_routes.py`
2. **Database Changes**: Update `database_schema.sql`
3. **Model Updates**: Replace the pickle file and update feature mapping
4. **Security**: Ensure proper role-based access control

### Testing

```bash
# Run the application
python app.py

# Test API endpoints
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@school.edu", "password": "Admin123!"}'
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use proper secrets management
2. **Database**: Use production PostgreSQL with proper backups
3. **Email**: Configure production SMTP server
4. **SSL/TLS**: Enable HTTPS with proper certificates
5. **Monitoring**: Add logging and monitoring
6. **Backup**: Regular database and model backups

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Troubleshooting

### Common Issues

1. **Database Connection**: Check PostgreSQL service and credentials
2. **Model Loading**: Ensure the pickle file is in the correct location
3. **Email Configuration**: Verify SMTP settings for email verification
4. **Permission Errors**: Check file permissions for CSV and model files

### Logs

The application logs to stdout. Check for error messages and debug information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API examples

---

**Note**: This is a production-ready system with comprehensive security features. Always change default passwords and secrets before deployment.
