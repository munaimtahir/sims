# SIMS Testing Documentation

## Stage-1 "Full-Green" Execution Status

**Last Updated:** 2025-10-11  
**Test Runner:** Django unittest / pytest  
**Coverage Tool:** coverage.py

## Current Test Status

### Overall Metrics
- **Total Tests:** 177
- **Passing:** 107 (60.5%)
- **Failing:** 10 (5.6%)
- **Errors:** 60 (33.9%)
- **Code Coverage:** 43.29%

### Module Breakdown

#### ✅ Users Module (100% passing)
- **Tests:** 30
- **Status:** All passing
- **Coverage:** 100% (tests.py), 85.48% (models.py)

#### 🟡 Cases Module (Partial)
- **Tests:** 21
- **Passing:** 11
- **Errors:** 10
- **Coverage:** Models 60-70%, Views 30-40%

#### 🟡 Logbook Module (Partial)
- **Tests:** 61
- **Passing:** 30+
- **Errors:** 30+
- **Coverage:** Models 44%, Views 24%

#### 🟡 Certificates Module (Partial)
- **Tests:** 35
- **Coverage:** Models 57%, Admin 35%

#### 🟡 Rotations Module (Partial)
- **Tests:** 30
- **Coverage:** Models 76%, Views 50%, Forms 59%

## Infrastructure Improvements

### ✅ Test Factories Created
All main models now have factory-boy factories for consistent test data:

```python
# User factories
from sims.tests.factories.user_factories import AdminFactory, SupervisorFactory, PGFactory

# Case factories
from sims.tests.factories.case_factories import ClinicalCaseFactory, CaseCategoryFactory

# Logbook factories
from sims.tests.factories.logbook_factories import LogbookEntryFactory, DiagnosisFactory, ProcedureFactory

# Certificate factories
from sims.tests.factories.certificate_factories import CertificateFactory, CertificateTypeFactory

# Rotation factories
from sims.tests.factories.rotation_factories import RotationFactory, HospitalFactory, DepartmentFactory
```

### ✅ Code Quality Tools Applied

#### Black Formatting
- **Files Reformatted:** 33
- **Status:** ✅ Complete
- **Command:** `black sims/ --exclude migrations`

#### Flake8 Linting
- **Initial Issues:** 100+
- **Current Issues:** 36
- **Main Categories:**
  - Unused imports: 19
  - Complexity warnings (C901): 14
  - Other: 3

### ✅ Model Enhancements
Added missing methods to support test assertions:
- `ClinicalCase.can_be_submitted()` 
- `ClinicalCase.can_be_reviewed()`
- `ClinicalCase.is_complete()`
- `ClinicalCase.can_edit(user)`

## Known Issues & Solutions

### Issue 1: Date Constraint Violations
**Problem:** Models with date fields have CHECK constraints preventing future dates  
**Solution:** Factories now use `date.today() - timedelta(days=X)` for all date fields  
**Status:** ✅ Fixed

### Issue 2: Manual User Creation
**Problem:** Tests creating users manually without required fields  
**Solution:** Replaced with factory-based user creation  
**Status:** ✅ Fixed in most tests

### Issue 3: Login Authentication
**Problem:** Tests using `client.login()` with hardcoded credentials  
**Solution:** Switched to `client.force_login(user_object)`  
**Status:** ✅ Fixed in case tests, needs fixing in other modules

### Issue 4: Missing Model Fields
**Problem:** Views referencing non-existent fields (e.g., `competencies_achieved`)  
**Solution:** Removed from prefetch_related queries  
**Status:** ✅ Fixed

### Issue 5: Form Submission Tests
**Problem:** Form tests expecting 302 redirects but getting 200  
**Solution:** Need to review form payloads and validation  
**Status:** ⚠️ In Progress

## Test Execution

### Running All Tests
```bash
# Django test runner
python manage.py test sims.users sims.cases sims.logbook sims.certificates sims.rotations

# Pytest
pytest sims/

# With coverage
coverage run --source=sims manage.py test
coverage report --skip-empty
coverage html  # Generates htmlcov/ directory
```

### Running Specific Modules
```bash
# Individual modules
python manage.py test sims.users --verbosity=2
python manage.py test sims.cases --verbosity=2

# Specific test class
python manage.py test sims.cases.tests.ClinicalCaseModelTest

# Specific test method
python manage.py test sims.cases.tests.ClinicalCaseModelTest.test_case_creation
```

### Code Quality Checks
```bash
# Format code
black sims/ --exclude migrations

# Check formatting
black --check sims/

# Lint code
flake8 sims/ --count --max-complexity=10 --max-line-length=127

# Django system check
python manage.py check
python manage.py check --deploy
```

## Coverage Analysis

### High Coverage Modules (>70%)
- ✅ **users/tests.py:** 100%
- ✅ **users/models.py:** 85.48%
- ✅ **rotations/tests.py:** 95.71%
- ✅ **rotations/models.py:** 75.91%
- ✅ **search/models.py:** 100%

### Low Coverage Modules (<40%)
- ⚠️ **logbook/views.py:** 24%
- ⚠️ **cases/views.py:** 30-40%
- ⚠️ **users/views.py:** 37%
- ⚠️ **users/admin.py:** 39%
- ⚠️ **certificates/admin.py:** 35%

### Recommendations for Improvement

#### Priority 1: Fix Existing Test Failures
1. Review and fix form submission tests
2. Update test data to match model requirements
3. Fix view tests using correct payloads

#### Priority 2: Increase View Coverage
1. Add tests for view permission checks
2. Test view context data
3. Test form submission flows
4. Test redirect behaviors

#### Priority 3: Increase Admin Coverage
1. Test admin actions
2. Test admin filters
3. Test admin search
4. Test custom admin methods

#### Priority 4: API Endpoint Tests
1. Test API permissions
2. Test API response formats
3. Test API error handling

## Test Organization

### Directory Structure
```
sims/
├── users/
│   └── tests.py           # User model and view tests
├── cases/
│   └── tests.py           # Case model, form, and view tests
├── logbook/
│   └── tests.py           # Logbook entry tests
├── certificates/
│   └── tests.py           # Certificate tests
├── rotations/
│   └── tests.py           # Rotation tests
└── tests/
    └── factories/
        ├── user_factories.py
        ├── case_factories.py
        ├── logbook_factories.py
        ├── certificate_factories.py
        └── rotation_factories.py
```

### Test Naming Conventions
- Test files: `tests.py` or `test_*.py`
- Test classes: `*TestCase` or `Test*`
- Test methods: `test_*`

## Continuous Integration

### GitHub Actions Workflow
Tests run automatically on:
- Push to `main` branch
- Pull requests
- Manual workflow dispatch

### CI Pipeline Steps
1. Code formatting check (Black)
2. Linting (Flake8)
3. Django check
4. Test execution with coverage
5. Coverage reporting

## Next Steps

### Immediate Actions (High Priority)
1. ✅ Create comprehensive factories for all models
2. ✅ Apply black formatting
3. ✅ Fix date constraint issues
4. ⏳ Fix remaining test errors (60)
5. ⏳ Fix test failures (10)

### Short-term Actions (Medium Priority)
6. ⏳ Replace all manual user creation with factories
7. ⏳ Fix form submission tests
8. ⏳ Add missing view permission tests
9. ⏳ Increase overall coverage to 60%+

### Long-term Actions (Low Priority)
10. Add E2E workflow tests
11. Make tests deterministic (seed RNG, freeze time)
12. Add performance tests
13. Add API integration tests
14. Target 80%+ overall coverage

## Resources

- **Django Testing Documentation:** https://docs.djangoproject.com/en/4.2/topics/testing/
- **Factory Boy Documentation:** https://factoryboy.readthedocs.io/
- **Coverage.py Documentation:** https://coverage.readthedocs.io/
- **Black Code Style:** https://black.readthedocs.io/
- **Flake8 Linting:** https://flake8.pycqa.org/

## Support

For questions or issues related to testing:
1. Check this documentation
2. Review existing test examples
3. Consult the Testing Guide in `docs/TESTING_GUIDE.md`
4. Check CI logs for detailed error messages

---

**Note:** This is a living document. Update it as the test suite evolves.
