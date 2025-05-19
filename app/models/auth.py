from app import mongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import random
import string
from app.utils.sms import send_verification_notification

class Auth:
    @staticmethod
    def create_credentials(user_id, unique_id, password, user_type, mobile=None, email=None):
        """
        Create credentials for a user
        """
        password_hash = generate_password_hash(password)
        credential_data = {
            'user_id': user_id,  # Reference to user in respective collection
            'unique_id': unique_id,  # Unique ID used as username
            'password_hash': password_hash,
            'user_type': user_type,  # 'migrant', 'employer', 'ngo', 'bg_checker', 'admin'
            'mobile': mobile,
            'email': email,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'status': 'active',
            'password_reset_token': None,
            'password_reset_expires': None
        }
        return mongo.db.credentials.insert_one(credential_data)
    
    @staticmethod
    def get_user_by_unique_id(unique_id):
        """
        Get user credentials by unique ID
        """
        # Only find by unique_id - simple and direct approach
        return mongo.db.credentials.find_one({'unique_id': unique_id, 'status': 'active'})
    
    @staticmethod
    def verify_password(unique_id, password):
        """
        Verify user password
        """
        user = Auth.get_user_by_unique_id(unique_id)
        if not user:
            return None
        
        if check_password_hash(user['password_hash'], password):
            # Update last login time
            mongo.db.credentials.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.utcnow()}}
            )
            return user
        return None
    
    @staticmethod
    def generate_otp(mobile):
        """
        Generate OTP for password reset via mobile
        """
        # Find user by mobile
        user = mongo.db.credentials.find_one({'mobile': mobile, 'status': 'active'})
        if not user:
            return None
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        # Set expiration time (10 minutes)
        expires = datetime.utcnow() + timedelta(minutes=10)
        
        # Store OTP in database
        mongo.db.credentials.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password_reset_token': otp,
                'password_reset_expires': expires
            }}
        )
        
        # Send OTP via SMS
        send_verification_notification(mobile, otp)
        
        return {
            'user_id': str(user['_id']),
            'otp': otp,
            'mobile': mobile,
            'expires': expires
        }
    
    @staticmethod
    def verify_otp(mobile, otp):
        """
        Verify OTP for password reset
        """
        user = mongo.db.credentials.find_one({
            'mobile': mobile,
            'password_reset_token': otp,
            'status': 'active'
        })
        
        if not user:
            return False
        
        # Check if OTP is expired
        if user['password_reset_expires'] < datetime.utcnow():
            return False
        
        return True
    
    @staticmethod
    def reset_password(mobile, otp, new_password):
        """
        Reset password after OTP verification
        """
        if not Auth.verify_otp(mobile, otp):
            return False
        
        # Hash new password
        password_hash = generate_password_hash(new_password)
        
        # Update password and clear reset token
        result = mongo.db.credentials.update_one(
            {'mobile': mobile, 'password_reset_token': otp},
            {'$set': {
                'password_hash': password_hash,
                'password_reset_token': None,
                'password_reset_expires': None
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def change_password(user_id, current_password, new_password):
        """
        Change password for a user
        """
        user = mongo.db.credentials.find_one({'_id': ObjectId(user_id)})
        if not user:
            return False
        
        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            return False
        
        # Hash and update new password
        password_hash = generate_password_hash(new_password)
        result = mongo.db.credentials.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'password_hash': password_hash}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def generate_default_password():
        """
        Generate a random default password
        """
        # Generate an 8-character password with digits and letters
        chars = string.ascii_letters + string.digits
        return ''.join(random.choices(chars, k=8))
    
    @staticmethod
    def deactivate_user(user_id):
        """
        Deactivate a user account
        """
        result = mongo.db.credentials.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'status': 'inactive'}}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_user_type_collection(user_type):
        """
        Get the corresponding collection for a user type
        """
        collections = {
            'migrant': mongo.db.migrants,
            'employer': mongo.db.employers,
            'ngo': mongo.db.ngos,
            'bg_checker': mongo.db.bg_checkers,
            'admin': mongo.db.admins
        }
        return collections.get(user_type)
    
    @staticmethod
    def get_user_profile(credentials):
        """
        Get the full user profile based on credentials
        """
        user_type = credentials['user_type']
        user_id = credentials['user_id']
        unique_id = credentials.get('unique_id')
        
        collection = Auth.get_user_type_collection(user_type)
        if collection is None:
            return None
        
        # For background checkers, try to find by unique_id first
        if user_type == 'bg_checker' and unique_id:
            profile = collection.find_one({'unique_id': unique_id})
            if profile:
                return profile
                
        # For all other cases or as fallback, find by ObjectId
        try:
            return collection.find_one({'_id': ObjectId(user_id)})
        except:
            # If user_id is not a valid ObjectId, try as a string
            return collection.find_one({'_id': user_id})
