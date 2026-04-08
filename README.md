# University Academic Performance Management & Early Warning System

**Chinese Name:** 大学生学习成绩中英文管理和预警系统  
**English Name:** Bilingual University Academic Performance Management and Early Warning System

A comprehensive Django-based university management system with three integrated portals (Admin, Teacher, Student), featuring bilingual support (English/Chinese), real-time performance analytics, and an AI-powered early warning system for student academic risk assessment.

## Features

### Core Features

- **Bilingual Interface**: Full English and Chinese language support
- **Academic Performance Management**: GPA/CGPA calculation, grade tracking, semester summaries
- **Early Warning System**: AI-powered risk assessment with configurable rules
- **Attendance Tracking**: Daily attendance recording and percentage calculation
- **Report Generation**: PDF transcripts, Excel/CSV exports, performance reports
- **Role-Based Access Control**: Secure authentication with admin, teacher, and student roles
- **Audit Logging**: Complete activity tracking for compliance
- **Notifications**: Real-time alerts for grades, warnings, and announcements

## Technology Stack

- **Backend**: Django 5, Python 3.12+
- **Database**: MySQL 8
- **Frontend**: Django Templates, Bootstrap 5, Chart.js
- **Task Queue**: Celery + Redis (optional)
- **Authentication**: Django auth with custom User model
- **Forms**: Django Crispy Forms with Bootstrap 5
- **Reports**: ReportLab (PDF), openpyxl (Excel)

## Project Structure

```
university_system/
├── apps/
│   ├── accounts/          # User authentication and profiles
│   ├── core/              # Core services, context processors, portal views
│   ├── departments/       # Department management
│   ├── programs/          # Program/major and curriculum management
│   ├── semesters/         # Academic semester management
│   ├── students/          # Student profiles and records
│   ├── teachers/          # Teacher profiles and records
│   ├── courses/           # Course and course offering management
│   ├── enrollments/       # Student enrollment management
│   ├── attendance/        # Attendance tracking
│   ├── assessments/       # Assessment components and scores
│   ├── results/           # Final grades and GPA calculations
│   ├── warnings/          # Early warning system
│   ├── announcements/     # System announcements
│   ├── notifications/     # User notifications
│   ├── reports/           # Report generation
│   ├── auditlogs/         # Audit logging
│   └── settings_app/      # System settings
├── config/                # Django configuration
├── templates/             # HTML templates
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded files
├── locale/                # Translation files
├── requirements/          # Dependency requirements
├── DB/                    # Database scripts and seeding
└── logs/                  # Application logs
```

## Installation

### Prerequisites

- Python 3.12+
- MySQL 8
- Redis (optional, for Celery)

### Setup Steps

1. **Clone the repository and navigate to the project:**
   ```bash
   cd university_system
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements/base.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Create the MySQL database:**
   ```sql
   CREATE DATABASE university_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create a superuser (admin):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Seed production data (optional - creates demo data):**
   
   The project includes a production data seeder that creates:
   - 5 Departments (Computer Science, Engineering, Business, Mathematics, Physics)
   - 3 Programs (BCS, BEE, MBA)
   - 2 Semesters (Fall 2024 active, Spring 2025)
   - 6 Courses with offerings
   - 3 Teachers
   - 20 Students with enrollments
   - Assessment components and warning rules
   
   ```bash
   python DB/reset_and_seed_production.py
   ```
   
   **Default credentials after seeding:**
   - Admin: `admin@university.edu` / `Admin123!`
   - Teachers: `zhang.prof@university.edu` / `Teacher123!`
   - Students: `student001@university.edu` / `Student123!`

9. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

10. **Access the application:**
    - Landing page: http://127.0.0.1:8000/
    - Admin login: http://127.0.0.1:8000/auth/login/
    - Django admin: http://127.0.0.1:8000/admin/

## Initial Setup

### Creating Admin User

The system requires an admin user to be created via the command line:

```bash
python manage.py createsuperuser
```

Enter email, full name, and password when prompted.

### Creating Student and Teacher Accounts

1. Log in as admin
2. Navigate to Admin Portal > Users
3. Click "Create User"
4. Select role (Student or Teacher)
5. Fill in details - account will be created with "pending" status
6. The system generates an activation token
7. Provide the activation token to the student/teacher
8. They can activate their account at `/auth/activate/`

### Setting Up Departments and Programs

1. Go to Admin Portal > Departments
2. Create departments with bilingual names
3. Go to Admin Portal > Programs
4. Create programs linked to departments

### Setting Up Semesters

1. Go to Admin Portal > Semesters
2. Create academic semesters with start/end dates
3. Mark the current semester as "active"

### Setting Up Courses

1. Go to Admin Portal > Courses
2. Create courses with credit hours, type, and prerequisites
3. Go to Admin Portal > Course Offerings
4. Create offerings for specific semesters with assigned teachers

### Configuring Grade Policy

1. Go to Admin Portal > Settings > Grade Policy
2. Configure passing thresholds, warning levels, and grade mappings

### Configuring Warning Rules

1. Go to Admin Portal > Warnings > Rules
2. Set up risk calculation rules for:
   - Attendance threshold
   - GPA thresholds
   - Course failure counts
   - Missing assessments
   - GPA trend monitoring

## Usage

### For Administrators

- **Dashboard**: View system-wide statistics and at-risk student alerts
- **User Management**: Create and manage student/teacher accounts
- **Academic Setup**: Configure departments, programs, courses, semesters
- **Enrollment Management**: Bulk enroll students in courses
- **Warning System**: Run risk calculations and view warning reports
- **Reports**: Generate institutional performance reports

### For Teachers

- **Dashboard**: View assigned courses and at-risk students
- **My Courses**: Manage course details and enrolled students
- **Attendance**: Record daily attendance for classes
- **Marks Entry**: Enter scores for assessment components
- **Grade Submission**: Submit final grades for approval
- **At-Risk Students**: View and intervene with struggling students
- **Analytics**: View class performance metrics

### For Students

- **Dashboard**: View current GPA, CGPA, warning level, and announcements
- **My Courses**: View enrolled courses and course details
- **My Results**: View grades and performance history
- **GPA/CGPA**: Track academic progress over semesters
- **Attendance**: View attendance records per course
- **Warning Center**: View risk alerts and recommendations
- **Transcript**: Download official academic transcript

## Early Warning System

The system uses a weighted risk score algorithm:

**Risk Score Formula:**
```
Risk Score = (0.25 × Attendance Risk) +
             (0.25 × Course Failure Risk) +
             (0.20 × GPA Risk) +
             (0.10 × Trend Risk) +
             (0.10 × Missing Assessment Risk) +
             (0.10 × Teacher Flag Risk)
```

**Warning Levels:**
- **Green (0-24)**: Stable performance
- **Yellow (25-49)**: Mild warning - monitoring recommended
- **Orange (50-74)**: Serious warning - intervention required
- **Red (75-100)**: Critical warning - immediate action needed

## Authentication Flow

1. **Admin**: Created via command line, logs in with email/password
2. **Teacher/Student**: 
   - Admin creates account (status: pending)
   - Activation token generated
   - User activates account at `/auth/activate/`
   - User sets password and account becomes active
   - User can then log in normally

## API Endpoints

### Authentication
- `POST /auth/login/` - User login
- `GET /auth/logout/` - User logout
- `POST /auth/activate/` - Account activation
- `POST /auth/password-reset/` - Password reset request

### Reports (for future API expansion)
- `GET /reports/transcript/<student_id>/`
- `GET /reports/semester-report/<student_id>/<semester_id>/`
- `GET /reports/course-report/<offering_id>/`

## Database Schema

The system includes comprehensive models for:
- Users and roles
- Departments and programs
- Courses and curriculum
- Semesters and academic calendar
- Teachers and students
- Enrollments and attendance
- Assessments and grades
- GPA/CGPA calculations
- Early warnings and interventions
- Notifications and announcements
- Audit logs

See individual app `models.py` files for detailed schema.

## Security Features

- Password hashing with Django's PBKDF2
- CSRF protection on all forms
- Role-based access control with custom decorators
- Audit logging for all critical actions
- Session-based authentication
- Secure password validation
- Account activation workflow

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is proprietary software for academic use.

## Support

For technical support or questions, please contact the system administrator.

## Deployment

### Preparing for Production

1. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

2. **Install production dependencies:**
   ```bash
   pip install -r requirements/prod.txt
   ```

3. **Collect static files:**
   ```bash
   python manage.py collectstatic
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Seed production data (optional):**
   ```bash
   python DB/reset_and_seed_production.py
   ```

### Deployment Options

#### Option 1: PythonAnywhere (Free Tier Available)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload code via Git or file upload
3. Create virtual environment and install requirements
4. Configure WSGI file
5. Set up MySQL database
6. Configure static files

#### Option 2: Railway (Recommended)

1. Push code to GitHub
2. Sign up at [railway.app](https://railway.app)
3. Create new project → Deploy from GitHub repo
4. Add MySQL database
5. Set environment variables
6. Railway auto-deploys on every git push

#### Option 3: VPS (DigitalOcean, AWS, etc.)

1. Set up server with Python, MySQL, Nginx
2. Clone repository
3. Configure Gunicorn as WSGI server
4. Set up Nginx as reverse proxy
5. Configure SSL certificate (Let's Encrypt)
6. Set up systemd services for auto-start

### Production Checklist

- [ ] Set `DEBUG=False` in environment
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up SSL/HTTPS
- [ ] Configure email settings for notifications
- [ ] Set up automated backups for database
- [ ] Configure log rotation
- [ ] Set up monitoring (optional)

## Acknowledgments

Built with Django, Bootstrap 5, and Chart.js.
