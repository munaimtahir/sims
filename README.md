# SIMS - Specialized Information Management System

A comprehensive Django web application for managing postgraduate medical residents' academic and training records.

## Features

- **User Management**: Role-based access control for admins, supervisors, and postgraduate students
- **Rotations**: Track and manage training rotations across different departments
- **Certificates**: Manage and track certifications and achievements
- **Logbook**: Digital logbook for recording training activities and evaluations
- **Clinical Cases**: Submit, review, and manage clinical cases with detailed documentation

## Quick Start

### 1. Install Dependencies
```powershell
py -m pip install -r requirements.txt
```

### 2. Run Database Migrations (if needed)
```powershell
py manage.py migrate
```

### 3. Create Superuser and Test Setup
```powershell
py test_setup.py
```

### 4. Start Development Server
```powershell
py manage.py runserver
```

### 5. Access the Application
- **Main Application**: http://127.0.0.1:8000
- **Admin Interface**: http://127.0.0.1:8000/admin
  - Username: `admin`
  - Password: `admin123`

## Project Structure

```
sims_project/
├── manage.py
├── requirements.txt
├── sims_project/          # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── sims/                  # SIMS applications
│   ├── users/            # User management and authentication
│   ├── rotations/        # Training rotation management
│   ├── certificates/     # Certification tracking
│   ├── logbook/          # Digital logbook functionality
│   └── cases/            # Clinical case management
├── templates/            # Global templates
├── static/              # Static files (CSS, JS, images)
└── media/               # User uploaded files
```

## User Roles

1. **Admin**: Full system access, user management, system configuration
2. **Supervisor**: Manage assigned residents, review cases and logbook entries
3. **Postgraduate (PG)**: Submit cases, maintain logbook, view certifications

## Database

The application uses SQLite for development. All migrations have been applied and the database schema is ready.

## Development Status

✅ **COMPLETED:**
- Database migrations applied
- All Django apps configured
- Admin interface ready
- Role-based user management
- Comprehensive data models
- URL routing configured
- Forms and views implemented

## Development Notes

- Django 5.2.1
- Bootstrap 5 UI framework
- Role-based access control
- Comprehensive admin interface
- RESTful API endpoints
- File upload capabilities
- Advanced filtering and search

## Production Deployment

For production deployment:
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up proper static file serving
4. Configure email settings
5. Use environment variables for sensitive data

---
*SIMS - Specialized Information Management System*  
*Created: 2025-05-30*