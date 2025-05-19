from app import mongo
from datetime import datetime
from bson.objectid import ObjectId
import uuid
from app.utils.sms import send_approval_notification, send_rejection_notification, send_sms

class Migrant:
    @staticmethod
    def create_profile(name, dob, aadhar, mobile, current_address, native_state, native_address,
                      job_source, referral_contact, contractor_name, contractor_number, company, 
                      company_type, company_sector, documents=None, added_by=None, email=None):
        """
        Create a new migrant profile
        """
        # Generate a unique ID for the migrant (will be used for verification)
        application_id = str(uuid.uuid4())[:8].upper()
        
        # If added by employer, set different default status
        if added_by and added_by.get('type') == 'employer':
            status = 'employer_approved'
            verification_status = 'pending'
        else:
            status = 'pending'
            verification_status = 'pending'
        
        document_data = {
            'personal_info': {
                'name': name,
                'dob': dob,
                'aadhar': aadhar,
                'mobile': mobile,
                'current_address': current_address,
                'native_state': native_state,
                'native_address': native_address,
                'job_source': job_source,
                'referral_contact': referral_contact,
                'contractor_name': contractor_name,
                'contractor_number': contractor_number,
                'company': company,
                'company_type': company_type,
                'company_sector': company_sector
            },
            # If email is provided, store it separately for future use
            'email': email,
            'documents': documents or {},
            'status': status,  # 'pending', 'approved', 'rejected', 'employer_approved'
            'verification_status': verification_status,  # 'pending', 'verified', 'rejected'
            'employer_status': 'pending',  # 'pending', 'approved', 'rejected'
            'application_id': application_id,
            'migrant_id': None,  # Will be assigned upon approval
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'added_by': added_by,
            'employment_history': [],
            'current_employment': None
        }
        
        result = mongo.db.migrants.insert_one(document_data)
        return str(result.inserted_id), application_id
    
    @staticmethod
    def get_profile(migrant_id):
        """
        Get migrant profile by ID
        """
        return mongo.db.migrants.find_one({"_id": ObjectId(migrant_id)})
    
    @staticmethod
    def get_profile_by_application_id(application_id):
        """
        Get migrant profile by application ID
        """
        return mongo.db.migrants.find_one({"application_id": application_id})
    
    @staticmethod
    def get_profile_by_migrant_id(migrant_id):
        """
        Get migrant profile by migrant ID (assigned after approval)
        """
        return mongo.db.migrants.find_one({"migrant_id": migrant_id})
    
    @staticmethod
    def approve_profile(migrant_id, verified_by=None):
        """
        Approve migrant profile by background checker
        """
        # Generate unique ID for migrant
        unique_id = f"MIG-{uuid.uuid4().hex[:8].upper()}"
        
        update_data = {
            "verification_status": "verified",
            "verified_by": verified_by,
            "verified_at": datetime.utcnow(),
            "migrant_id": unique_id,
            "updated_at": datetime.utcnow()
        }
        
        # Get migrant profile to access mobile number for notification
        migrant = Migrant.get_profile(migrant_id)
        
        # Only update status if not already approved by employer
        if migrant and migrant.get('status') != 'employer_approved':
            update_data["status"] = "approved"
        
        # Update the migrant record in the database
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": update_data}
        )
        
        # Send SMS notification if mobile number is available
        if migrant and migrant.get('personal_info', {}).get('mobile'):
            mobile = migrant['personal_info']['mobile']
            name = migrant['personal_info'].get('name', 'Migrant')
            send_approval_notification(mobile, 'migrant', name, unique_id)
            
        return unique_id
    
    @staticmethod
    def reject_profile(migrant_id, reason=None, rejected_by=None):
        """
        Reject migrant profile by background checker
        """
        # Get migrant profile to access mobile number for notification
        migrant = Migrant.get_profile(migrant_id)
        
        # Update the database record
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": {
                "status": "rejected",
                "verification_status": "rejected",
                "rejection_reason": reason,
                "rejected_by": rejected_by,
                "rejected_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Send SMS notification if mobile number is available
        if migrant and migrant.get('personal_info', {}).get('mobile'):
            mobile = migrant['personal_info']['mobile']
            send_rejection_notification(mobile, 'migrant', reason)
    
    @staticmethod
    def employer_approve(migrant_id, employer_id):
        """
        Approve migrant by employer
        """
        # Get migrant profile to access mobile number for notification
        migrant = Migrant.get_profile(migrant_id)
        
        result = mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": {
                "employer_status": "approved",
                "approved_by_employer": employer_id,
                "employer_approval_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Send SMS notification if mobile number is available
        if result.modified_count > 0 and migrant and migrant.get('personal_info', {}).get('mobile'):
            mobile = migrant['personal_info']['mobile']
            name = migrant['personal_info'].get('name', 'Migrant')
            migrant_id = migrant.get('migrant_id', 'Not Assigned')
            
            # Get employer name
            employer = mongo.db.employers.find_one({"_id": ObjectId(employer_id)})
            employer_name = employer.get('company_name', 'Your employer') if employer else 'Your employer'
            
            # Custom message for employer approval
            message = f"Good news! {employer_name} has approved your employment registration. Your Migrant ID is {migrant_id}. Welcome to MigrantConnectTN."
            send_sms(mobile, message)
            
        return result.modified_count > 0
    
    @staticmethod
    def employer_reject(migrant_id, employer_id, reason=None):
        """
        Reject migrant by employer
        """
        # Get migrant profile to access mobile number for notification
        migrant = Migrant.get_profile(migrant_id)
        
        result = mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": {
                "employer_status": "rejected",
                "rejected_by_employer": employer_id,
                "employer_rejection_reason": reason,
                "employer_rejection_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Send SMS notification if mobile number is available
        if result.modified_count > 0 and migrant and migrant.get('personal_info', {}).get('mobile'):
            mobile = migrant['personal_info']['mobile']
            
            # Get employer name
            employer = mongo.db.employers.find_one({"_id": ObjectId(employer_id)})
            employer_name = employer.get('company_name', 'An employer') if employer else 'An employer'
            
            reason_text = f" Reason: {reason}" if reason else ""
            
            # Custom message for employer rejection
            message = f"{employer_name} has not approved your employment application.{reason_text} Please contact our support center for assistance."
            send_sms(mobile, message)
            
        return result.modified_count > 0
    
    @staticmethod
    def add_employment_record(migrant_id, employer_id, employer_name, job_title, start_date, end_date=None, salary=None):
        """
        Add employment record for migrant
        """
        employment_record = {
            "employer_id": employer_id,
            "employer_name": employer_name,
            "job_title": job_title,
            "start_date": start_date,
            "end_date": end_date,
            "salary": salary,
            "status": "active" if not end_date else "completed",
            "created_at": datetime.utcnow()
        }
        
        # Add to employment history
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$push": {"employment_history": employment_record}}
        )
        
        # If active employment, update current_employment
        if not end_date:
            mongo.db.migrants.update_one(
                {"_id": ObjectId(migrant_id)},
                {"$set": {"current_employment": employment_record}}
            )
        
        return True
    
    @staticmethod
    def end_employment(migrant_id, employer_id, end_date=None):
        """
        End current employment for migrant
        """
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get migrant profile
        migrant = Migrant.get_profile(migrant_id)
        if not migrant or not migrant.get('current_employment'):
            return False
        
        current_employment = migrant['current_employment']
        if current_employment['employer_id'] != employer_id:
            return False
        
        # Update employment history record
        mongo.db.migrants.update_one(
            {
                "_id": ObjectId(migrant_id),
                "employment_history.employer_id": employer_id,
                "employment_history.status": "active"
            },
            {"$set": {
                "employment_history.$.end_date": end_date,
                "employment_history.$.status": "completed"
            }}
        )
        
        # Clear current employment
        mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": {"current_employment": None}}
        )
        
        return True
    
    @staticmethod
    def get_pending_employer_verifications(employer_id):
        """
        Get all migrants pending employer verification
        """
        query = {
            "personal_info.company": employer_id,
            "employer_status": "pending"
        }
        return list(mongo.db.migrants.find(query))
    
    @staticmethod
    def get_all_migrants(filters=None, limit=None, skip=None):
        """
        Get all migrants with optional filters
        """
        query = filters or {}
        cursor = mongo.db.migrants.find(query)
        
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
            
        return list(cursor)
