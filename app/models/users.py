from flask_login import UserMixin
from app import mongo, login_manager
from bson.objectid import ObjectId
import uuid
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    # Check if this is a BGK ID (background checker)
    if user_id.startswith('BGK'):
        # Find by unique_id instead of _id
        user_data = mongo.db.credentials.find_one({"unique_id": user_id})
    else:
        # Try to convert to ObjectId for other user types
        try:
            user_data = mongo.db.credentials.find_one({"_id": ObjectId(user_id)})
        except:
            # If conversion fails, try finding by unique_id as fallback
            user_data = mongo.db.credentials.find_one({"unique_id": user_id})
    
    if user_data:
        # Get the user's profile data
        from app.models.auth import Auth
        user_profile = Auth.get_user_profile(user_data)
        
        # Create composite user object
        user_obj = {
            '_id': user_data['_id'],
            'email': user_data.get('email'),
            'role': user_data['user_type'],
            'user_data': user_profile,
            'unique_id': user_data.get('unique_id')  # Pass the unique_id
        }
        return User(user_obj)
    return None

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data
        self._id = user_data.get('_id')
        self.email = user_data.get('email')
        self.role = user_data.get('role')  # 'migrant', 'employer', 'ngo', 'admin', 'bg_checker'
        self.profile = user_data.get('user_data', {})
        
        # Store unique_id from credentials if available
        self.unique_id = user_data.get('unique_id')
        
    def get_id(self):
        # Return unique_id if available (for all user types)
        if self.unique_id:
            return str(self.unique_id)
        return str(self._id)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_bg_checker(self):
        return self.role == 'bg_checker'
    
    def is_employer(self):
        return self.role == 'employer'
    
    def is_migrant(self):
        return self.role == 'migrant'
    
    def is_ngo(self):
        return self.role == 'ngo'
        
    @staticmethod
    def get_by_unique_id(unique_id):
        from app.models.auth import Auth
        user_data = Auth.get_user_by_unique_id(unique_id)
        if user_data:
            user_profile = Auth.get_user_profile(user_data)
            user_obj = {
                '_id': user_data['_id'],
                'email': user_data.get('email'),
                'role': user_data['user_type'],
                'user_data': user_profile
            }
            return User(user_obj)
        return None
    
    @staticmethod
    def is_email_taken(email):
        return mongo.db.credentials.find_one({"email": email}) is not None
        
    @staticmethod
    def is_mobile_taken(mobile):
        return mongo.db.credentials.find_one({"mobile": mobile}) is not None
        
    @staticmethod
    def is_unique_id_taken(unique_id):
        return mongo.db.credentials.find_one({"unique_id": unique_id}) is not None

class Migrant:
    @staticmethod
    def create_profile(user_id, personal_info, documents):
        document_data = {
            'user_id': user_id,
            'personal_info': personal_info,
            'documents': documents,
            'status': 'pending',  # 'pending', 'approved', 'rejected'
            'migrant_id': None,  # Will be assigned upon approval
            'created_at': datetime.utcnow(),
            'jobs': []
        }
        return mongo.db.migrants.insert_one(document_data)
    
    @staticmethod
    def get_profile(user_id):
        return mongo.db.migrants.find_one({"user_id": user_id})
    
    @staticmethod
    def approve_profile(migrant_id):
        # Generate unique ID for migrant
        unique_id = f"MIG-{uuid.uuid4().hex[:8].upper()}"
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": {"status": "approved", "migrant_id": unique_id}}
        )
        return unique_id
    
    @staticmethod
    def reject_profile(migrant_id, reason=None):
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": {"status": "rejected", "rejection_reason": reason}}
        )

class Employer:
    @staticmethod
    def create_profile(user_id, company_info):
        document_data = {
            'user_id': user_id,
            'company_info': company_info,
            'created_at': datetime.utcnow(),
            'jobs_posted': []
        }
        return mongo.db.employers.insert_one(document_data)
    
    @staticmethod
    def get_profile(user_id):
        return mongo.db.employers.find_one({"user_id": user_id})
    
    @staticmethod
    def post_job(employer_id, job_details):
        job_id = str(ObjectId())
        job_data = {
            'job_id': job_id,
            'employer_id': employer_id,
            'details': job_details,
            'created_at': datetime.utcnow(),
            'status': 'active',
            'applicants': []
        }
        mongo.db.jobs.insert_one(job_data)
        mongo.db.employers.update_one(
            {"_id": ObjectId(employer_id)},
            {"$push": {"jobs_posted": job_id}}
        )
        return job_id
    
    @staticmethod
    def add_migrant(employer_id, migrant_id, job_details):
        # Add migrant to employer's records
        job_assignment = {
            'migrant_id': migrant_id,
            'job_details': job_details,
            'start_date': datetime.utcnow(),
            'status': 'active'
        }
        mongo.db.employers.update_one(
            {"_id": ObjectId(employer_id)},
            {"$push": {"employees": job_assignment}}
        )
        
        # Update migrant's job history
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$push": {"jobs": {
                'employer_id': employer_id,
                'job_details': job_details,
                'start_date': datetime.utcnow(),
                'status': 'active'
            }}}
        )

class Policy:
    @staticmethod
    def create_policy(title, description, sector=None, created_by=None):
        policy_data = {
            'title': title,
            'description': description,
            'sector': sector,  # None for all sectors
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        return mongo.db.policies.insert_one(policy_data)
    
    @staticmethod
    def get_policies(sector=None):
        if sector:
            return list(mongo.db.policies.find({"$or": [{"sector": sector}, {"sector": None}]}))
        return list(mongo.db.policies.find())
