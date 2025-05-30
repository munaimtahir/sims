#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sims_project.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@sims.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    print("✅ Superuser 'admin' created successfully!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Email: admin@sims.com")
else:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print("✅ Superuser 'admin' already exists, password updated!")
    print("   Username: admin")
    print("   Password: admin123")

print(f"\n📊 Total users in system: {User.objects.count()}")
