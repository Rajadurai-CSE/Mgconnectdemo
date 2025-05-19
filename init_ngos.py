from datetime import datetime
import pymongo
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import uuid

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = pymongo.MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/mgconnecttndeemo"))
db = client.get_default_database()

def init_ngos():
    # Clear existing data
    db.ngos.delete_many({})
    db.credentials.delete_many({"user_type": "ngo"})
    
    # Create test NGOs for different districts
    ngos_data = [
        {
            "name": "Tamil Nadu Labor Rights Foundation",
            "email": "tnlrf@example.org",
            "phone": "9876543220",
            "area_served": "Chennai",
            "services": ["Legal Aid", "Education", "Healthcare"],
            "password": "ngo123"
        },
        {
            "name": "Migrant Workers Welfare Association",
            "email": "mwwa@example.org",
            "phone": "9876543221",
            "area_served": "Coimbatore",
            "services": ["Housing", "Job Training", "Legal Aid"],
            "password": "ngo123"
        },
        {
            "name": "Rural Development Trust",
            "email": "rdt@example.org",
            "phone": "9876543222",
            "area_served": "Madurai",
            "services": ["Healthcare", "Education", "Financial Aid"],
            "password": "ngo123"
        },
        {
            "name": "Workers Unity Coalition",
            "email": "wuc@example.org",
            "phone": "9876543223",
            "area_served": "Trichy",
            "services": ["Legal Aid", "Advocacy", "Community Support"],
            "password": "ngo123"
        },
        {
            "name": "Migrant Family Support Center",
            "email": "mfsc@example.org",
            "phone": "9876543224",
            "area_served": "Salem",
            "services": ["Childcare", "Education", "Healthcare"],
            "password": "ngo123"
        }
    ]
    
    # Create NGOs
    for ngo_data in ngos_data:
        # Generate a unique ID for the NGO with NGO prefix
        ngo_id = f"NGO{str(uuid.uuid4().int)[:6]}"
        
        # Create the NGO profile in dedicated collection
        ngo_profile = {
            'name': ngo_data["name"],
            'email': ngo_data["email"],
            'phone': ngo_data["phone"],
            'area_served': ngo_data["area_served"],
            'services': ngo_data["services"],
            'unique_id': ngo_id,
            'created_at': datetime.utcnow(),
            'status': 'active',
            'verified': True,
            'service_count': 0,
            'last_active': datetime.utcnow()
        }
        
        # Insert into ngos collection
        result = db.ngos.insert_one(ngo_profile)
        
        # Create credentials in credentials collection
        password_hash = generate_password_hash(ngo_data["password"])
        credential_data = {
            'user_id': str(result.inserted_id),
            'unique_id': ngo_id,
            'password_hash': password_hash,
            'user_type': 'ngo',
            'mobile': ngo_data["phone"],
            'email': ngo_data["email"],
            'created_at': datetime.utcnow(),
            'last_login': None,
            'status': 'active',
            'password_reset_token': None,
            'password_reset_expires': None
        }
        db.credentials.insert_one(credential_data)
        
        print(f"Created NGO {ngo_id} for {ngo_data['area_served']}")

def init_services():
    # Create some services offered by NGOs
    db.services.delete_many({})
    
    services = [
        {
            "name": "Free Legal Consultation",
            "description": "Legal advice for migrant workers on labor laws and rights",
            "category": "Legal Aid",
            "location": "Chennai",
            "availability": "Monday-Friday, 10AM-4PM",
            "contact": "9876543220",
            "eligibility": "All registered migrant workers"
        },
        {
            "name": "Vocational Training",
            "description": "Skills development program for construction and factory work",
            "category": "Job Training",
            "location": "Coimbatore",
            "availability": "Weekends, 9AM-5PM",
            "contact": "9876543221",
            "eligibility": "Registered migrant workers aged 18-45"
        },
        {
            "name": "Medical Camp",
            "description": "Free health check-ups and basic medications",
            "category": "Healthcare",
            "location": "Madurai",
            "availability": "First Sunday of every month, 8AM-2PM",
            "contact": "9876543222",
            "eligibility": "All migrant workers and their families"
        },
        {
            "name": "Child Education Support",
            "description": "After-school programs for children of migrant workers",
            "category": "Education",
            "location": "Trichy",
            "availability": "Monday-Friday, 4PM-6PM",
            "contact": "9876543223",
            "eligibility": "Children aged 6-14 of registered migrant workers"
        },
        {
            "name": "Emergency Housing Assistance",
            "description": "Temporary shelter for displaced migrant workers",
            "category": "Housing",
            "location": "Salem",
            "availability": "24/7 Emergency Service",
            "contact": "9876543224",
            "eligibility": "Migrant workers in emergency situations"
        }
    ]
    
    # Get NGOs to associate services with
    ngos = list(db.ngos.find())
    
    for i, service in enumerate(services):
        # Associate each service with an NGO
        ngo = ngos[i % len(ngos)]
        
        service_data = {
            "name": service["name"],
            "description": service["description"],
            "category": service["category"],
            "location": service["location"],
            "availability": service["availability"],
            "contact": service["contact"],
            "eligibility": service["eligibility"],
            "ngo_id": str(ngo["_id"]),
            "ngo_name": ngo["name"],
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        db.services.insert_one(service_data)
        print(f"Created service: {service['name']} by {ngo['name']}")

if __name__ == "__main__":
    print("Initializing NGOs and services...")
    init_ngos()
    init_services()
    print("Initialization complete!")
