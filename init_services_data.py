from app import create_app, mongo
from datetime import datetime
from bson.objectid import ObjectId
import random

# Create and configure the app
app = create_app()

# NGO IDs (you should replace these with actual NGO IDs from your database)
ngo_ids = [
    ObjectId(),  # NGO 1 - Legal Aid Foundation
    ObjectId(),  # NGO 2 - Housing Support Network
    ObjectId(),  # NGO 3 - Child Education Trust
    ObjectId(),  # NGO 4 - Migrant Support Foundation
    ObjectId(),  # NGO 5 - Labor Rights Initiative
]

# NGO Names
ngo_names = [
    "Legal Aid Foundation",
    "Housing Support Network",
    "Child Education Trust",
    "Migrant Support Foundation",
    "Labor Rights Initiative"
]

# Create NGO data
ngos_data = []
for i in range(5):
    ngo = {
        "_id": ngo_ids[i],
        "ngo_info": {
            "name": ngo_names[i],
            "registration_number": f"NGO{i+1000}",
            "establishment_date": datetime(2010 + i, 1, 1),
            "website": f"http://www.{ngo_names[i].lower().replace(' ', '')}.org",
            "description": f"A nonprofit organization dedicated to supporting migrant workers in Tamil Nadu through {ngo_names[i].lower()} services."
        },
        "contact_info": {
            "name": f"NGO Contact {i+1}",
            "phone": f"+91 9876{50000+i}",
            "email": f"contact@{ngo_names[i].lower().replace(' ', '')}.org",
            "address": f"{i+1} NGO Street, Chennai, Tamil Nadu",
            "whatsapp": f"9876{50000+i}"
        },
        "services": {
            "legal_aid": [],
            "housing": [],
            "education": [],
            "scholarships": []
        },
        "status": "approved",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    ngos_data.append(ngo)

# Legal Aid Services Data
legal_services = [
    {
        "name": "Labor Dispute Resolution",
        "description": "Free legal counsel and representation for wage and labor disputes",
        "service_days": "Monday, Wednesday, Friday",
        "service_hours": "10:00 AM - 4:00 PM",
        "eligibility": "All registered migrant workers",
        "documents_required": ["ID proof", "Employment contract", "Wage slips (if available)"]
    },
    {
        "name": "Document Assistance",
        "description": "Help with legal document preparation, translation, and attestation",
        "service_days": "Tuesday, Thursday",
        "service_hours": "9:00 AM - 3:00 PM",
        "eligibility": "All registered migrant workers",
        "documents_required": ["ID proof"]
    },
    {
        "name": "Workplace Rights Counseling",
        "description": "Information and advice on workplace rights and labor laws",
        "service_days": "Monday to Friday",
        "service_hours": "9:00 AM - 5:00 PM",
        "eligibility": "All migrant workers",
        "documents_required": ["None required"]
    },
    {
        "name": "Compensation Claims",
        "description": "Assistance with work injury and compensation claims",
        "service_days": "Monday, Wednesday, Friday",
        "service_hours": "10:00 AM - 4:00 PM",
        "eligibility": "Injured migrant workers",
        "documents_required": ["ID proof", "Medical reports", "Accident reports"]
    },
    {
        "name": "Legal Representation",
        "description": "Court representation for serious disputes and cases",
        "service_days": "By appointment",
        "service_hours": "10:00 AM - 4:00 PM",
        "eligibility": "Case-by-case basis",
        "documents_required": ["ID proof", "Case documents", "Prior consultation"]
    }
]

# Housing Services Data
housing_services = [
    {
        "name": "Emergency Shelter",
        "description": "Temporary housing for migrants in crisis situations",
        "service_days": "All days",
        "service_hours": "24 hours",
        "eligibility": "Migrants facing housing crisis",
        "documents_required": ["ID proof (if available)"],
        "capacity": "30 beds",
        "duration": "Up to 14 days"
    },
    {
        "name": "Rental Assistance",
        "description": "Financial aid for first month's rent and deposit",
        "service_days": "Monday to Friday",
        "service_hours": "10:00 AM - 4:00 PM",
        "eligibility": "Low-income migrant families",
        "documents_required": ["ID proof", "Income proof", "Rental agreement"],
        "amount": "Up to ₹10,000"
    },
    {
        "name": "Housing Search Support",
        "description": "Help finding safe and affordable housing options",
        "service_days": "Monday, Wednesday, Friday",
        "service_hours": "10:00 AM - 4:00 PM",
        "eligibility": "All registered migrant workers",
        "documents_required": ["ID proof"]
    },
    {
        "name": "Tenant Rights Education",
        "description": "Information sessions on tenant rights and responsibilities",
        "service_days": "Every Tuesday",
        "service_hours": "5:00 PM - 7:00 PM",
        "eligibility": "All migrant workers",
        "documents_required": ["None required"],
        "location": "Community hall"
    },
    {
        "name": "Housing Complaint Resolution",
        "description": "Mediation between tenants and landlords for dispute resolution",
        "service_days": "Thursday",
        "service_hours": "10:00 AM - 4:00 PM",
        "eligibility": "Migrant tenants with housing disputes",
        "documents_required": ["ID proof", "Rental agreement", "Evidence of issues"]
    }
]

# Education Services Data
education_services = [
    {
        "name": "School Enrollment Assistance",
        "description": "Help with enrolling children in local government schools",
        "service_days": "Monday to Friday",
        "service_hours": "9:00 AM - 3:00 PM",
        "eligibility": "Migrant families with children aged 6-14",
        "documents_required": ["Child's birth certificate", "Parent's ID proof"]
    },
    {
        "name": "After-School Program",
        "description": "Supervised homework help and educational activities",
        "service_days": "Monday to Friday",
        "service_hours": "4:00 PM - 6:00 PM",
        "eligibility": "School-going migrant children",
        "documents_required": ["School ID"],
        "location": "Community center"
    },
    {
        "name": "Language Support Classes",
        "description": "Tamil and English language classes for migrant children",
        "service_days": "Tuesday, Thursday",
        "service_hours": "4:00 PM - 5:30 PM",
        "eligibility": "Migrant children age 6+",
        "documents_required": ["None required"],
        "location": "NGO office"
    },
    {
        "name": "Educational Materials Support",
        "description": "Free textbooks, notebooks, and stationery for school children",
        "service_days": "First Saturday of every month",
        "service_hours": "10:00 AM - 1:00 PM",
        "eligibility": "Registered migrant children in school",
        "documents_required": ["School enrollment proof"]
    },
    {
        "name": "Parent Education Workshop",
        "description": "Information sessions for parents on supporting children's education",
        "service_days": "Last Sunday of every month",
        "service_hours": "10:00 AM - 12:00 PM",
        "eligibility": "Migrant parents",
        "documents_required": ["None required"],
        "location": "Community hall"
    }
]

# Scholarship Data
scholarship_services = [
    {
        "name": "Primary Education Scholarship",
        "description": "Financial support for primary school students",
        "amount": "₹5,000 per year",
        "eligibility": "Migrant children in grades 1-5",
        "application_deadline": "June 30 every year",
        "documents_required": ["School enrollment proof", "Parent's ID", "Income certificate"]
    },
    {
        "name": "Secondary Education Scholarship",
        "description": "Financial support for secondary school students",
        "amount": "₹8,000 per year",
        "eligibility": "Migrant children in grades 6-10",
        "application_deadline": "June 30 every year",
        "documents_required": ["School enrollment proof", "Previous year's marks", "Parent's ID"]
    },
    {
        "name": "Merit Scholarship",
        "description": "Financial reward for academic excellence",
        "amount": "₹10,000 per year",
        "eligibility": "Migrant children with 80%+ grades",
        "application_deadline": "July 31 every year",
        "documents_required": ["Mark sheets", "School certificate", "Parent's ID"]
    },
    {
        "name": "Vocational Training Scholarship",
        "description": "Support for vocational and skill training courses",
        "amount": "Up to ₹15,000",
        "eligibility": "Migrant youth aged 16-22",
        "application_deadline": "Quarterly applications",
        "documents_required": ["ID proof", "Course admission letter", "Income certificate"]
    },
    {
        "name": "Girl Child Education Scholarship",
        "description": "Special scholarship to promote girl child education",
        "amount": "₹12,000 per year",
        "eligibility": "Girl children from migrant families",
        "application_deadline": "June 30 every year",
        "documents_required": ["School enrollment proof", "Birth certificate", "Parent's ID"]
    }
]

# Emergency Helpline Data
emergency_helplines = [
    {
        "name": "Police Emergency",
        "phone": "100",
        "description": "For crime, theft, and security emergencies",
        "district": "All Districts",
        "hours": "24/7",
        "type": "Government"
    },
    {
        "name": "Ambulance Service",
        "phone": "108",
        "description": "Medical emergencies and ambulance services",
        "district": "All Districts",
        "hours": "24/7",
        "type": "Government"
    },
    {
        "name": "Women's Helpline",
        "phone": "1091",
        "description": "For women facing harassment or violence",
        "district": "All Districts",
        "hours": "24/7",
        "type": "Government"
    },
    {
        "name": "Child Helpline",
        "phone": "1098",
        "description": "For child welfare and protection issues",
        "district": "All Districts",
        "hours": "24/7",
        "type": "Government"
    },
    {
        "name": "Labor Helpline",
        "phone": "1800-425-1400",
        "description": "Reporting labor law violations and exploitation",
        "district": "All Districts",
        "hours": "8:00 AM - 8:00 PM",
        "type": "Government"
    },
    {
        "name": "Tamil Nadu Workers Resource Center",
        "phone": "044-2345-6789",
        "description": "NGO helpline for migrant worker issues",
        "district": "Chennai",
        "hours": "9:00 AM - 6:00 PM (Mon-Sat)",
        "type": "NGO"
    },
    {
        "name": "Migrant Support Hotline",
        "phone": "044-9876-5432",
        "description": "Multi-lingual support for migrant workers",
        "district": "Chennai",
        "hours": "8:00 AM - 8:00 PM (All days)",
        "type": "NGO"
    },
    {
        "name": "Housing Emergency Helpline",
        "phone": "044-8765-4321",
        "description": "For eviction and housing crisis situations",
        "district": "Chennai",
        "hours": "9:00 AM - 9:00 PM (All days)",
        "type": "NGO"
    },
    {
        "name": "Mental Health Support Line",
        "phone": "1800-599-0019",
        "description": "Mental health counseling and support",
        "district": "All Districts",
        "hours": "24/7",
        "type": "Government"
    },
    {
        "name": "Coimbatore Migrant Support",
        "phone": "0422-123-4567",
        "description": "Local support for migrants in Coimbatore",
        "district": "Coimbatore",
        "hours": "9:00 AM - 6:00 PM (Mon-Sat)",
        "type": "NGO"
    }
]

# Hospital Data for Emergency Services
hospitals = [
    {
        "name": "Government General Hospital",
        "type": "Government",
        "address": "Park Town, Chennai-600003",
        "contact": "044-2530-5000",
        "services": ["Emergency Care", "General Medicine", "Surgery", "Orthopedics"],
        "district": "Chennai",
        "location": "13.0827,80.2707"
    },
    {
        "name": "Tamil Nadu Government Multi Super Speciality Hospital",
        "type": "Government",
        "address": "Omandurar Estate, Chennai-600002",
        "contact": "044-2530-7000",
        "services": ["Emergency Care", "Specialty Care", "Critical Care"],
        "district": "Chennai",
        "location": "13.0698,80.2738"
    },
    {
        "name": "Government Royapettah Hospital",
        "type": "Government",
        "address": "Royapettah, Chennai-600014",
        "contact": "044-2813-1661",
        "services": ["Emergency Care", "General Medicine"],
        "district": "Chennai",
        "location": "13.0543,80.2638"
    },
    {
        "name": "Coimbatore Medical College Hospital",
        "type": "Government",
        "address": "Trichy Road, Coimbatore-641018",
        "contact": "0422-2301-393",
        "services": ["Emergency Care", "General Medicine", "Surgery"],
        "district": "Coimbatore",
        "location": "11.0168,76.9558"
    },
    {
        "name": "Madurai Medical College and Hospital",
        "type": "Government",
        "address": "Panthalkudi, Madurai-625020",
        "contact": "0452-2532-535",
        "services": ["Emergency Care", "General Medicine"],
        "district": "Madurai",
        "location": "9.9252,78.1198"
    },
    {
        "name": "Government Hospital of Thoracic Medicine",
        "type": "Government",
        "address": "Tambaram Sanatorium, Chennai-600047",
        "contact": "044-2237-1500",
        "services": ["Respiratory Care", "TB Treatment"],
        "district": "Chennai",
        "location": "12.9249,80.1270"
    },
    {
        "name": "Urban Primary Health Center",
        "type": "Government",
        "address": "Saidapet, Chennai-600015",
        "contact": "044-2467-1234",
        "services": ["Primary Care", "Maternal Care", "Child Health"],
        "district": "Chennai",
        "location": "13.0213,80.2231"
    },
    {
        "name": "Government Royapuram Hospital",
        "type": "Government",
        "address": "Royapuram, Chennai-600013",
        "contact": "044-2595-1012",
        "services": ["Emergency Care", "General Medicine"],
        "district": "Chennai",
        "location": "13.1192,80.2951"
    },
    {
        "name": "Salem Government Hospital",
        "type": "Government",
        "address": "Shevapet, Salem-636002",
        "contact": "0427-2311-542",
        "services": ["Emergency Care", "General Medicine"],
        "district": "Salem",
        "location": "11.6537,78.1585"
    },
    {
        "name": "Tirunelveli Medical College Hospital",
        "type": "Government",
        "address": "High Ground, Tirunelveli-627011",
        "contact": "0462-2572-733",
        "services": ["Emergency Care", "General Medicine", "Surgery"],
        "district": "Tirunelveli",
        "location": "8.7139,77.7567"
    }
]

def init_db():
    with app.app_context():
        print("Initializing database with migrant services data...")
        
        # Clear existing data
        mongo.db.ngos.drop()
        mongo.db.helplines.drop()
        mongo.db.hospitals.drop()
        
        # Insert NGOs
        mongo.db.ngos.insert_many(ngos_data)
        print(f"Added {len(ngos_data)} NGOs to the database")
        
        # Assign services to NGOs
        for ngo in ngos_data:
            ngo_id = ngo["_id"]
            
            # Assign legal services to Legal Aid and Migrant Support NGOs
            if ngo["ngo_info"]["name"] in ["Legal Aid Foundation", "Migrant Support Foundation", "Labor Rights Initiative"]:
                legal_services_subset = random.sample(legal_services, 3)
                mongo.db.ngos.update_one(
                    {"_id": ngo_id},
                    {"$set": {"services.legal_aid": legal_services_subset}}
                )
                print(f"Added legal services to {ngo['ngo_info']['name']}")
            
            # Assign housing services to Housing Support and Migrant Support NGOs
            if ngo["ngo_info"]["name"] in ["Housing Support Network", "Migrant Support Foundation"]:
                housing_services_subset = random.sample(housing_services, 3)
                mongo.db.ngos.update_one(
                    {"_id": ngo_id},
                    {"$set": {"services.housing": housing_services_subset}}
                )
                print(f"Added housing services to {ngo['ngo_info']['name']}")
            
            # Assign education services to Child Education and Migrant Support NGOs
            if ngo["ngo_info"]["name"] in ["Child Education Trust", "Migrant Support Foundation"]:
                education_services_subset = random.sample(education_services, 3)
                mongo.db.ngos.update_one(
                    {"_id": ngo_id},
                    {"$set": {"services.education": education_services_subset}}
                )
                print(f"Added education services to {ngo['ngo_info']['name']}")
                
                # Also add scholarships
                scholarship_services_subset = random.sample(scholarship_services, 2)
                mongo.db.ngos.update_one(
                    {"_id": ngo_id},
                    {"$set": {"services.scholarships": scholarship_services_subset}}
                )
                print(f"Added scholarships to {ngo['ngo_info']['name']}")
        
        # Insert Emergency Helplines
        mongo.db.helplines.insert_many(emergency_helplines)
        print(f"Added {len(emergency_helplines)} emergency helplines to the database")
        
        # Insert Hospitals
        mongo.db.hospitals.insert_many(hospitals)
        print(f"Added {len(hospitals)} hospitals to the database")
        
        print("Database initialization complete!")

if __name__ == "__main__":
    init_db()
