from app import create_app, mongo
from datetime import datetime
from bson.objectid import ObjectId
import random

app = create_app()

def init_healthcare_services():
    with app.app_context():
        # First check if we already have healthcare services
        existing_services = mongo.db.services.find_one({"category": "Healthcare"})
        if existing_services:
            print("Healthcare services already exist. Skipping initialization.")
            return
        
        # Get all NGOs with healthcare services
        ngos = list(mongo.db.ngos.find({"services": {"$in": ["Healthcare"]}}))        
        if not ngos:
            print("No NGOs with healthcare services found. Please run init_ngos.py first.")
            return
        
        print(f"Found {len(ngos)} NGOs with healthcare services")
        
        # Healthcare service types
        service_types = [
            "General Medical Care",
            "Mental Health Support",
            "Maternal Care",
            "Child Healthcare",
            "Vaccination Programs",
            "Dental Services",
            "Eye Care",
            "Emergency Medical Assistance"
        ]
        
        # Create healthcare services for each NGO
        services_created = 0
        for ngo in ngos:
            # Create 1-3 healthcare services for each NGO
            num_services = random.randint(1, 3)
            for _ in range(num_services):
                service_type = random.choice(service_types)
                service = {
                    "category": "Healthcare",
                    "ngo_id": ngo["unique_id"],
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "views": random.randint(0, 100),
                    "details": {
                        "name": f"{service_type} - {ngo['name']}",
                        "type": service_type,
                        "location": ngo["area_served"],
                        "description": f"Providing {service_type.lower()} for migrants in {ngo['area_served']}",
                        "contact_phone": ngo["phone"],
                        "contact_email": ngo["email"],
                        "available_slots": random.randint(5, 30),
                        "is_free": random.choice([True, False])
                    }
                }
                
                result = mongo.db.services.insert_one(service)
                if result.inserted_id:
                    services_created += 1
                    print(f"Created healthcare service: {service['details']['name']}")
        
        print(f"Successfully created {services_created} healthcare services")

if __name__ == "__main__":
    init_healthcare_services()
    print("Healthcare services initialization complete!")
