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
    def create_credentials(user_id, password, user_type, mobile=None, email=None, unique_id=None, approval_status='pending'):
        """
        Create credentials for a user
        
        Args:
            user_id: Reference to user in respective collection
            password: Plain text password
            user_type: Type of user (migrant, employer, ngo, bg_checker, admin)
            mobile: Mobile number
            email: Email address
            unique_id: Unique ID (will be assigned after approval)
            approval_status: Status of approval (pending, approved, rejected)
        """
        password_hash = generate_password_hash(password)
        credential_data = {
            'user_id': user_id,  # Reference to user in respective collection
            'password_hash': password_hash,
            'user_type': user_type,  # 'migrant', 'employer', 'ngo', 'bg_checker', 'admin'
            'mobile': mobile,
            'email': email,
            'created_at': datetime.utcnow(),
            'last_login': None,
            'status': 'active',
            'approval_status': approval_status,
            'unique_id': unique_id,  # Will be null initially, assigned after approval
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
    def check_password(credential_id, password):
        """
        Check if the provided password matches the stored password hash
        
        Args:
            credential_id: The credential document ID
            password: The password to check
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            credential = mongo.db.credentials.find_one({'_id': ObjectId(credential_id)})
            if credential and check_password_hash(credential['password_hash'], password):
                return True
            return False
        except Exception as e:
            print(f"Error checking password: {e}")
            return False
    
    @staticmethod
    def get_user_by_mobile(mobile):
        """
        Get user credentials by mobile number
        """
        return mongo.db.credentials.find_one({'mobile': mobile, 'status': 'active'})
    
    @staticmethod
    def verify_password(login_id, password):
        """
        Verify user password - can use unique_id or mobile number for login
        
        Args:
            login_id: Either unique_id or mobile number
            password: Plain text password
        """
        # Try to find user by unique_id first (for approved users)
        user = Auth.get_user_by_unique_id(login_id)
        
        # If not found, try by mobile number (for pending approval users)
        if not user:
            user = Auth.get_user_by_mobile(login_id)
            
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
        if not Auth.check_password(user_id, current_password):
            return False
        
        # Update password
        return Auth.update_password(user_id, new_password)
    
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
    def get_user_profile(user_data):
        """
        Get user profile based on user type
        """
        user_type = user_data['user_type']
        user_id = user_data['user_id']
        
        if user_type == 'migrant':
            return mongo.db.migrants.find_one({'_id': ObjectId(user_id)})
        elif user_type == 'employer':
            return mongo.db.employers.find_one({'_id': ObjectId(user_id)})
        elif user_type == 'ngo':
            return mongo.db.ngos.find_one({'_id': ObjectId(user_id)})
        elif user_type == 'bg_checker':
            return mongo.db.bg_checkers.find_one({'_id': ObjectId(user_id)})
        elif user_type == 'admin':
            return {'admin': True}  # Admin doesn't need a profile
        return None
        
    @staticmethod
    def assign_unique_id(user_id, user_type):
        """
        Assign a unique ID to a user after approval
        
        Args:
            user_id: MongoDB ObjectId of the credential document
            user_type: Type of user (migrant, employer, ngo, bg_checker)
            
        Returns:
            str: The newly assigned unique ID
        """
        # Generate prefix based on user type
        prefix_map = {
            'migrant': 'MIG',
            'employer': 'EMP',
            'ngo': 'NGO',
            'bg_checker': 'BGK'
        }
        prefix = prefix_map.get(user_type, 'USR')
        
        # Generate random 6-digit number
        random_digits = ''.join(random.choices(string.digits, k=6))
        unique_id = f"{prefix}{random_digits}"
        
        # Update user credentials with unique ID and set status to approved
        mongo.db.credentials.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'unique_id': unique_id,
                'approval_status': 'approved'
            }}
        )
        
        # Get user data to send SMS notification
        user_data = mongo.db.credentials.find_one({'_id': ObjectId(user_id)})
        if user_data and user_data.get('mobile'):
            # Get user profile to get name
            user_profile = None
            if user_type == 'migrant':
                user_profile = mongo.db.migrants.find_one({'_id': ObjectId(user_data['user_id'])})
            elif user_type == 'employer':
                user_profile = mongo.db.employers.find_one({'_id': ObjectId(user_data['user_id'])})
            elif user_type == 'ngo':
                user_profile = mongo.db.ngos.find_one({'_id': ObjectId(user_data['user_id'])})
                
            # Send SMS notification with unique ID
            from app.utils.sms import send_approval_notification_with_unique_id
            name = user_profile.get('name', 'User') if user_profile else 'User'
            send_approval_notification_with_unique_id(
                user_data['mobile'],
                user_type,
                name,
                unique_id
            )
        
        return unique_id
        
    @staticmethod
    def update_approval_status(user_id, status, reason=None):
        """
        Update approval status of a user
        
        Args:
            user_id: MongoDB ObjectId of the credential document
            status: New status (approved, rejected)
            reason: Reason for rejection (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_data = mongo.db.credentials.find_one({'_id': ObjectId(user_id)})
            if not user_data:
                return False
                
            update_data = {'approval_status': status}
            if reason:
                update_data['rejection_reason'] = reason
                
            # If approved, assign unique ID
            unique_id = None
            if status == 'approved':
                unique_id = Auth.assign_unique_id(user_id, user_data['user_type'])
                update_data['unique_id'] = unique_id
            elif status == 'rejected' and user_data.get('mobile'):
                # Send rejection SMS
                from app.utils.sms import send_rejection_notification
                send_rejection_notification(
                    user_data['mobile'],
                    user_data['user_type'],
                    reason
                )
            
            # Update status in database (if not already updated by assign_unique_id)
            if status != 'approved' or not unique_id:
                mongo.db.credentials.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': update_data}
                )
            
            return True
        except Exception as e:
            print(f"Error updating approval status: {str(e)}")
            return False
