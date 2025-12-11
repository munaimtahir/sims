# SIMS - Student (Postgrduate) Information Management System

A comprehensive Django web application for managing postgraduate medical residents' academic and training records.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: flake8](https://img.shields.io/badge/linter-flake8-blue.svg)](https://flake8.pycqa.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Development Status](#development-status)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [User Roles](#user-roles)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Deployment](#deployment)
- [Documentation](#documentation)
- [Contributing](#contributing)

## 🎯 Overview

SIMS (Surgical Information Management System) is a comprehensive web-based management system designed specifically for postgraduate medical training programs. It provides a complete solution for tracking trainee progress, managing rotations, maintaining digital logbooks, and handling clinical case submissions.

**Current Status**: ✅ **Production-Ready for Pilot Deployment**

## ✨ Features

### Core Features (Ready to Use)

- **👥 User Management**: Role-based access control for admins, supervisors, and postgraduate students
- **📊 Dashboard System**: Customized dashboards for each user role with analytics
- **🔄 Rotation Management**: Track and manage training rotations across different departments
- **📜 Certificate Management**: Manage and track certifications and achievements
- **📚 Digital Logbook**: Record training activities, procedures, and evaluations
- **🏥 Clinical Cases**: Submit, review, and manage clinical cases with detailed documentation
- **📈 Analytics & Reporting**: Comprehensive statistics and data visualization
- **🔍 Advanced Filtering**: Search and filter capabilities across all modules
- **📤 Data Export**: Export data to CSV format for all major modules
- **🔐 Security**: Role-based permissions, secure authentication, and session management
- **🌐 Global Search**: Cross-module search with suggestions, highlights, and per-user history
- **🛡️ Audit Trail**: Historical tracking for key models plus Activity Log APIs and CSV export
- **✅ Business Rules Engine**: Centralised validators, sanitisation and consistent error handling

### Additional Features

- **Admin Interface**: Comprehensive Django admin with custom branding
- **RESTful APIs**: JSON endpoints for statistics and data retrieval
- **File Management**: Upload and manage documents and images
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **PMC Theme**: Professional medical college branding throughout

For a detailed breakdown of all features by development status, see [FEATURES_STATUS.md](docs/FEATURES_STATUS.md).

## 📊 Development Status

The SIMS application has completed its initial development phase with the following status:

- **✅ Ready to Use**: ~90 features (60%) - Fully functional and production-ready
- **⚠️ Needs Work**: ~25 features (17%) - Implemented but requires debugging or completion
- **🔜 Planned**: ~35 features (23%) - Yet to be built

### Module Status Summary

| Module | Completion | Status |
|--------|------------|--------|
| Authentication | 100% | ✅ Complete |
| User Management | 95% | ✅ Nearly Complete |
| Dashboards | 100% | ✅ Complete |
| Clinical Cases | 90% | ✅ Functional |
| Digital Logbook | 95% | ✅ Nearly Complete |
| Certificates | 95% | ✅ Nearly Complete |
| Rotations | 90% | ✅ Functional |
| Admin Interface | 100% | ✅ Complete |
| UI/UX | 95% | ✅ Nearly Complete |

See [docs/FEATURES_STATUS.md](docs/FEATURES_STATUS.md) for complete feature categorization.

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/munaimtahir/sims.git
cd sims
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Or use the default credentials:
- Username: `admin`
- Password: `admin123`

### 6. Start Development Server

```bash
python manage.py runserver
```

### 7. Access the Application

- **Main Application**: http://127.0.0.1:8000
- **Admin Interface**: http://127.0.0.1:8000/admin
- **Login**: Use admin credentials

## 📁 Project Structure

```
sims/
├── manage.py                   # Django management script
├── README.md                   # Project overview and documentation
├── CHANGELOG.md                # Project changelog
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
├── pytest.ini                  # Pytest configuration
├── pyproject.toml              # Black/pytest configuration
├── conftest.py                 # Pytest fixtures and configuration
├── .github/workflows/          # CI/CD workflows
├── archive/                    # 🗄️ Legacy files (preserved, not maintained)
│   ├── docs/                   # Old development docs & deployment guides
│   ├── scripts/                # Legacy utility scripts
│   └── tests/                  # Old diagnostic test scripts
├── deployment/                 # Deployment configuration and scripts
├── docs/                       # 📚 Current project documentation
│   ├── archive/                # Historical development documents
│   ├── reports/                # Feature and testing reports
│   └── CHANGELOG_RESTRUCTURE.md # Repository cleanup documentation
├── frontend/                   # Next.js frontend application
├── logs/                       # Runtime and diagnostic logs
├── scripts/                    # Active utility scripts
├── sims_project/               # Django project configuration
│   ├── settings.py             # Django settings module
│   ├── urls.py                 # Root URL patterns
│   ├── wsgi.py                 # WSGI configuration
│   └── health.py               # Health check endpoints
├── sims/                       # Core Django applications
│   ├── analytics/              # Analytics and metrics
│   ├── attendance/             # Attendance tracking
│   ├── audit/                  # Audit trail functionality
│   ├── bulk/                   # Bulk operations
│   ├── cases/                  # Clinical case management
│   ├── certificates/           # Certification tracking
│   ├── logbook/                # Digital logbook functionality
│   ├── notifications/          # Notification system
│   ├── reports/                # Report generation
│   ├── rotations/              # Training rotation management
│   ├── search/                 # Global search functionality
│   └── users/                  # User management and authentication
├── static/                     # Project static assets
│   ├── css/                    # Compiled CSS
│   ├── images/                 # Shared imagery and icons
│   └── js/                     # JavaScript bundles
├── templates/                  # Django template files
└── tests/                      # Test suite and utilities
    ├── factories/              # Test data factories
    ├── feature_verification/   # Feature verification tests
    ├── manual/                 # Manual test utilities
    └── resources/              # Test resources
```

> **Note**: The `/archive/` directory contains legacy files preserved for reference. These files are not maintained and may not work with the current codebase. See [docs/CHANGELOG_RESTRUCTURE.md](docs/CHANGELOG_RESTRUCTURE.md) for details on what was archived.

## 👥 User Roles

The system supports three primary user roles:

### 1. **Admin** 
- Full system access
- User management and creation
- System configuration
- View all data and analytics
- Manage all modules

### 2. **Supervisor**
- Manage assigned postgraduate students
- Review and approve logbook entries
- Review clinical cases
- Evaluate rotations
- View trainee progress and analytics

### 3. **Postgraduate (PG)**
- Maintain personal digital logbook
- Submit clinical cases for review
- Track certifications and achievements
- View rotation schedule
- Access personal analytics and progress

## 🛠️ Development Guidelines

### Code Style

This project follows Python and Django best practices:

- **Code Formatting**: [Black](https://github.com/psf/black) with 100 character line length
- **Linting**: [Flake8](https://flake8.pycqa.org/) for code quality checks
- **Style Guide**: [PEP 8](https://www.python.org/dev/peps/pep-0008/)

### Running Code Quality Checks

```bash
# Format code with Black
black sims/ --line-length 100

# Run Flake8 linter
flake8 sims/ --count --statistics

# Run both
black sims/ --line-length 100 && flake8 sims/ --count --statistics
```

### Git Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make your changes and commit: `git commit -m "Description of changes"`
3. Push to the branch: `git push origin feature/your-feature-name`
4. Create a Pull Request

### Commit Messages

Follow conventional commit format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test sims.users

# Run with pytest (if configured)
pytest
```

### Writing Tests

- Place tests in `tests.py` within each app
- Follow Django testing best practices
- Aim for good test coverage of critical functionality
- Test both success and error cases

## 🚀 Deployment

### Development Deployment

The application is ready for development/testing deployment using the built-in Django development server.

### Production Deployment

For production deployment, consider:

1. **Environment Configuration**
   - Set `DEBUG = False` in settings
   - Use environment variables for sensitive data
   - Configure `ALLOWED_HOSTS`

2. **Database**
   - Use PostgreSQL or MySQL for production
   - Configure proper database backup

3. **Static Files**
   - Collect static files: `python manage.py collectstatic`
   - Serve via nginx or CDN

4. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure nginx as reverse proxy
   - Set up SSL/TLS certificates

5. **Security**
   - Enable security middleware
   - Configure HTTPS
   - Set up proper logging
   - Implement backup strategy

See [docs/SERVER_DEPLOYMENT_GUIDE_172.236.152.35.md](docs/SERVER_DEPLOYMENT_GUIDE_172.236.152.35.md) for detailed deployment instructions.

## 📖 Documentation

All documentation has been consolidated under `docs/` for consistency. Start with the [documentation index](docs/README.md) to see every guide, report, and checklist that previously lived in the project root.

Key references:

- [PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) – Up-to-date directory layout.
- [PROJECT_ORGANIZATION_GUIDE.md](docs/PROJECT_ORGANIZATION_GUIDE.md) & [COMPLETE_ORGANIZATION_GUIDE.md](docs/COMPLETE_ORGANIZATION_GUIDE.md) – Detailed notes that were relocated from the root without content changes.
- [PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) – Overall platform overview and readiness summary.
- [FEATURES_STATUS.md](docs/FEATURES_STATUS.md) & [SYSTEM_STATUS.md](docs/SYSTEM_STATUS.md) – Feature completeness and system health tracking.
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) – Common issues and remediation steps.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create your branch from `main`
2. **Write clear commit messages** following the commit message format
3. **Follow the code style** guidelines (Black + Flake8)
4. **Add tests** for new features
5. **Update documentation** as needed
6. **Submit a pull request** with a clear description of changes

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run code quality checks before committing
black sims/ --check
flake8 sims/
python manage.py test
```

## 📄 License

This project is proprietary software developed for medical training management.

## 📞 Support

For support, issues, or questions:
- **Issues**: Open an issue on GitHub
- **Documentation**: Check the docs/ directory
- **Email**: admin@sims.com

## 🙏 Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- UI framework: [Bootstrap 5](https://getbootstrap.com/)
- Icons: [Font Awesome](https://fontawesome.com/)

---

**SIMS - Surgical Information Management System**  
*Version 1.0 - January 2025*  
*Production-Ready for Pilot Deployment*
