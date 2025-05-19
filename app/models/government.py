from app import mongo
from datetime import datetime
from bson.objectid import ObjectId
import uuid

class Government:
    @staticmethod
    def create_bg_checker(name, email, password_hash, phone, area_assigned):
        # Generate a unique ID for the background checker with BGK prefix
        bg_checker_id = f"BGK{str(uuid.uuid4().int)[:6]}"
        
        # Create the bg_checker profile in dedicated collection
        checker_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'area_assigned': area_assigned,
            'department': 'Verification Department',
            'unique_id': bg_checker_id,
            'created_at': datetime.utcnow(),
            'status': 'active',
            'verified_migrants_count': 0,
            'last_active': datetime.utcnow()
        }
        
        # Insert into bg_checkers collection
        result = mongo.db.bg_checkers.insert_one(checker_data)
        
        # Create credentials in credentials collection
        from app.models.auth import Auth
        Auth.create_credentials(
            user_id=str(result.inserted_id),
            unique_id=bg_checker_id,
            password=password_hash,  # Already hashed
            user_type='bg_checker',
            mobile=phone,
            email=email
        )
        
        return result
    
    @staticmethod
    def get_all_bg_checkers():
        return list(mongo.db.bg_checkers.find())
    
    @staticmethod
    def get_pending_verifications(area=None):
        query = {"status": "pending"}
        if area:
            query["personal_info.current_address"] = {"$regex": area, "$options": "i"}
        return list(mongo.db.migrants.find(query))
    
    @staticmethod
    def process_verification(migrant_id, status, notes=None, verified_by=None):
        update_data = {
            "status": status,
            "verification_notes": notes,
            "verified_by": verified_by,
            "verified_at": datetime.utcnow()
        }
        
        if status == "approved":
            # Generate unique ID for migrant
            migrant_id_number = f"MIG-{uuid.uuid4().hex[:8].upper()}"
            update_data["migrant_id"] = migrant_id_number
        
        result = mongo.db.migrants.update_one(
            {"_id": ObjectId(migrant_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_migration_stats():
        # Get total count of approved migrants
        total_migrants = mongo.db.migrants.count_documents({"status": "approved"})
        
        # Get sector-wise distribution
        pipeline = [
            {"$match": {"status": "approved"}},
            {"$group": {"_id": "$personal_info.company_sector", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sector_stats = list(mongo.db.migrants.aggregate(pipeline))
        
        # Get state-wise distribution
        pipeline = [
            {"$match": {"status": "approved"}},
            {"$group": {"_id": "$personal_info.native_state", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        state_stats = list(mongo.db.migrants.aggregate(pipeline))
        
        # Get monthly registrations
        pipeline = [
            {"$match": {"status": "approved"}},
            {"$project": {
                "month": {"$month": "$created_at"},
                "year": {"$year": "$created_at"}
            }},
            {"$group": {
                "_id": {"month": "$month", "year": "$year"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}}
        ]
        monthly_stats = list(mongo.db.migrants.aggregate(pipeline))
        
        return {
            "total_migrants": total_migrants,
            "sector_stats": sector_stats,
            "state_stats": state_stats,
            "monthly_stats": monthly_stats
        }
    
    @staticmethod
    def add_emergency_helpline(district, police_helpline, labor_helpline, women_helpline=None, child_helpline=None):
        helpline_data = {
            "district": district,
            "police_helpline": police_helpline,
            "labor_helpline": labor_helpline,
            "women_helpline": women_helpline,
            "child_helpline": child_helpline,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Check if helpline for district already exists
        existing = mongo.db.helplines.find_one({"district": district})
        if existing:
            # Update existing helpline
            mongo.db.helplines.update_one(
                {"district": district},
                {"$set": helpline_data}
            )
            return str(existing["_id"])
        else:
            # Create new helpline
            result = mongo.db.helplines.insert_one(helpline_data)
            return str(result.inserted_id)
    
    @staticmethod
    def get_all_helplines():
        return list(mongo.db.helplines.find())
    
    @staticmethod
    def get_helpline_by_district(district):
        return mongo.db.helplines.find_one({"district": district})
    
    @staticmethod
    def add_policy(title, description, sector=None, document_url=None, published_date=None):
        policy_data = {
            "title": title,
            "description": description,
            "sector": sector,
            "document_url": document_url,
            "published_date": published_date or datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "status": "active"
        }
        
        result = mongo.db.policies.insert_one(policy_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all_policies(sector=None):
        query = {"status": "active"}
        if sector:
            query["sector"] = sector
        return list(mongo.db.policies.find(query).sort("published_date", -1))
    
    @staticmethod
    def get_policy(policy_id):
        return mongo.db.policies.find_one({"_id": ObjectId(policy_id)})
