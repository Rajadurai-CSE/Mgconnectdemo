from app import mongo
from datetime import datetime
from bson.objectid import ObjectId

class ChildEducation:
    @staticmethod
    def add_enrollment_service(name, description, service_type, location, eligibility, contact_person, 
                               contact_number, contact_email, documents_required=None, created_by=None):
        """
        Add a new child enrollment service provided by NGO or government
        """
        service_data = {
            'name': name,
            'description': description,
            'service_type': service_type,  # 'ngo' or 'government'
            'location': location,
            'eligibility': eligibility,
            'contact_person': contact_person,
            'contact_number': contact_number,
            'contact_email': contact_email,
            'documents_required': documents_required or [],
            'created_by': created_by,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        return mongo.db.enrollment_services.insert_one(service_data)
    
    @staticmethod
    def get_all_enrollment_services(service_type=None):
        """
        Get all enrollment services optionally filtered by type
        """
        query = {'status': 'active'}
        if service_type:
            query['service_type'] = service_type
        return list(mongo.db.enrollment_services.find(query))
    
    @staticmethod
    def add_scholarship(name, description, education_level, amount, duration, eligibility, 
                        application_process, documents_required=None, deadline=None, 
                        provider_type=None, provider_id=None):
        """
        Add a new scholarship opportunity provided by NGO or government
        """
        scholarship_data = {
            'name': name,
            'description': description,
            'education_level': education_level,
            'amount': amount,
            'duration': duration,
            'eligibility': eligibility,
            'application_process': application_process,
            'documents_required': documents_required or [],
            'deadline': deadline,
            'provider_type': provider_type,  # 'ngo' or 'government'
            'provider_id': provider_id,
            'created_at': datetime.utcnow(),
            'status': 'active'
        }
        return mongo.db.scholarships.insert_one(scholarship_data)
    
    @staticmethod
    def get_all_scholarships(education_level=None, provider_type=None):
        """
        Get all scholarships optionally filtered by education level or provider type
        """
        query = {'status': 'active'}
        if education_level:
            query['education_level'] = education_level
        if provider_type:
            query['provider_type'] = provider_type
        return list(mongo.db.scholarships.find(query))
    
    @staticmethod
    def apply_for_enrollment(migrant_id, service_id, child_name, child_age, child_gender, 
                            previous_education, documents=None, additional_info=None):
        """
        Apply for a child enrollment service
        """
        application_data = {
            'migrant_id': migrant_id,
            'service_id': service_id,
            'child_name': child_name,
            'child_age': child_age,
            'child_gender': child_gender,
            'previous_education': previous_education,
            'documents': documents or [],
            'additional_info': additional_info,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        return mongo.db.enrollment_applications.insert_one(application_data)
    
    @staticmethod
    def apply_for_scholarship(migrant_id, scholarship_id, child_name, child_age, 
                             current_education, documents=None, additional_info=None):
        """
        Apply for a scholarship
        """
        application_data = {
            'migrant_id': migrant_id,
            'scholarship_id': scholarship_id,
            'child_name': child_name,
            'child_age': child_age,
            'current_education': current_education,
            'documents': documents or [],
            'additional_info': additional_info,
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        return mongo.db.scholarship_applications.insert_one(application_data)
    
    @staticmethod
    def get_migrant_applications(migrant_id):
        """
        Get all education/scholarship applications for a migrant
        """
        enrollment_apps = list(mongo.db.enrollment_applications.find({'migrant_id': migrant_id}))
        scholarship_apps = list(mongo.db.scholarship_applications.find({'migrant_id': migrant_id}))
        
        return {
            'enrollment': enrollment_apps,
            'scholarships': scholarship_apps
        }
