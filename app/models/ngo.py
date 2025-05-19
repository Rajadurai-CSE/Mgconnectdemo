from app import mongo
from datetime import datetime
from bson.objectid import ObjectId
import uuid

class NGO:
    @staticmethod
    def create_profile(user_id, ngo_info, documents=None):
        document_data = {
            'user_id': user_id,
            'ngo_info': ngo_info,
            'documents': documents or [],
            'status': 'pending',  # 'pending', 'approved', 'rejected'
            'created_at': datetime.utcnow(),
            'services': {
                'housing': [],
                'legal_aid': [],
                'education': [],
                'scholarships': []
            }
        }
        return mongo.db.ngos.insert_one(document_data)
    
    @staticmethod
    def get_profile(user_id):
        # First try to find by unique_id (for NGOxxxxxx format IDs)
        if isinstance(user_id, str) and user_id.startswith('NGO'):
            return mongo.db.ngos.find_one({"unique_id": user_id})
            
        # Then try by user_id
        profile = mongo.db.ngos.find_one({"user_id": user_id})
        if profile:
            return profile
            
        # Finally try by _id if it's a valid ObjectId
        try:
            return mongo.db.ngos.find_one({"_id": ObjectId(user_id)})
        except:
            return None
    
    @staticmethod
    def approve_profile(ngo_id):
        # Generate unique ID for NGO
        unique_id = f"NGO-{uuid.uuid4().hex[:8].upper()}"
        mongo.db.ngos.update_one(
            {"_id": ObjectId(ngo_id)},
            {"$set": {"status": "approved", "ngo_id": unique_id}}
        )
        return unique_id
    
    @staticmethod
    def reject_profile(ngo_id, reason=None):
        mongo.db.ngos.update_one(
            {"_id": ObjectId(ngo_id)},
            {"$set": {"status": "rejected", "rejection_reason": reason}}
        )

    @staticmethod
    def add_housing_service(ngo_id, housing_details):
        housing_id = str(ObjectId())
        housing_data = {
            'id': housing_id,
            'details': housing_details,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        mongo.db.ngos.update_one(
            {"_id": ObjectId(ngo_id)},
            {"$push": {"services.housing": housing_data}}
        )
        return housing_id
    
    @staticmethod
    def add_legal_service(ngo_id, legal_details):
        legal_id = str(ObjectId())
        legal_data = {
            'id': legal_id,
            'details': legal_details,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        mongo.db.ngos.update_one(
            {"_id": ObjectId(ngo_id)},
            {"$push": {"services.legal_aid": legal_data}}
        )
        return legal_id
    
    @staticmethod
    def add_education_service(ngo_id, education_details):
        education_id = str(ObjectId())
        education_data = {
            'id': education_id,
            'details': education_details,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        mongo.db.ngos.update_one(
            {"_id": ObjectId(ngo_id)},
            {"$push": {"services.education": education_data}}
        )
        return education_id
    
    @staticmethod
    def add_scholarship(ngo_id, scholarship_details):
        scholarship_id = str(ObjectId())
        scholarship_data = {
            'id': scholarship_id,
            'details': scholarship_details,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        mongo.db.ngos.update_one(
            {"_id": ObjectId(ngo_id)},
            {"$push": {"services.scholarships": scholarship_data}}
        )
        return scholarship_id
    
    @staticmethod
    def get_all_housing_services():
        ngo_data = list(mongo.db.ngos.find({"status": "approved"}))
        services = []
        for ngo in ngo_data:
            for service in ngo.get('services', {}).get('housing', []):
                service['ngo_name'] = ngo.get('ngo_info', {}).get('name', 'Unknown NGO')
                service['ngo_contact'] = ngo.get('ngo_info', {}).get('contact', 'N/A')
                services.append(service)
        return services
    
    @staticmethod
    def get_all_legal_services():
        ngo_data = list(mongo.db.ngos.find({"status": "approved"}))
        services = []
        for ngo in ngo_data:
            for service in ngo.get('services', {}).get('legal_aid', []):
                service['ngo_name'] = ngo.get('ngo_info', {}).get('name', 'Unknown NGO')
                service['ngo_contact'] = ngo.get('ngo_info', {}).get('contact', 'N/A')
                services.append(service)
        return services
    
    @staticmethod
    def get_all_education_services():
        ngo_data = list(mongo.db.ngos.find({"status": "approved"}))
        services = []
        for ngo in ngo_data:
            for service in ngo.get('services', {}).get('education', []):
                service['ngo_name'] = ngo.get('ngo_info', {}).get('name', 'Unknown NGO')
                service['ngo_contact'] = ngo.get('ngo_info', {}).get('contact', 'N/A')
                services.append(service)
        return services
    
    @staticmethod
    def get_all_scholarships():
        ngo_data = list(mongo.db.ngos.find({"status": "approved"}))
        scholarships = []
        for ngo in ngo_data:
            for scholarship in ngo.get('services', {}).get('scholarships', []):
                scholarship['ngo_name'] = ngo.get('ngo_info', {}).get('name', 'Unknown NGO')
                scholarship['ngo_contact'] = ngo.get('ngo_info', {}).get('contact', 'N/A')
                scholarships.append(scholarship)
        return scholarships
