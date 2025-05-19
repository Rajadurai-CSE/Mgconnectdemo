from app import create_app, mongo
from app.models.auth import Auth
from app.models.migrant import Migrant
from app.models.employer import Employer
from app.models.ngo import NGO
from app.models.government import Government
from datetime import datetime
from bson.objectid import ObjectId
import os

# Create a Flask application context
app = create_app()
app.app_context().push()

# Clear all collections first
def reset_database():
    print("Resetting database...")
    collections = [
        'credentials', 'migrants', 'employers', 'ngos', 'admins', 
        'bg_checkers', 'policies', 'helplines', 'jobs', 'housing_services',
        'legal_services', 'education_services', 'scholarships', 'support_requests'
    ]
    
    for collection in collections:
        mongo.db[collection].delete_many({})
    print("Database reset complete.")

# Create admin user
def create_admin():
    print("Creating admin user...")
    # First create the admin profile
    admin_id = mongo.db.admins.insert_one({
        'name': 'System Administrator',
        'email': 'admin@mgconnecttn.gov.in',
        'mobile': '9999999999',
        'department': 'Information Technology',
        'created_at': datetime.utcnow()
    }).inserted_id
    
    # Create admin credentials
    Auth.create_credentials(
        user_id=str(admin_id),
        unique_id='ADMIN001',
        password='admin123',  # This would be changed in production
        user_type='admin',
        mobile='9999999999',
        email='admin@mgconnecttn.gov.in'
    )
    print("Admin user created successfully.")

# Create background checker
def create_bg_checker():
    print("Creating background checker...")
    # Create background checker
    from app.models.government import Government
    
    # Create background checker in users collection
    bg_checker_id = mongo.db.users.insert_one({
        'name': 'BG Checker 1',
        'email': 'bgcheck@mgconnecttn.gov.in',
        'phone': '8888888888',
        'department': 'Verification Department',
        'district': 'Chennai',
        'area_assigned': 'Chennai',  # Important for bg_checker_dashboard function
        'role': 'bg_checker',
        'status': 'active',
        'created_at': datetime.utcnow(),
        'created_by': 'ADMIN001'
    }).inserted_id
    
    # Create bg_checker credentials
    Auth.create_credentials(
        user_id=str(bg_checker_id),
        unique_id='BGCHK001',
        password='checker123',  # This would be changed in production
        user_type='bg_checker',
        mobile='8888888888',
        email='bgcheck@mgconnecttn.gov.in'
    )
    print("Background checker created successfully.")

# Create employer
def create_employer():
    print("Creating employer...")
    # Create the employer profile
    employer_id = mongo.db.employers.insert_one({
        'company_name': 'TN Construction Ltd',
        'contact_person': 'Ramesh Kumar',
        'email': 'hr@tnconstruction.com',
        'mobile': '7777777777',
        'address': '123 Anna Salai, Chennai',
        'district': 'Chennai',
        'industry': 'Construction',
        'company_size': '100-500',
        'gstin': '33AABCT1234Z1Z5',
        'verification_status': 'approved',
        'created_at': datetime.utcnow(),
        'job_postings': []
    }).inserted_id
    
    # Create employer credentials
    Auth.create_credentials(
        user_id=str(employer_id),
        unique_id='EMP001',
        password='employer123',  # This would be changed in production
        user_type='employer',
        mobile='7777777777',
        email='hr@tnconstruction.com'
    )
    print("Employer created successfully.")

# Create NGO
def create_ngo():
    print("Creating NGO...")
    # Create the NGO profile
    ngo_id = mongo.db.ngos.insert_one({
        'name': 'Migrant Workers Welfare Association',
        'registration_number': 'NGO/TN/2022/12345',
        'contact_person': 'Lakshmi Subramanian',
        'email': 'info@mwwa.org',
        'mobile': '6666666666',
        'address': '45 Gandhi Road, Coimbatore',
        'district': 'Coimbatore',
        'areas_of_operation': ['Housing', 'Legal Aid', 'Education'],
        'verification_status': 'approved',
        'created_at': datetime.utcnow(),
        'housing_services': [],
        'legal_services': [],
        'education_services': [],
        'scholarships': []
    }).inserted_id
    
    # Create NGO credentials
    Auth.create_credentials(
        user_id=str(ngo_id),
        unique_id='NGO001',
        password='ngo123',  # This would be changed in production
        user_type='ngo',
        mobile='6666666666',
        email='info@mwwa.org'
    )
    print("NGO created successfully.")

# Create migrant
def create_migrant():
    print("Creating migrant...")
    # Create the migrant profile
    migrant_id = mongo.db.migrants.insert_one({
        'personal_info': {
            'name': 'Suresh Bihari',
            'gender': 'Male',
            'dob': '1990-05-15',
            'mobile': '5555555555',
            'email': 'suresh.b@example.com',
            'home_state': 'Bihar',
            'home_district': 'Patna',
            'current_address': '78 Workers Colony, Sriperumbudur',
            'current_district': 'Kanchipuram',
            'skills': ['Construction', 'Electrical', 'Plumbing'],
            'languages': ['Hindi', 'Tamil (Basic)'],
            'education': 'Secondary',
            'dependents': 3,
            'emergency_contact': {
                'name': 'Amit Bihari',
                'relation': 'Brother',
                'mobile': '5555555556'
            }
        },
        'documents': {
            'aadhar': 'XXXX-XXXX-XXXX',
            'voter_id': 'BHR123456789',
            'bank_account': {
                'bank_name': 'State Bank of India',
                'account_number': 'XXXXXXXX5678',
                'ifsc_code': 'SBIN0000123'
            }
        },
        'employment': {
            'current_employer': 'TN Construction Ltd',
            'employer_id': None,  # Will be filled after creation
            'job_role': 'Construction Worker',
            'wage_type': 'Daily',
            'wage_amount': 500,
            'start_date': '2023-01-15'
        },
        'family': {
            'spouse_name': 'Priya Devi',
            'children': [
                {'name': 'Rahul Bihari', 'age': 10, 'education': 'Primary'},
                {'name': 'Neha Bihari', 'age': 8, 'education': 'Primary'}
            ]
        },
        'status': 'approved',
        'migrant_id': 'MIG001',
        'verification_status': 'verified',
        'created_at': datetime.utcnow(),
        'approved_at': datetime.utcnow(),
        'approved_by': 'BGCHK001'
    }).inserted_id
    
    # Create migrant credentials
    Auth.create_credentials(
        user_id=str(migrant_id),
        unique_id='MIG001',
        password='migrant123',  # This would be changed in production
        user_type='migrant',
        mobile='5555555555',
        email='suresh.b@example.com'
    )
    
    # Update the employer reference
    employer = mongo.db.employers.find_one({'company_name': 'TN Construction Ltd'})
    if employer:
        mongo.db.migrants.update_one(
            {'_id': migrant_id},
            {'$set': {'employment.employer_id': str(employer['_id'])}}
        )
    
    print("Migrant created successfully.")

# Create policies
def create_policies():
    print("Creating policies...")
    policies = [
        {
            'title': 'Minimum Wage Policy for Migrant Workers',
            'description': 'Details of minimum wage rates for different sectors applicable to migrant workers in Tamil Nadu.',
            'content': 'As per the Minimum Wages Act, the minimum wage for unskilled workers is Rs. 350 per day. Semi-skilled workers shall be paid a minimum of Rs. 450 per day. Skilled workers shall be paid a minimum of Rs. 550 per day.',
            'sector': 'Wages',
            'created_at': datetime.utcnow(),
            'created_by': 'ADMIN001'
        },
        {
            'title': 'Housing Guidelines for Migrant Workers',
            'description': 'Standards for housing and accommodation provided to migrant workers.',
            'content': 'Employers providing housing to migrant workers must ensure minimum space of 50 sq ft per person, adequate ventilation, clean drinking water, and sanitation facilities. Housing must be located within 5 km of worksite or transportation must be provided.',
            'sector': 'Housing',
            'created_at': datetime.utcnow(),
            'created_by': 'ADMIN001'
        },
        {
            'title': 'Education Rights for Children of Migrant Workers',
            'description': 'Information about education rights and opportunities for migrant children.',
            'content': 'Children of migrant workers have the right to education under the Right to Education Act. Local schools must admit children of migrant workers even in the middle of the academic year. Special bridge courses are available to help children adapt to the local language and curriculum.',
            'sector': 'Education',
            'created_at': datetime.utcnow(),
            'created_by': 'ADMIN001'
        }
    ]
    
    mongo.db.policies.insert_many(policies)
    print("Policies created successfully.")

# Create helplines
def create_helplines():
    print("Creating helplines...")
    helplines = [
        {
            'name': 'Migrant Worker Emergency Helpline',
            'phone': '1800-123-4567',
            'languages': ['Tamil', 'Hindi', 'Bengali', 'Odia'],
            'description': '24x7 helpline for migrant workers in emergency situations',
            'created_at': datetime.utcnow(),
            'created_by': 'ADMIN001'
        },
        {
            'name': 'Labor Department Complaint Line',
            'phone': '1800-425-6789',
            'languages': ['Tamil', 'Hindi', 'English'],
            'description': 'Helpline for wage disputes and labor law violations',
            'created_at': datetime.utcnow(),
            'created_by': 'ADMIN001'
        },
        {
            'name': 'Healthcare Assistance Helpline',
            'phone': '1800-233-4567',
            'languages': ['Tamil', 'Hindi', 'Telugu'],
            'description': 'Medical assistance and healthcare information for migrant workers',
            'created_at': datetime.utcnow(),
            'created_by': 'ADMIN001'
        }
    ]
    
    mongo.db.helplines.insert_many(helplines)
    print("Helplines created successfully.")

# Create NGO services
def create_ngo_services():
    print("Creating NGO services...")
    
    ngo = mongo.db.ngos.find_one({'name': 'Migrant Workers Welfare Association'})
    if not ngo:
        print("NGO not found. Skipping service creation.")
        return
    
    # Housing services
    housing_services = [
        {
            'ngo_id': str(ngo['_id']),
            'service_name': 'Temporary Shelter for Migrant Families',
            'location': 'Coimbatore',
            'capacity': 100,
            'facilities': ['Beds', 'Clean Water', 'Kitchen', 'Bathrooms'],
            'eligibility': 'Migrant workers with families who need temporary accommodation',
            'contact_details': {
                'name': 'Housing Coordinator',
                'phone': '6666666601',
                'email': 'housing@mwwa.org'
            },
            'available_slots': 75,
            'created_at': datetime.utcnow(),
            'views': 25
        },
        {
            'ngo_id': str(ngo['_id']),
            'service_name': 'Single Workers Dormitory',
            'location': 'Tiruppur',
            'capacity': 200,
            'facilities': ['Bunk Beds', 'Lockers', 'Mess', 'Recreation Room'],
            'eligibility': 'Single male migrant workers',
            'contact_details': {
                'name': 'Dormitory Manager',
                'phone': '6666666602',
                'email': 'dorm@mwwa.org'
            },
            'available_slots': 120,
            'created_at': datetime.utcnow(),
            'views': 42
        }
    ]
    
    housing_ids = mongo.db.housing_services.insert_many(housing_services).inserted_ids
    
    # Update NGO with housing service IDs
    mongo.db.ngos.update_one(
        {'_id': ngo['_id']},
        {'$set': {'housing_services': [str(id) for id in housing_ids]}}
    )
    
    # Legal services
    legal_services = [
        {
            'ngo_id': str(ngo['_id']),
            'service_name': 'Wage Dispute Resolution',
            'description': 'Legal assistance for migrant workers facing wage payment issues',
            'service_type': 'Consultation',
            'availability': 'Monday to Friday, 10 AM to 5 PM',
            'languages': ['Tamil', 'Hindi', 'Bengali'],
            'contact_details': {
                'name': 'Legal Coordinator',
                'phone': '6666666603',
                'email': 'legal@mwwa.org'
            },
            'created_at': datetime.utcnow(),
            'views': 35
        },
        {
            'ngo_id': str(ngo['_id']),
            'service_name': 'Document Assistance',
            'description': 'Help with various documentation needs including Aadhar enrollment, bank accounts, etc.',
            'service_type': 'Document Processing',
            'availability': 'Wednesday and Saturday, 9 AM to 3 PM',
            'languages': ['Tamil', 'Hindi', 'Telugu', 'Odia'],
            'contact_details': {
                'name': 'Documentation Team',
                'phone': '6666666604',
                'email': 'docs@mwwa.org'
            },
            'created_at': datetime.utcnow(),
            'views': 48
        }
    ]
    
    legal_ids = mongo.db.legal_services.insert_many(legal_services).inserted_ids
    
    # Update NGO with legal service IDs
    mongo.db.ngos.update_one(
        {'_id': ngo['_id']},
        {'$set': {'legal_services': [str(id) for id in legal_ids]}}
    )
    
    # Education services
    education_services = [
        {
            'ngo_id': str(ngo['_id']),
            'service_name': 'Bridge School for Migrant Children',
            'description': 'Bridging program to help migrant children transition to local schools',
            'location': 'Coimbatore',
            'age_group': '6-14 years',
            'capacity': 50,
            'languages': ['Tamil', 'Hindi'],
            'contact_details': {
                'name': 'Education Coordinator',
                'phone': '6666666605',
                'email': 'education@mwwa.org'
            },
            'enrollment_process': 'Visit the center with the child\'s previous school records if available',
            'created_at': datetime.utcnow(),
            'views': 28
        },
        {
            'ngo_id': str(ngo['_id']),
            'service_name': 'Adult Literacy Program',
            'description': 'Evening classes for adult migrant workers to learn basic reading and writing',
            'location': 'Multiple centers across Coimbatore',
            'age_group': 'Adults',
            'capacity': 100,
            'languages': ['Tamil', 'Hindi', 'Bengali'],
            'contact_details': {
                'name': 'Adult Education Team',
                'phone': '6666666606',
                'email': 'adulted@mwwa.org'
            },
            'enrollment_process': 'Drop in at any center between 6 PM and 8 PM on weekdays',
            'created_at': datetime.utcnow(),
            'views': 32
        }
    ]
    
    education_ids = mongo.db.education_services.insert_many(education_services).inserted_ids
    
    # Update NGO with education service IDs
    mongo.db.ngos.update_one(
        {'_id': ngo['_id']},
        {'$set': {'education_services': [str(id) for id in education_ids]}}
    )
    
    # Scholarships
    scholarships = [
        {
            'ngo_id': str(ngo['_id']),
            'name': 'Migrant Children Education Scholarship',
            'description': 'Financial assistance for school fees, books, and uniforms',
            'amount': 5000,
            'eligibility': 'Children of migrant workers studying in classes 1-10',
            'application_process': 'Submit application form with school enrollment proof and parent\'s migrant worker ID',
            'deadline': '2023-07-31',
            'contact_details': {
                'name': 'Scholarship Coordinator',
                'phone': '6666666607',
                'email': 'scholarship@mwwa.org'
            },
            'created_at': datetime.utcnow(),
            'views': 55
        },
        {
            'ngo_id': str(ngo['_id']),
            'name': 'Higher Education Grant for Migrant Youths',
            'description': 'Funding support for migrant children pursuing higher education',
            'amount': 15000,
            'eligibility': 'Children of migrant workers who have completed class 12 and gained admission to college',
            'application_process': 'Submit application with college admission letter, class 12 marksheet, and parent\'s migrant worker ID',
            'deadline': '2023-08-15',
            'contact_details': {
                'name': 'Higher Education Team',
                'phone': '6666666608',
                'email': 'highered@mwwa.org'
            },
            'created_at': datetime.utcnow(),
            'views': 42
        }
    ]
    
    scholarship_ids = mongo.db.scholarships.insert_many(scholarships).inserted_ids
    
    # Update NGO with scholarship IDs
    mongo.db.ngos.update_one(
        {'_id': ngo['_id']},
        {'$set': {'scholarships': [str(id) for id in scholarship_ids]}}
    )
    
    print("NGO services created successfully.")

# Create job postings
def create_job_postings():
    print("Creating job postings...")
    
    employer = mongo.db.employers.find_one({'company_name': 'TN Construction Ltd'})
    if not employer:
        print("Employer not found. Skipping job posting creation.")
        return
    
    job_postings = [
        {
            'employer_id': str(employer['_id']),
            'title': 'Construction Workers',
            'description': 'Hiring workers for a large residential construction project',
            'job_type': 'Full-time',
            'location': 'Chennai',
            'skills_required': ['Construction', 'Physical Strength', 'Teamwork'],
            'experience_required': '1-3 years',
            'wage_type': 'Daily',
            'wage_amount': 500,
            'benefits': ['Accommodation', 'Meals', 'Transport'],
            'vacancies': 25,
            'deadline': '2023-06-30',
            'contact_details': {
                'name': 'HR Department',
                'phone': '7777777701',
                'email': 'jobs@tnconstruction.com'
            },
            'created_at': datetime.utcnow(),
            'status': 'active',
            'views': 120
        },
        {
            'employer_id': str(employer['_id']),
            'title': 'Skilled Electricians',
            'description': 'Skilled electricians needed for commercial building project',
            'job_type': 'Full-time',
            'location': 'Chennai',
            'skills_required': ['Electrical Wiring', 'Circuit Installation', 'Safety Standards'],
            'experience_required': '3-5 years',
            'wage_type': 'Daily',
            'wage_amount': 800,
            'benefits': ['Accommodation', 'Health Insurance', 'Transport'],
            'vacancies': 10,
            'deadline': '2023-06-15',
            'contact_details': {
                'name': 'HR Department',
                'phone': '7777777701',
                'email': 'jobs@tnconstruction.com'
            },
            'created_at': datetime.utcnow(),
            'status': 'active',
            'views': 85
        }
    ]
    
    job_ids = mongo.db.jobs.insert_many(job_postings).inserted_ids
    
    # Update employer with job posting IDs
    mongo.db.employers.update_one(
        {'_id': employer['_id']},
        {'$set': {'job_postings': [str(id) for id in job_ids]}}
    )
    
    print("Job postings created successfully.")

# Function to summarize all credentials for easy access
def summarize_credentials():
    print("\n" + "="*80)
    print("CREDENTIAL SUMMARY FOR MGCONNECTTNDEEMO DATABASE")
    print("="*80)
    print("\nUse these credentials to log into the system:\n")
    
    credentials = [
        {"role": "Admin", "unique_id": "ADMIN001", "password": "admin123", "email": "admin@mgconnecttn.gov.in", "mobile": "9999999999"},
        {"role": "Background Checker", "unique_id": "BGCHK001", "password": "checker123", "email": "bgcheck@mgconnecttn.gov.in", "mobile": "8888888888"},
        {"role": "Employer", "unique_id": "EMP001", "password": "employer123", "email": "hr@tnconstruction.com", "mobile": "7777777777"},
        {"role": "NGO", "unique_id": "NGO001", "password": "ngo123", "email": "info@mwwa.org", "mobile": "6666666666"},
        {"role": "Migrant", "unique_id": "MIG001", "password": "migrant123", "email": "suresh.b@example.com", "mobile": "5555555555"}
    ]
    
    # Print a table of credentials
    format_str = "{:<20} {:<15} {:<15} {:<30} {:<15}"
    print(format_str.format("Role", "Unique ID", "Password", "Email", "Mobile"))
    print("-"*95)
    
    for cred in credentials:
        print(format_str.format(
            cred["role"], 
            cred["unique_id"], 
            cred["password"], 
            cred["email"], 
            cred["mobile"]
        ))
    
    print("\nNOTE: These passwords are for development purposes only. In production, secure passwords should be used.")
    print("="*80)

# Main function to initialize database
def init_db():
    print("\nInitializing database: mgconnecttndeemo")
    print("This will reset all existing data in the database.")
    print("\nPopulating database...")
    
    reset_database()
    create_admin()
    create_bg_checker()
    create_employer()
    create_ngo()
    create_migrant()
    create_policies()
    create_helplines()
    create_ngo_services()
    create_job_postings()
    
    print("\nDatabase initialization complete!")
    summarize_credentials()

if __name__ == "__main__":
    init_db()
