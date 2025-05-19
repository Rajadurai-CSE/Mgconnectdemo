from app import create_app, mongo
from datetime import datetime
from bson.objectid import ObjectId

# Create and configure the app
app = create_app()

# Tamil Nadu Districts
districts = [
    "Ariyalur", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri", 
    "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Kanyakumari", 
    "Karur", "Krishnagiri", "Madurai", "Nagapattinam", "Namakkal", 
    "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet", 
    "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", 
    "Thoothukudi", "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", 
    "Tiruvallur", "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram",
    "Virudhunagar"
]

# District Police Helplines
district_police_helplines = []

for district in districts:
    # Generate a unique helpline number for each district
    # Format: First 5 digits are 04422 followed by district-specific 5 digits
    district_code = districts.index(district) + 1
    helpline_number = f"04422-{district_code:05d}"
    
    helpline = {
        "district": district,
        "helpline_number": helpline_number,
        "control_room": f"{district} District Police Control Room",
        "address": f"District Police Headquarters, {district}",
        "email": f"police@{district.lower()}.tn.gov.in",
        "emergency_contact_person": f"DSP, {district} District",
        "services": [
            "Emergency Response",
            "Crime Reporting",
            "Women Safety",
            "Lost & Found",
            "Public Assistance"
        ],
        "languages": ["Tamil", "English"],
        "additional_info": "In case of emergency, please dial 100 first",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # Add a few special contacts for specific districts
    if district == "Chennai":
        helpline["special_units"] = [
            {"name": "Women Helpdesk", "number": "044-28592750"},
            {"name": "Traffic Control Room", "number": "044-23452350"},
            {"name": "Cyber Crime Cell", "number": "044-24527777"}
        ]
    elif district == "Coimbatore":
        helpline["special_units"] = [
            {"name": "Women Helpdesk", "number": "0422-2300970"},
            {"name": "Traffic Control Room", "number": "0422-2301683"}
        ]
    elif district == "Madurai":
        helpline["special_units"] = [
            {"name": "Women Helpdesk", "number": "0452-2346302"},
            {"name": "Traffic Control Room", "number": "0452-2346300"}
        ]
    
    district_police_helplines.append(helpline)


def init_district_police():
    with app.app_context():
        print("Initializing database with district police helplines...")
        
        # Clear existing data
        mongo.db.district_police.drop()
        
        # Insert district police helplines
        mongo.db.district_police.insert_many(district_police_helplines)
        print(f"Added police helplines for {len(district_police_helplines)} districts")
        
        # Create index for faster search
        mongo.db.district_police.create_index("district")
        print("Created index on district field")
        
        print("District police helplines initialization complete!")

if __name__ == "__main__":
    init_district_police()
