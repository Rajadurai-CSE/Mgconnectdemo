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

def init_bg_checkers():
    # Clear existing data
    db.bg_checkers.delete_many({})
    db.credentials.delete_many({"user_type": "bg_checker"})
    
    # Create test background checkers for different districts
    districts = [
        {
            "name": "Rajesh Kumar",
            "email": "rajesh@mgconnecttn.gov.in",
            "phone": "9876543210",
            "area_assigned": "Chennai",
            "password": "checker123"
        },
        {
            "name": "Priya Sharma",
            "email": "priya@mgconnecttn.gov.in",
            "phone": "9876543211",
            "area_assigned": "Coimbatore",
            "password": "checker123"
        },
        {
            "name": "Anand Singh",
            "email": "anand@mgconnecttn.gov.in",
            "phone": "9876543212",
            "area_assigned": "Madurai",
            "password": "checker123"
        },
        {
            "name": "Lakshmi Narayanan",
            "email": "lakshmi@mgconnecttn.gov.in",
            "phone": "9876543213",
            "area_assigned": "Trichy",
            "password": "checker123"
        },
        {
            "name": "Mohammed Ismail",
            "email": "ismail@mgconnecttn.gov.in",
            "phone": "9876543214",
            "area_assigned": "Salem",
            "password": "checker123"
        }
    ]
    
    # Create background checkers
    for district in districts:
        # Generate a unique ID for the background checker with BGK prefix
        bg_checker_id = f"BGK{str(uuid.uuid4().int)[:6]}"
        
        # Create the bg_checker profile in dedicated collection
        checker_data = {
            'name': district["name"],
            'email': district["email"],
            'phone': district["phone"],
            'area_assigned': district["area_assigned"],
            'department': 'Verification Department',
            'unique_id': bg_checker_id,
            'created_at': datetime.utcnow(),
            'status': 'active',
            'verified_migrants_count': 0,
            'last_active': datetime.utcnow()
        }
        
        # Insert into bg_checkers collection
        result = db.bg_checkers.insert_one(checker_data)
        
        # Create credentials in credentials collection
        password_hash = generate_password_hash(district["password"])
        credential_data = {
            'user_id': str(result.inserted_id),
            'unique_id': bg_checker_id,
            'password_hash': password_hash,
            'user_type': 'bg_checker',
            'mobile': district["phone"],
            'email': district["email"],
            'created_at': datetime.utcnow(),
            'last_login': None,
            'status': 'active',
            'password_reset_token': None,
            'password_reset_expires': None
        }
        db.credentials.insert_one(credential_data)
        
        print(f"Created background checker {bg_checker_id} for {district['area_assigned']}")

def init_pending_migrants():
    # Create some pending migrant profiles for testing
    districts = ["Chennai", "Coimbatore", "Madurai", "Trichy", "Salem"]
    
    # Clear existing test data
    db.migrants.delete_many({"test_data": True})
    
    for i, district in enumerate(districts):
        for j in range(3):  # 3 migrants per district
            migrant_data = {
                "personal_info": {
                    "name": f"Test Migrant {i*3+j+1}",
                    "age": 25 + j,
                    "gender": "Male" if j % 2 == 0 else "Female",
                    "mobile": f"98765{i}{j}321",
                    "email": f"migrant{i*3+j+1}@example.com",
                    "current_address": f"123 Test Street, {district}, Tamil Nadu",
                    "permanent_address": "456 Home Street, Bihar",
                    "aadhar": f"1234{i}{j}7890{i}{j}1234"
                },
                "work_info": {
                    "skills": ["Construction", "Farming"],
                    "experience": f"{j+2} years",
                    "education": "10th Standard",
                    "languages": ["Hindi", "Tamil"]
                },
                "status": "pending",
                "created_at": datetime.utcnow(),
                "test_data": True
            }
            
            db.migrants.insert_one(migrant_data)
            print(f"Created pending migrant in {district}")

if __name__ == "__main__":
    print("Initializing background checkers and test data...")
    init_bg_checkers()
    init_pending_migrants()
    print("Initialization complete!")
