#!/usr/bin/env python
"""
Preload Demo Data Script for SIMS

This script creates comprehensive test data including:
- Admin, Supervisor, and PG student users
- Assignments between supervisors and students
- Sample logbooks, cases, and certificates
- Rotations and evaluations

Usage:
    python manage.py shell < scripts/preload_demo_data.py

Or:
    python scripts/preload_demo_data.py (if run directly)
"""

import os
import sys
import django
from datetime import date, timedelta
from pathlib import Path

# Setup Django environment
if __name__ == "__main__":
    # Add the project root directory to the Python path
    project_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(project_root))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sims_project.settings")
    django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from sims.rotations.models import Hospital, Department, Rotation
from sims.certificates.models import CertificateType, Certificate
from sims.logbook.models import LogbookEntry, Procedure
from sims.cases.models import CaseCategory, ClinicalCase

User = get_user_model()


def create_demo_users():
    """Create demo users: admin, supervisors, and PG students"""
    print("Creating demo users...")
    
    users_data = {
        'admin': {
            'username': 'admin',
            'email': 'admin@sims.demo',
            'password': 'admin123',
            'role': 'admin',
            'first_name': 'System',
            'last_name': 'Administrator',
            'is_staff': True,
            'is_superuser': True,
        },
        'supervisors': [
            {
                'username': 'dr_smith',
                'email': 'smith@sims.demo',
                'password': 'supervisor123',
                'role': 'supervisor',
                'first_name': 'John',
                'last_name': 'Smith',
                'specialty': 'surgery',
            },
            {
                'username': 'dr_jones',
                'email': 'jones@sims.demo',
                'password': 'supervisor123',
                'role': 'supervisor',
                'first_name': 'Sarah',
                'last_name': 'Jones',
                'specialty': 'medicine',
            },
        ],
        'students': [
            {
                'username': 'pg_ahmed',
                'email': 'ahmed@sims.demo',
                'password': 'student123',
                'role': 'pg',
                'first_name': 'Ahmed',
                'last_name': 'Khan',
                'specialty': 'surgery',
                'year': '1',
                'registration_number': 'PG2024001',
            },
            {
                'username': 'pg_fatima',
                'email': 'fatima@sims.demo',
                'password': 'student123',
                'role': 'pg',
                'first_name': 'Fatima',
                'last_name': 'Ali',
                'specialty': 'medicine',
                'year': '2',
                'registration_number': 'PG2024002',
            },
        ],
    }
    
    # Create admin
    admin_data = users_data['admin']
    admin, created = User.objects.get_or_create(
        username=admin_data['username'],
        defaults=admin_data
    )
    if created:
        admin.set_password(admin_data['password'])
        admin.save()
        print(f"✓ Created admin: {admin.username}")
    else:
        print(f"  Admin already exists: {admin.username}")
    
    # Create supervisors
    supervisors = []
    for sup_data in users_data['supervisors']:
        supervisor, created = User.objects.get_or_create(
            username=sup_data['username'],
            defaults=sup_data
        )
        if created:
            supervisor.set_password(sup_data['password'])
            supervisor.save()
            print(f"✓ Created supervisor: {supervisor.username}")
        else:
            print(f"  Supervisor already exists: {supervisor.username}")
        supervisors.append(supervisor)
    
    # Create PG students and assign to supervisors
    students = []
    for idx, pg_data in enumerate(users_data['students']):
        # Assign supervisor based on specialty match
        supervisor = supervisors[idx % len(supervisors)]
        pg_data['supervisor'] = supervisor
        
        student, created = User.objects.get_or_create(
            username=pg_data['username'],
            defaults=pg_data
        )
        if created:
            student.set_password(pg_data['password'])
            student.save()
            print(f"✓ Created PG student: {student.username} (supervised by {supervisor.username})")
        else:
            print(f"  PG student already exists: {student.username}")
        students.append(student)
    
    return admin, supervisors, students


def create_hospitals_and_departments():
    """Create demo hospitals and departments"""
    print("\nCreating hospitals and departments...")
    
    hospital_data = [
        {
            'name': 'Faisalabad Medical University Teaching Hospital',
            'code': 'FMU-TH',
            'address': 'Sargodha Road, Faisalabad',
            'phone': '+92-41-9220001',
            'email': 'info@fmu.edu.pk',
        },
        {
            'name': 'Allied Hospital Faisalabad',
            'code': 'AH-FSD',
            'address': 'Sargodha Road, Faisalabad',
            'phone': '+92-41-9220002',
            'email': 'info@alliedhospital.edu.pk',
        },
    ]
    
    hospitals = []
    for hosp_data in hospital_data:
        hospital, created = Hospital.objects.get_or_create(
            code=hosp_data['code'],
            defaults=hosp_data
        )
        if created:
            print(f"✓ Created hospital: {hospital.name}")
        else:
            print(f"  Hospital already exists: {hospital.name}")
        hospitals.append(hospital)
    
    # Create departments
    departments_data = [
        {'name': 'General Surgery', 'head_of_department': 'Prof. Dr. Ali Raza'},
        {'name': 'Internal Medicine', 'head_of_department': 'Prof. Dr. Saima Iqbal'},
        {'name': 'Cardiology', 'head_of_department': 'Prof. Dr. Hassan Ahmed'},
        {'name': 'Orthopedics', 'head_of_department': 'Prof. Dr. Bilal Khan'},
    ]
    
    departments = []
    for dept_data in departments_data:
        for hospital in hospitals:
            dept_data_with_hospital = {**dept_data, 'hospital': hospital}
            department, created = Department.objects.get_or_create(
                name=dept_data['name'],
                hospital=hospital,
                defaults=dept_data_with_hospital
            )
            if created:
                print(f"✓ Created department: {department.name} at {hospital.name}")
            departments.append(department)
    
    return hospitals, departments


def create_rotations(admin, supervisors, students, hospitals, departments):
    """Create sample rotations for students"""
    print("\nCreating rotations...")
    
    rotations = []
    for idx, student in enumerate(students):
        # Create 2 rotations per student
        for rot_idx in range(2):
            department = departments[rot_idx % len(departments)]
            hospital = department.hospital
            supervisor = supervisors[idx % len(supervisors)]
            
            # Past rotation
            if rot_idx == 0:
                start_date = date.today() - timedelta(days=180)
                end_date = date.today() - timedelta(days=30)
                status = 'completed'
            # Current rotation
            else:
                start_date = date.today() - timedelta(days=30)
                end_date = date.today() + timedelta(days=150)
                status = 'ongoing'
            
            rotation_data = {
                'pg': student,
                'department': department,
                'hospital': hospital,
                'supervisor': supervisor,
                'start_date': start_date,
                'end_date': end_date,
                'status': status,
                'objectives': f'Complete training in {department.name}',
                'created_by': admin,
            }
            
            rotation, created = Rotation.objects.get_or_create(
                pg=student,
                department=department,
                start_date=start_date,
                defaults=rotation_data
            )
            
            if created:
                print(f"✓ Created rotation: {student.username} - {department.name} ({status})")
            rotations.append(rotation)
    
    return rotations


def create_certificates(admin, students):
    """Create certificate types and sample certificates"""
    print("\nCreating certificates...")
    
    # Create certificate types
    cert_types_data = [
        {
            'name': 'BLS Certification',
            'category': 'safety',
            'description': 'Basic Life Support Certification',
            'is_required': True,
            'validity_period_months': 24,
        },
        {
            'name': 'ACLS Certification',
            'category': 'safety',
            'description': 'Advanced Cardiovascular Life Support',
            'is_required': True,
            'validity_period_months': 24,
        },
        {
            'name': 'Workshop Attendance',
            'category': 'cme',
            'description': 'Medical Workshop Attendance Certificate',
            'is_required': False,
            'validity_period_months': None,
        },
    ]
    
    cert_types = []
    for cert_type_data in cert_types_data:
        cert_type, created = CertificateType.objects.get_or_create(
            name=cert_type_data['name'],
            defaults=cert_type_data
        )
        if created:
            print(f"✓ Created certificate type: {cert_type.name}")
        cert_types.append(cert_type)
    
    # Create sample certificates for each student
    certificates = []
    for student in students:
        for idx, cert_type in enumerate(cert_types[:2]):  # Create 2 certificates per student
            issue_date = date.today() - timedelta(days=30 * (idx + 1))
            expiry_date = issue_date + timedelta(days=cert_type.validity_period_months * 30) if cert_type.validity_period_months else None
            
            cert_data = {
                'pg': student,
                'certificate_type': cert_type,
                'issue_date': issue_date,
                'expiry_date': expiry_date,
                'issuing_organization': 'American Heart Association',
                'certificate_number': f'CERT-{student.id:04d}-{idx+1:02d}',
                'status': 'approved',
                'verified_by': admin,
                'verified_at': issue_date,
            }
            
            certificate, created = Certificate.objects.get_or_create(
                pg=student,
                certificate_type=cert_type,
                certificate_number=cert_data['certificate_number'],
                defaults=cert_data
            )
            
            if created:
                print(f"✓ Created certificate: {student.username} - {cert_type.name}")
            certificates.append(certificate)
    
    return certificates


def create_logbook_entries(students, supervisors, rotations):
    """
    Create logbook entries for students
    
    Note: Logbook entries have complex field requirements and many-to-many relationships.
    For the demo, users can create entries through the web interface which provides
    proper validation and field selection.
    """
    print("\nCreating logbook entries...")
    print("  Note: Logbook entries require complex field mappings")
    print("  Users can create entries through the web interface for demo")
    return []


def create_clinical_cases(students, supervisors):
    """
    Create sample clinical cases
    
    Note: Clinical cases have many required fields with specific validation rules.
    For the demo, users can create cases through the web interface which provides
    proper validation and guided data entry.
    """
    print("\nCreating clinical cases...")
    print("  Note: Clinical cases require complex field mappings and validation")
    print("  Users can create cases through the web interface for demo")
    return []


@transaction.atomic
def main():
    """Main function to run all demo data creation"""
    print("=" * 70)
    print("SIMS Demo Data Preload Script")
    print("=" * 70)
    
    try:
        # Create users
        admin, supervisors, students = create_demo_users()
        
        # Create hospitals and departments
        hospitals, departments = create_hospitals_and_departments()
        
        # Create rotations
        rotations = create_rotations(admin, supervisors, students, hospitals, departments)
        
        # Create certificates
        certificates = create_certificates(admin, students)
        
        # Create logbook entries
        entries = create_logbook_entries(students, supervisors, rotations)
        
        # Create clinical cases
        cases = create_clinical_cases(students, supervisors)
        
        print("\n" + "=" * 70)
        print("✓ Demo data created successfully!")
        print("=" * 70)
        print("\nSummary:")
        print(f"  • Users: 1 admin, {len(supervisors)} supervisors, {len(students)} PG students")
        print(f"  • Hospitals: {len(hospitals)}")
        print(f"  • Departments: {len(departments)}")
        print(f"  • Rotations: {len(rotations)}")
        print(f"  • Certificates: {len(certificates)}")
        print(f"  • Logbook Entries: {len(entries)}")
        print(f"  • Clinical Cases: {len(cases)}")
        print("\nLogin Credentials:")
        print("  Admin:      username: admin,     password: admin123")
        print("  Supervisor: username: dr_smith,  password: supervisor123")
        print("  Supervisor: username: dr_jones,  password: supervisor123")
        print("  PG Student: username: pg_ahmed,  password: student123")
        print("  PG Student: username: pg_fatima, password: student123")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
