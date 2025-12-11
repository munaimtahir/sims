# SIMS Repository Structure

## Overview

This document describes the standardized directory structure of the SIMS (Student Information Management System) repository after the December 2025 cleanup and restructuring effort.

## Directory Layout

```
sims/
├── .github/                    # GitHub Actions CI/CD workflows
│   └── workflows/              
│       ├── django-tests.yml    # Backend test pipeline
│       └── frontend-tests.yml  # Frontend test pipeline
│
├── archive/                    # 🗄️ Legacy files (preserved, not maintained)
│   ├── README.md               # Archive documentation
│   ├── docs/                   # Old development and planning docs (18 files)
│   ├── scripts/                # Legacy utility scripts (26 files)
│   └── tests/                  # Old diagnostic test scripts (60+ files)
│
├── deployment/                 # Deployment configurations and scripts
│   ├── nginx.conf              # Nginx configuration
│   ├── gunicorn.conf.py        # Gunicorn WSGI server config
│   ├── sims.service            # Systemd service file
│   └── *.sh                    # Deployment shell scripts
│
├── docs/                       # 📚 Current project documentation
│   ├── README.md               # Documentation index
│   ├── CHANGELOG_RESTRUCTURE.md # Repository cleanup log
│   ├── PROJECT_STRUCTURE.md    # Detailed structure guide
│   ├── PROJECT_SUMMARY.md      # Executive summary
│   ├── TESTING_GUIDE.md        # Testing documentation
│   ├── TROUBLESHOOTING.md      # Common issues and fixes
│   ├── archive/                # Historical development documents
│   └── reports/                # Feature and testing reports
│
├── frontend/                   # Next.js frontend application
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   ├── lib/                    # Utility libraries
│   ├── types/                  # TypeScript type definitions
│   ├── package.json            # Frontend dependencies
│   └── next.config.mjs         # Next.js configuration
│
├── logs/                       # Runtime logs (gitignored)
│   └── test_reports/           # Test execution reports
│
├── media/                      # User-uploaded files (gitignored)
│
├── scripts/                    # Active utility scripts
│   └── create_superuser.bat    # Superuser creation helper
│
├── sims/                       # Django application modules
│   ├── academics/              # Academic management
│   ├── analytics/              # Analytics and metrics
│   ├── attendance/             # Attendance tracking
│   ├── audit/                  # Audit trail functionality
│   ├── bulk/                   # Bulk operations
│   ├── cases/                  # Clinical case management
│   ├── certificates/           # Certification tracking
│   ├── domain/                 # Domain models and business logic
│   ├── logbook/                # Digital logbook
│   ├── notifications/          # Notification system
│   ├── reports/                # Report generation
│   ├── results/                # Results management
│   ├── rotations/              # Training rotation management
│   ├── search/                 # Global search functionality
│   ├── static/                 # App-specific static files
│   ├── tests/                  # App-level test utilities
│   └── users/                  # User management and authentication
│
├── sims_project/               # Django project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py                 # WSGI application
│   ├── asgi.py                 # ASGI application
│   ├── celery.py               # Celery configuration
│   ├── health.py               # Health check endpoints
│   └── middleware.py           # Custom middleware
│
├── static/                     # Project-wide static assets
│   ├── css/                    # Compiled CSS
│   ├── images/                 # Shared images and icons
│   └── js/                     # JavaScript bundles
│
├── templates/                  # Django HTML templates
│   ├── admin/                  # Admin interface templates
│   ├── base/                   # Base templates
│   ├── cases/                  # Clinical cases templates
│   ├── certificates/           # Certificates templates
│   ├── home/                   # Homepage templates
│   ├── logbook/                # Logbook templates
│   ├── notifications/          # Notification templates
│   ├── registration/           # Auth/login templates
│   ├── reports/                # Report templates
│   ├── rotations/              # Rotation templates
│   └── users/                  # User management templates
│
├── tests/                      # Test suite
│   ├── conftest.py             # Pytest configuration
│   ├── factories/              # Test data factories
│   ├── feature_verification/   # Feature verification tests
│   ├── manual/                 # Manual test utilities
│   ├── resources/              # Test resources
│   └── test_*.py               # Test modules (22 files)
│
├── .dockerignore               # Docker build exclusions
├── .env.example                # Environment variables template
├── .gitignore                  # Git exclusions
├── .pre-commit-config.yaml     # Pre-commit hooks config
├── CHANGELOG.md                # Project changelog
├── README.md                   # Main project documentation
├── conftest.py                 # Root pytest configuration
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── manage.py                   # Django management script
├── Makefile                    # Build automation
├── pyproject.toml              # Python project metadata
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Python dependencies
└── requirements-dev.txt        # Development dependencies
```

## Key Directories Explained

### Active Code (`sims/`, `sims_project/`, `templates/`, `static/`)
Contains the production Django application code. All modules under `sims/` are Django apps that comprise the SIMS platform functionality.

### Frontend (`frontend/`)
Separate Next.js application providing a modern React-based UI. Can be developed and deployed independently from the Django backend.

### Tests (`tests/`)
Focused test suite containing only active, maintained test files. Legacy diagnostic scripts have been archived. Currently contains 22 test modules testing all major features.

### Documentation (`docs/`)
All current project documentation. Historical reports and development documents are preserved here. See `docs/README.md` for a complete index.

### Archive (`archive/`)
Legacy files preserved for reference but not maintained. Includes:
- Old development planning documents
- Legacy utility and diagnostic scripts  
- Old test verification scripts

These files may not work with current code but are kept for historical reference.

### Deployment (`deployment/`)
Production deployment configurations including:
- Nginx reverse proxy config
- Gunicorn WSGI server config
- Systemd service definitions
- Deployment automation scripts

### Configuration Files (Root)
- `manage.py` - Django CLI entrypoint
- `requirements.txt` - Python production dependencies
- `requirements-dev.txt` - Development dependencies
- `pytest.ini`, `pyproject.toml` - Testing configuration
- `Dockerfile`, `docker-compose.yml` - Container definitions
- `.env.example` - Environment variable template

## Excluded from Version Control

The following are excluded via `.gitignore`:
- `__pycache__/`, `*.pyc` - Python bytecode
- `venv/`, `env/` - Virtual environments
- `db.sqlite3` - Development database
- `/media/` - User uploads
- `/staticfiles/` - Collected static files
- `logs/*.log` - Log files
- `.coverage`, `htmlcov/` - Test coverage reports
- `node_modules/` - Frontend dependencies

## Excluded from Docker Builds

The following are excluded via `.dockerignore`:
- `archive/` - Legacy files
- `docs/` - Documentation
- `tests/` - Test suite
- `.github/` - CI workflows
- `frontend/` - Separate Next.js app
- `logs/`, `scripts/` - Development artifacts

## Repository Standards

### Python Code
- **Location**: `sims/`, `sims_project/`
- **Style**: Black formatter (100 char line length)
- **Linting**: Flake8
- **Testing**: pytest, pytest-django

### Frontend Code
- **Location**: `frontend/`
- **Framework**: Next.js 14 with TypeScript
- **Testing**: Jest, Playwright
- **Linting**: ESLint

### Documentation
- **Location**: `docs/`
- **Format**: Markdown
- **Index**: See `docs/README.md`

### Tests
- **Location**: `tests/` (root), `sims/*/tests.py` (app-level)
- **Framework**: pytest with pytest-django
- **Coverage**: Tracked via pytest-cov
- **Target**: 40%+ coverage

## CI/CD Pipelines

### Django Tests (`.github/workflows/django-tests.yml`)
- Python 3.11, 3.12
- Black formatting check
- Flake8 linting
- Django system checks
- Full test suite with coverage

### Frontend Tests (`.github/workflows/frontend-tests.yml`)
- Node.js 18, 20
- ESLint checks
- Jest unit tests
- Playwright e2e tests
- Production build verification

## Additional Resources

- **Complete cleanup log**: `docs/CHANGELOG_RESTRUCTURE.md`
- **Documentation index**: `docs/README.md`
- **Project summary**: `docs/PROJECT_SUMMARY.md`
- **Testing guide**: `docs/TESTING_GUIDE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

## Questions?

For questions about the repository structure or the recent cleanup, refer to:
1. This document for current structure
2. `docs/CHANGELOG_RESTRUCTURE.md` for cleanup details
3. `archive/README.md` for information about archived files
4. Project README.md for general information

---

**Last Updated**: December 2025  
**Related Documents**: CHANGELOG_RESTRUCTURE.md, PROJECT_SUMMARY.md  
**Status**: Current and maintained
