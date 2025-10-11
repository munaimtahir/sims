# SIMS Testing Guide - Stage 1 Full Green

## Overview
This document provides patterns and fixes for achieving 100% test coverage with 0 failures and 0 errors.

## Current Status (Starting Point)
- Tests: 184 total (100 pass, 9 fail, 75 errors)
- Coverage: 43.28%
- Issues: ValidationErrors from missing user fields, IntegrityErrors, form validation failures

## Test Infrastructure Improvements

### 1. Factories (✅ Complete)
All models now have comprehensive factories:
- **User factories**: AdminFactory, SupervisorFactory, PGFactory
- **Logbook factories**: DiagnosisFactory, ProcedureFactory, LogbookEntryFactory, LogbookReviewFactory
- **Case factories**: CaseCategoryFactory, ClinicalCaseFactory  
- **Certificate factories**: CertificateTypeFactory, CertificateFactory
- **Rotation factories**: HospitalFactory, DepartmentFactory, RotationFactory, RotationEvaluationFactory

### 2. Deterministic Test Configuration (✅ Complete)
- `conftest.py`: Pytest fixtures for reproducible tests
- Random seed: 42 (set in conftest.py)
- Temporary media storage configured
- Freezegun integration for time-based tests

## Common Error Patterns and Fixes

### Pattern 1: ValidationError - Missing User Fields

**Error:**
```python
ValidationError: {'specialty': ['This field is required for supervisors']}
ValidationError: {'year': ['This field is required for PG users']}
```

**Old Code:**
```python
self.supervisor = User.objects.create_user(
    username='supervisor', 
    role='supervisor'
)
```

**Fixed Code:**
```python
from sims.tests.factories import SupervisorFactory, PGFactory

self.supervisor = SupervisorFactory()
self.pg = PGFactory(supervisor=self.supervisor)
```

### Pattern 2: IntegrityError - Future Date Validation

**Error:**
```python
IntegrityError: CHECK constraint failed: logbook_entry_date_not_future
```

**Fix:**
Use freezegun or ensure dates are in the past:
```python
from datetime import date, timedelta

# Option 1: Use past date
entry = LogbookEntryFactory(date=date.today() - timedelta(days=5))

# Option 2: Freeze time
from freezegun import freeze_time

@freeze_time("2024-01-15")
def test_logbook_entry(self):
    entry = LogbookEntryFactory(date=date(2024, 1, 10))
```

### Pattern 3: Form Validation Failures

**Error:**
```python
AssertionError: False is not true  # form.is_valid() failed
```

**Debug approach:**
```python
form = SomeForm(data=form_data)
if not form.is_valid():
    print(f"Form errors: {form.errors}")  # Debug what's wrong
self.assertTrue(form.is_valid())
```

**Common fixes:**
- Ensure all required fields are provided
- Use correct field names (check model fields)
- Provide valid foreign key IDs, not objects
- Use correct date format: 'YYYY-MM-DD'

### Pattern 4: Redirect Status Code Mismatches

**Error:**
```python
AssertionError: 200 != 302  # Expected redirect, got success
AssertionError: 301 != 302  # Permanent vs temporary redirect
```

**Fix:**
Check the actual view behavior:
```python
# If form is invalid, view returns 200 (re-renders form)
# If form is valid, view returns 302 (redirect)
response = self.client.post(url, data)
if response.status_code == 200:
    # Form failed validation, check errors
    form = response.context.get('form')
    if form:
        print(f"Form errors: {form.errors}")
```

### Pattern 5: Import Test Base Classes

**Error:**
```python
ImportError: cannot import name 'TestCase'
```

**Fix:**
```python
from django.test import TestCase, Client
from django.urls import reverse
```

## Systematic Test Fixing Workflow

### Step 1: Fix User Creation (Priority: CRITICAL)
Replace all manual user creation with factories:

```python
# Find all instances of:
User.objects.create_user(...)

# Replace with:
from sims.tests.factories import PGFactory, SupervisorFactory, AdminFactory

# In setUp():
self.supervisor = SupervisorFactory()
self.pg = PGFactory(supervisor=self.supervisor)
self.admin = AdminFactory()
```

### Step 2: Fix Date Validation (Priority: HIGH)
Ensure all dates are valid:

```python
from datetime import date, timedelta

# For past dates:
date=date.today() - timedelta(days=5)

# For future dates (where allowed):
date=date.today() + timedelta(days=30)
```

### Step 3: Fix Form Tests (Priority: HIGH)
Update form test data:

```python
# Check model fields first
# Ensure data dictionary has all required fields
# Use correct field types and formats

form_data = {
    'title': 'Test Title',
    'date': '2024-01-15',  # String format for form data
    'pg': self.pg.id,  # Use .id for foreign keys in forms
    'supervisor': self.supervisor.id,
    # ... all other required fields
}

form = MyForm(data=form_data)
if not form.is_valid():
    self.fail(f"Form validation failed: {form.errors}")
```

### Step 4: Fix View Tests (Priority: MEDIUM)
Ensure proper authentication and permissions:

```python
def test_view_requires_login(self):
    response = self.client.get(reverse('view-name'))
    self.assertEqual(response.status_code, 302)  # Redirect to login

def test_view_with_auth(self):
    self.client.force_login(self.pg)
    response = self.client.get(reverse('view-name'))
    self.assertEqual(response.status_code, 200)
```

## Module-Specific Fixes

### Cases Module
- Replace User.objects.create_user() with factories
- Ensure all foreign keys (category, diagnosis) are created
- Fix date fields to use past dates

### Logbook Module
- Add rotation factory usage where needed
- Fix date validation (no future dates)
- Ensure supervisor is assigned

### Certificates Module
- Add certificate_file in test data (use SimpleUploadedFile)
- Fix expiry_date to be after issue_date
- Use factories for certificate_type

### Rotations Module
- Use hospital and department factories
- Fix date ranges (start_date < end_date)
- Ensure duration_weeks matches date range

## Coverage Improvement Strategy

### Phase 1: Views (Target: 90%+)
1. Test all CRUD operations
2. Test permission checks (admin, supervisor, pg)
3. Test form validation
4. Test redirects
5. Test context data

### Phase 2: Admin (Target: 80%+)
1. Test admin list views
2. Test admin filters
3. Test admin actions
4. Test custom admin methods

### Phase 3: API (Target: 90%+)
1. Test all endpoints
2. Test authentication
3. Test permissions
4. Test response formats

### Phase 4: Forms (Target: 90%+)
1. Test valid data
2. Test invalid data
3. Test field validations
4. Test clean methods

## Testing Best Practices

### 1. Use Factories Consistently
```python
# Good
pg = PGFactory()

# Bad  
pg = User.objects.create_user(...)
```

### 2. Test One Thing Per Test
```python
# Good
def test_user_creation(self):
    user = PGFactory()
    self.assertEqual(user.role, 'pg')

def test_user_has_supervisor(self):
    user = PGFactory()
    self.assertIsNotNone(user.supervisor)

# Bad
def test_user(self):
    user = PGFactory()
    self.assertEqual(user.role, 'pg')
    self.assertIsNotNone(user.supervisor)
    # ... many more assertions
```

### 3. Use Descriptive Test Names
```python
# Good
def test_pg_cannot_access_other_pg_cases(self):
    ...

# Bad
def test_access(self):
    ...
```

### 4. Clean Up After Tests
```python
def tearDown(self):
    # Factories handle this automatically with django TestCase
    # But for manual cleanup:
    User.objects.all().delete()
```

## Running Tests

### Run all tests:
```bash
python manage.py test
```

### Run specific module:
```bash
python manage.py test sims.users
python manage.py test sims.cases
```

### Run with coverage:
```bash
coverage run --source=sims manage.py test
coverage report
coverage html
```

### Run specific test:
```bash
python manage.py test sims.users.tests.UserModelTests.test_pg_creation
```

## Quality Checks

### Before committing:
```bash
# Format code
black sims/ --line-length 100

# Check linting
flake8 sims/

# Run Django checks
python manage.py check

# Run tests
python manage.py test

# Check coverage
coverage run --source=sims manage.py test
coverage report --skip-empty
```

## Next Steps

1. ✅ Code quality (black, flake8) - DONE
2. ✅ Factory infrastructure - DONE
3. ⏳ Fix test errors (75 errors) - IN PROGRESS
4. ⏳ Fix test failures (9 failures) - PENDING
5. ⏳ Improve coverage to 100% - PENDING
6. ⏳ Add E2E tests - PENDING
7. ⏳ Documentation updates - PENDING

## Estimated Timeline

- Fix test errors: 2-3 hours (systematic replacement)
- Fix test failures: 1-2 hours (form/redirect fixes)
- Improve coverage: 3-4 hours (new test cases)
- E2E tests: 2-3 hours (integration scenarios)
- Documentation: 1 hour

Total: 9-13 hours of focused work
