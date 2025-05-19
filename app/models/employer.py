from app import mongo
from datetime import datetime
from bson.objectid import ObjectId
import uuid
from app.utils.sms import send_approval_notification, send_rejection_notification, send_sms

class Employer:
    @staticmethod
    def create_profile(company_name, industry, address, city, state, contact_person, contact_phone, 
                       company_size, registration_number, description, organized=True, email=None):
        """
        Create a new employer profile
        """
        # Generate a unique ID for the employer
        employer_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        
        document_data = {
            'employer_id': employer_id,
            'company_info': {
                'company_name': company_name,
                'industry': industry,
                'address': address,
                'city': city,
                'state': state,
                'contact_person': contact_person,
                'contact_phone': contact_phone,
                'email': email,
                'company_size': company_size,
                'registration_number': registration_number,
                'description': description,
                'organized': organized
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'active',
            'verification_status': 'approved' if organized else 'pending',
            'employees': [],
            'jobs_posted': []
        }
        
        result = mongo.db.employers.insert_one(document_data)
        return str(result.inserted_id), employer_id
    
    @staticmethod
    def get_profile_by_id(employer_id):
        """
        Get employer profile by ID
        """
        return mongo.db.employers.find_one({"_id": ObjectId(employer_id)})
    
    @staticmethod
    def get_profile_by_employer_id(employer_id):
        """
        Get employer profile by employer ID
        """
        return mongo.db.employers.find_one({"employer_id": employer_id})
    
    @staticmethod
    def approve_unorganized_company(employer_id, approved_by=None):
        """
        Approve an unorganized company by admin/bg checker
        """
        # Get employer profile for sending notification
        employer = Employer.get_profile_by_id(employer_id)
        
        result = mongo.db.employers.update_one(
            {"_id": ObjectId(employer_id)},
            {"$set": {
                "verification_status": "approved",
                "approved_by": approved_by,
                "approval_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        
        # Send SMS notification if approved and contact phone is available
        if result.modified_count > 0 and employer:
            contact_phone = employer.get('company_info', {}).get('contact_phone')
            company_name = employer.get('company_info', {}).get('company_name', 'Your company')
            employer_unique_id = employer.get('employer_id', 'Not assigned')
            
            if contact_phone:
                message = f"Congratulations! Your unorganized company '{company_name}' has been approved. Your Employer ID is {employer_unique_id}. You can now post jobs and manage migrant workers on MigrantConnectTN."
                send_sms(contact_phone, message)
                
        return result.modified_count > 0
    
    @staticmethod
    def reject_unorganized_company(employer_id, reason=None, rejected_by=None):
        """
        Reject an unorganized company by admin/bg checker
        """
        # Get employer profile for sending notification
        employer = Employer.get_profile_by_id(employer_id)
        
        result = mongo.db.employers.update_one(
            {"_id": ObjectId(employer_id)},
            {"$set": {
                "verification_status": "rejected",
                "rejection_reason": reason,
                "rejected_by": rejected_by,
                "rejection_date": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "inactive"
            }}
        )
        
        # Send SMS notification if rejected and contact phone is available
        if result.modified_count > 0 and employer:
            contact_phone = employer.get('company_info', {}).get('contact_phone')
            company_name = employer.get('company_info', {}).get('company_name', 'Your company')
            reason_text = f" Reason: {reason}" if reason else ""
            
            if contact_phone:
                message = f"Your unorganized company '{company_name}' registration has been rejected.{reason_text} Please contact our support center for assistance."
                send_sms(contact_phone, message)
                
        return result.modified_count > 0
    
    @staticmethod
    def post_job(employer_id, title, description, location, salary_range, job_type, duration=None, 
                 skills_required=None, experience_required=None, education_required=None):
        """
        Post a new job
        """
        job_id = f"JOB-{uuid.uuid4().hex[:8].upper()}"
        
        job_data = {
            'job_id': job_id,
            'employer_id': employer_id,
            'title': title,
            'description': description,
            'location': location,
            'salary_range': salary_range,
            'job_type': job_type,  # 'full-time', 'part-time', 'contract', 'seasonal'
            'duration': duration,
            'skills_required': skills_required or [],
            'experience_required': experience_required,
            'education_required': education_required,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'active',
            'applicants': [],
            'views': 0
        }
        
        # Insert job into jobs collection
        mongo.db.jobs.insert_one(job_data)
        
        # Update employer's jobs_posted array
        mongo.db.employers.update_one(
            {"_id": ObjectId(employer_id)},
            {"$push": {"jobs_posted": job_id}}
        )
        
        return job_id
    
    @staticmethod
    def get_job(job_id):
        """
        Get job details by job ID
        """
        return mongo.db.jobs.find_one({"job_id": job_id})
    
    @staticmethod
    def get_all_jobs(filters=None, limit=None, skip=None):
        """
        Get all jobs with optional filters
        """
        query = filters or {"status": "active"}
        cursor = mongo.db.jobs.find(query)
        
        if skip is not None:
            cursor = cursor.skip(skip)
        if limit is not None:
            cursor = cursor.limit(limit)
            
        return list(cursor)
    
    @staticmethod
    def get_employer_jobs(employer_id):
        """
        Get all jobs posted by an employer
        """
        return list(mongo.db.jobs.find({"employer_id": employer_id}))
    
    @staticmethod
    def add_migrant_employee(employer_id, migrant_id, migrant_name, job_title, start_date, salary=None):
        """
        Add a migrant as an employee
        """
        employee_data = {
            "migrant_id": migrant_id,
            "migrant_name": migrant_name,
            "job_title": job_title,
            "start_date": start_date,
            "end_date": None,
            "salary": salary,
            "status": "active",
            "added_at": datetime.utcnow()
        }
        
        # Add to employer's employees
        mongo.db.employers.update_one(
            {"_id": ObjectId(employer_id)},
            {"$push": {"employees": employee_data}}
        )
        
        # Also update migrant's employment history
        from app.models.migrant import Migrant
        
        employer = Employer.get_profile_by_id(employer_id)
        if employer:
            company_name = employer['company_info']['company_name']
            Migrant.add_employment_record(
                migrant_id, employer_id, company_name, job_title, start_date, None, salary
            )
        
        return True
    
    @staticmethod
    def end_employee_employment(employer_id, migrant_id, end_date=None):
        """
        End employment of a migrant
        """
        if not end_date:
            end_date = datetime.utcnow()
        
        # Update employer's employee record
        mongo.db.employers.update_one(
            {
                "_id": ObjectId(employer_id),
                "employees.migrant_id": migrant_id,
                "employees.status": "active"
            },
            {"$set": {
                "employees.$.end_date": end_date,
                "employees.$.status": "inactive"
            }}
        )
        
        # Also update migrant's employment record
        from app.models.migrant import Migrant
        Migrant.end_employment(migrant_id, employer_id, end_date)
        
        return True
    
    @staticmethod
    def get_pending_unorganized_companies():
        """
        Get all pending unorganized companies
        """
        query = {
            "company_info.organized": False,
            "verification_status": "pending"
        }
        return list(mongo.db.employers.find(query))
    
    @staticmethod
    def track_job_view(job_id):
        """
        Track a view on a job posting
        """
        mongo.db.jobs.update_one(
            {"job_id": job_id},
            {"$inc": {"views": 1}}
        )
