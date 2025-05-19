#!/usr/bin/env python

"""
Test Data Generator for MigrantConnectTN

This script generates sample data for testing the MigrantConnectTN application.
It creates test users for all roles (migrants, employers, NGOs, background checkers),
as well as sample job postings, services, and policies.

Usage:
    python generate_test_data.py
"""

import os
import sys
import random
import datetime
from faker import Faker
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId
import uuid

# Add the application to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the app and models after setting the path
from app import create_app, mongo
from app.models.auth import Auth
from app.models.government import Government

# Initialize Flask app
app = create_app()

# Initialize Faker
fake = Faker('en_IN')  # Use Indian locale for more realistic data

# Constants
TN_CITIES = [
    'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem',
    'Tirunelveli', 'Tiruppur', 'Vellore', 'Erode', 'Thoothukkudi',
    'Dindigul', 'Thanjavur', 'Ranipet', 'Sivakasi', 'Karur', 
    'Udhagamandalam', 'Hosur', 'Nagercoil', 'Kanchipuram'
]

INDIAN_STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
    'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
    'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
    'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal'
]

COMPANY_SECTORS = [
    'Construction', 'Manufacturing', 'Textile', 'Agriculture', 'Hospitality',
    'Information Technology', 'Healthcare', 'Education', 'Other'
]

COMPANY_TYPES = ['organized', 'unorganized']
JOB_INFO_SOURCES = ['friends', 'agency', 'other']
APPROVAL_STATUSES = ['pending', 'approved', 'rejected']

# Helper functions
def generate_aadhar():
    """Generate a random 12-digit Aadhar number"""
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])

def generate_phone():
    """Generate a random 10-digit Indian phone number"""
    return ''.join(['9'] + [str(random.randint(0, 9)) for _ in range(9)])

def generate_unique_id(prefix):
    """Generate a unique ID with the given prefix"""
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

def clear_collections():
    """Clear all collections before generating new data"""
    with app.app_context():
        collections = [
            'credentials', 'migrants', 'employers', 'ngos', 'bg_checkers',
            'jobs', 'services', 'policies', 'helplines'
        ]
        for collection in collections:
            mongo.db[collection].delete_many({})
        print("All collections cleared.")

# Data generators
def generate_migrants(count=20):
    """Generate sample migrant data"""
    print(f"Generating {count} migrant profiles...")
    migrants = []
    
    with app.app_context():
        for _ in range(count):
            # Create migrant profile
            name = fake.name()
            mobile = generate_phone()
            dob = fake.date_of_birth(minimum_age=18, maximum_age=50)
            aadhar = generate_aadhar()
            current_city = random.choice(TN_CITIES)
            current_address = fake.address()
            native_state = random.choice([s for s in INDIAN_STATES if s != 'Tamil Nadu'])
            native_address = fake.address()
            job_info_source = random.choice(JOB_INFO_SOURCES)
            
            # Create contact info if job source is friends or agency
            contact_name = fake.name() if job_info_source in ['friends', 'agency'] else None
            contact_number = generate_phone() if job_info_source in ['friends', 'agency'] else None
            
            # Company info
            contractor_name = fake.name()
            contractor_number = generate_phone()
            company_name = fake.company()
            company_type = random.choice(COMPANY_TYPES)
            company_sector = random.choice(COMPANY_SECTORS)
            
            # Determine status (mostly pending, some approved)
            status = random.choices(
                APPROVAL_STATUSES, 
                weights=[0.6, 0.3, 0.1],  # 60% pending, 30% approved, 10% rejected
                k=1
            )[0]
            
            # Create migrant profile
            migrant_data = {
                'name': name,
                'dob': dob.strftime('%Y-%m-%d'),
                'aadhar': aadhar,
                'current_address': current_address,
                'current_city': current_city,
                'native_state': native_state,
                'native_address': native_address,
                'job_info_source': job_info_source,
                'contact_name': contact_name,
                'contact_number': contact_number,
                'contractor_name': contractor_name,
                'contractor_number': contractor_number,
                'company_name': company_name,
                'company_type': company_type,
                'company_sector': company_sector,
                'registration_date': fake.date_time_between(start_date='-30d', end_date='now'),
                'status': status
            }
            
            # Insert migrant profile
            migrant_id = mongo.db.migrants.insert_one(migrant_data).inserted_id
            
            # Generate unique ID for approved migrants
            unique_id = generate_unique_id("MIG") if status == 'approved' else None
            
            # Create credentials
            Auth.create_credentials(
                user_id=migrant_id,
                password='default123',
                user_type='migrant',
                mobile=mobile,
                email=fake.email() if random.random() > 0.5 else None,  # 50% chance of having email
                unique_id=unique_id,
                approval_status=status
            )
            
            migrants.append({
                'id': str(migrant_id),
                'name': name,
                'mobile': mobile,
                'status': status,
                'unique_id': unique_id
            })
    
    return migrants

def generate_employers(count=5):
    """Generate sample employer data"""
    print(f"Generating {count} employer profiles...")
    employers = []
    
    with app.app_context():
        for _ in range(count):
            # Create employer profile
            company_name = fake.company()
            contact_name = fake.name()
            mobile = generate_phone()
            email = fake.company_email()
            address = fake.address()
            city = random.choice(TN_CITIES)
            sector = random.choice(COMPANY_SECTORS)
            employee_count = random.randint(10, 500)
            
            # Determine status
            status = random.choices(
                APPROVAL_STATUSES, 
                weights=[0.4, 0.5, 0.1],  # 40% pending, 50% approved, 10% rejected
                k=1
            )[0]
            
            # Create employer profile
            employer_data = {
                'company_name': company_name,
                'contact_name': contact_name,
                'address': address,
                'city': city,
                'sector': sector,
                'employee_count': employee_count,
                'registration_date': fake.date_time_between(start_date='-60d', end_date='now'),
                'status': status
            }
            
            # Insert employer profile
            employer_id = mongo.db.employers.insert_one(employer_data).inserted_id
            
            # Generate unique ID for approved employers
            unique_id = generate_unique_id("EMP") if status == 'approved' else None
            
            # Create credentials
            Auth.create_credentials(
                user_id=employer_id,
                password='default123',
                user_type='employer',
                mobile=mobile,
                email=email,
                unique_id=unique_id,
                approval_status=status
            )
            
            employers.append({
                'id': str(employer_id),
                'company_name': company_name,
                'contact_name': contact_name,
                'mobile': mobile,
                'email': email,
                'status': status,
                'unique_id': unique_id
            })
            
            # Generate jobs for approved employers
            if status == 'approved':
                generate_jobs(employer_id, company_name, random.randint(1, 3))
    
    return employers

def generate_ngos(count=3):
    """Generate sample NGO data"""
    print(f"Generating {count} NGO profiles...")
    ngos = []
    
    with app.app_context():
        for _ in range(count):
            # Create NGO profile
            org_name = fake.company() + " Foundation"
            contact_name = fake.name()
            mobile = generate_phone()
            email = fake.company_email()
            address = fake.address()
            city = random.choice(TN_CITIES)
            focus_area = random.choice(['Education', 'Healthcare', 'Legal Aid', 'Welfare', 'Housing'])
            
            # Determine status
            status = random.choices(
                APPROVAL_STATUSES, 
                weights=[0.3, 0.6, 0.1],  # 30% pending, 60% approved, 10% rejected
                k=1
            )[0]
            
            # Create NGO profile
            ngo_data = {
                'organization_name': org_name,
                'contact_name': contact_name,
                'address': address,
                'city': city,
                'focus_area': focus_area,
                'registration_date': fake.date_time_between(start_date='-90d', end_date='now'),
                'status': status
            }
            
            # Insert NGO profile
            ngo_id = mongo.db.ngos.insert_one(ngo_data).inserted_id
            
            # Generate unique ID for approved NGOs
            unique_id = generate_unique_id("NGO") if status == 'approved' else None
            
            # Create credentials
            Auth.create_credentials(
                user_id=ngo_id,
                password='default123',
                user_type='ngo',
                mobile=mobile,
                email=email,
                unique_id=unique_id,
                approval_status=status
            )
            
            ngos.append({
                'id': str(ngo_id),
                'org_name': org_name,
                'contact_name': contact_name,
                'mobile': mobile,
                'email': email,
                'status': status,
                'unique_id': unique_id
            })
            
            # Generate services for approved NGOs
            if status == 'approved':
                generate_services(ngo_id, org_name, random.randint(1, 3))
    
    return ngos

def generate_bg_checkers(count=5):
    """Generate sample background checker data"""
    print(f"Generating {count} background checker profiles...")
    bg_checkers = []
    
    with app.app_context():
        for _ in range(count):
            # Create background checker profile
            name = fake.name()
            email = fake.email()
            phone = generate_phone()
            area_assigned = random.choice(TN_CITIES)
            
            # Create the background checker
            result = Government.create_bg_checker(
                name=name,
                email=email,
                password_hash=generate_password_hash('default123'),
                phone=phone,
                area_assigned=area_assigned
            )
            
            bg_checker_id = result.inserted_id
            bg_checker = mongo.db.bg_checkers.find_one({'_id': bg_checker_id})
            
            bg_checkers.append({
                'id': str(bg_checker_id),
                'name': name,
                'email': email,
                'phone': phone,
                'area_assigned': area_assigned,
                'unique_id': bg_checker['unique_id']
            })
    
    return bg_checkers

def generate_admin():
    """Generate admin user"""
    print("Generating admin user...")
    
    with app.app_context():
        # Create admin profile
        admin_data = {
            'name': 'Admin User',
            'email': 'admin@migrantconnect-tn.gov.in',
            'department': 'Administration',
            'role': 'System Administrator',
            'created_at': datetime.datetime.utcnow()
        }
        
        # Insert admin profile
        admin_id = mongo.db.admins.insert_one(admin_data).inserted_id
        
        # Create credentials
        Auth.create_credentials(
            user_id=admin_id,
            password='admin123',  # Default admin password
            user_type='admin',
            mobile='9876543210',
            email='admin@migrantconnect-tn.gov.in',
            unique_id='ADMIN001',
            approval_status='approved'
        )
        
        return {
            'id': str(admin_id),
            'email': 'admin@migrantconnect-tn.gov.in',
            'password': 'admin123',
            'unique_id': 'ADMIN001'
        }

def generate_jobs(employer_id, company_name, count=2):
    """Generate sample job postings for an employer"""
    jobs = []
    
    with app.app_context():
        for _ in range(count):
            # Create job posting
            job_title = random.choice([
                'Construction Worker', 'Factory Worker', 'Machine Operator',
                'Textile Worker', 'Agricultural Laborer', 'Warehouse Associate',
                'Delivery Driver', 'Security Guard', 'Housekeeping Staff'
            ])
            
            job_data = {
                'employer_id': employer_id,
                'company_name': company_name,
                'title': job_title,
                'description': fake.paragraph(nb_sentences=3),
                'location': random.choice(TN_CITIES),
                'salary': random.randint(10000, 25000),
                'vacancies': random.randint(1, 10),
                'sector': random.choice(COMPANY_SECTORS),
                'skills_required': fake.paragraph(nb_sentences=1),
                'experience_required': random.choice(['0-1 years', '1-3 years', '3-5 years']),
                'posted_date': fake.date_time_between(start_date='-30d', end_date='now'),
                'status': 'active'
            }
            
            # Insert job posting
            job_id = mongo.db.jobs.insert_one(job_data).inserted_id
            
            jobs.append({
                'id': str(job_id),
                'title': job_title,
                'company_name': company_name
            })
    
    return jobs

def generate_services(ngo_id, org_name, count=2):
    """Generate sample services for an NGO"""
    services = []
    
    with app.app_context():
        for _ in range(count):
            # Create service
            service_title = random.choice([
                'Legal Assistance', 'Healthcare Camp', 'Education Support',
                'Housing Assistance', 'Job Training', 'Language Classes',
                'Cultural Integration', 'Financial Literacy', 'Women Empowerment'
            ])
            
            service_data = {
                'ngo_id': ngo_id,
                'organization_name': org_name,
                'title': service_title,
                'description': fake.paragraph(nb_sentences=3),
                'location': random.choice(TN_CITIES),
                'service_date': fake.date_time_between(start_date='now', end_date='+30d'),
                'eligibility': fake.paragraph(nb_sentences=1),
                'contact_person': fake.name(),
                'contact_phone': generate_phone(),
                'posted_date': fake.date_time_between(start_date='-30d', end_date='now'),
                'status': 'active'
            }
            
            # Insert service
            service_id = mongo.db.services.insert_one(service_data).inserted_id
            
            services.append({
                'id': str(service_id),
                'title': service_title,
                'organization_name': org_name
            })
    
    return services

def generate_policies(count=5):
    """Generate sample government policies"""
    print(f"Generating {count} government policies...")
    policies = []
    
    policy_titles = [
        'Migrant Worker Protection Act',
        'Healthcare Access for Migrant Workers',
        'Educational Support for Migrant Children',
        'Housing Regulations for Migrant Workers',
        'Minimum Wage Enforcement for Migrant Labor',
        'Social Security Benefits for Interstate Workers',
        'Skill Development Program for Migrant Workers',
        'Cultural Integration Initiative'
    ]
    
    with app.app_context():
        for i in range(min(count, len(policy_titles))):
            # Create policy
            policy_data = {
                'title': policy_titles[i],
                'description': fake.paragraph(nb_sentences=5),
                'sector': random.choice(COMPANY_SECTORS),
                'published_date': fake.date_time_between(start_date='-180d', end_date='now'),
                'effective_date': fake.date_time_between(start_date='now', end_date='+90d'),
                'created_by': 'Department of Labor Welfare',
                'status': 'active'
            }
            
            # Insert policy
            policy_id = mongo.db.policies.insert_one(policy_data).inserted_id
            
            policies.append({
                'id': str(policy_id),
                'title': policy_titles[i]
            })
    
    return policies

def generate_helplines(count=5):
    """Generate sample helpline numbers"""
    print(f"Generating {count} helpline numbers...")
    helplines = []
    
    helpline_titles = [
        'Emergency Migrant Assistance',
        'Healthcare Helpline',
        'Legal Aid Helpline',
        'Women and Child Safety',
        'Labor Rights Helpline',
        'Mental Health Support',
        'Anti-Trafficking Helpline'
    ]
    
    with app.app_context():
        for i in range(min(count, len(helpline_titles))):
            # Create helpline
            helpline_data = {
                'title': helpline_titles[i],
                'description': fake.paragraph(nb_sentences=2),
                'phone_number': generate_phone(),
                'alternate_number': generate_phone() if random.random() > 0.5 else None,
                'email': fake.email(),
                'department': fake.company(),
                'hours': '24x7' if random.random() > 0.5 else '9 AM - 6 PM',
                'status': 'active'
            }
            
            # Insert helpline
            helpline_id = mongo.db.helplines.insert_one(helpline_data).inserted_id
            
            helplines.append({
                'id': str(helpline_id),
                'title': helpline_titles[i],
                'phone_number': helpline_data['phone_number']
            })
    
    return helplines

def main():
    """Main function to generate all test data"""
    print("Starting test data generation for MigrantConnectTN...")
    
    # Ask for confirmation before clearing collections
    response = input("This will clear all existing data. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        return
    
    # Clear all collections
    clear_collections()
    
    # Generate data
    admin = generate_admin()
    migrants = generate_migrants(20)  # 20 migrants
    employers = generate_employers(5)  # 5 employers
    ngos = generate_ngos(3)  # 3 NGOs
    bg_checkers = generate_bg_checkers(5)  # 5 background checkers
    policies = generate_policies(5)  # 5 policies
    helplines = generate_helplines(5)  # 5 helplines
    
    # Print summary
    print("\nTest data generation complete!")
    print("\nAdmin credentials:")
    print(f"  Email: {admin['email']}")
    print(f"  Password: admin123")
    print(f"  Unique ID: {admin['unique_id']}")
    
    print("\nSample migrant credentials (approved only):")
    for migrant in migrants:
        if migrant['status'] == 'approved':
            print(f"  Name: {migrant['name']}")
            print(f"  Mobile: {migrant['mobile']}")
            print(f"  Unique ID: {migrant['unique_id']}")
            print(f"  Password: default123")
            print("")
    
    print("\nSample employer credentials (approved only):")
    for employer in employers:
        if employer['status'] == 'approved':
            print(f"  Company: {employer['company_name']}")
            print(f"  Email: {employer['email']}")
            print(f"  Mobile: {employer['mobile']}")
            print(f"  Unique ID: {employer['unique_id']}")
            print(f"  Password: default123")
            print("")
    
    print("\nBackground checker credentials:")
    for bg_checker in bg_checkers:
        print(f"  Name: {bg_checker['name']}")
        print(f"  Email: {bg_checker['email']}")
        print(f"  Area: {bg_checker['area_assigned']}")
        print(f"  Unique ID: {bg_checker['unique_id']}")
        print(f"  Password: default123")
        print("")
    
    print("Note: All users have the default password 'default123'")
    print("You can use the unique IDs to log in to the system.")

if __name__ == '__main__':
    main()
