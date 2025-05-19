import requests
import os
from dotenv import load_dotenv
import logging
from flask import current_app

# Load environment variables
load_dotenv()

# TextLink SMS API configuration
TEXT_LINK_API_KEY = os.environ.get("text_link_sms_api_key")
TEXT_LINK_API_URL = "https://api.textlinksms.com/sms"

# Setup logging
logger = logging.getLogger(__name__)

def send_sms(mobile_number, message):
    """
    Send SMS to the specified mobile number using TextLink SMS API
    
    Args:
        mobile_number (str): Recipient phone number with country prefix (e.g., +911234567890)
        message (str): Message body
        
    Returns:
        bool: True if SMS was sent successfully, False otherwise
    """
    if not mobile_number or not message:
        logger.error("Mobile number or message is empty")
        return False
    
    # Ensure mobile number has country code prefix
    if not mobile_number.startswith("+"):
        mobile_number = "+91" + mobile_number  # Default to India country code if not provided
        
    try:
        # In development mode, just log the message
        if os.environ.get("FLASK_ENV") == "development" or not TEXT_LINK_API_KEY:
            logger.info(f"SMS to {mobile_number}: {message}")
            print(f"\n[SMS NOTIFICATION] To: {mobile_number}\nMessage: {message}\n")
            return True
            
        # In production, send actual SMS using TextLink API
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": TEXT_LINK_API_KEY
        }
        
        payload = {
            "phone_number": mobile_number,
            "text": message
        }
        
        response = requests.post(TEXT_LINK_API_URL, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            logger.info(f"SMS sent successfully to {mobile_number}")
            return True
        else:
            logger.error(f"Failed to send SMS: {response_data}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return False

def send_approval_notification(mobile_number, applicant_type, name, id_number):
    """
    Send approval notification to migrant or employer
    """
    if applicant_type == "migrant":
        message = f"Congratulations! Your migrant registration has been approved. Your Migrant ID is {id_number}. You can now access MigrantConnectTN services."
    elif applicant_type == "employer":
        message = f"Congratulations! {name}'s registration has been approved. The Company ID is {id_number}. You can now post jobs and manage migrant workers on MigrantConnectTN."
    else:
        return False
        
    return send_sms(mobile_number, message)

def send_approval_notification_with_unique_id(mobile_number, applicant_type, name, unique_id, default_password='default123'):
    """
    Send approval notification with unique ID and default password
    
    Args:
        mobile_number: Recipient's mobile number
        applicant_type: Type of user (migrant, employer, ngo, bg_checker)
        name: Name of the user
        unique_id: Assigned unique ID
        default_password: Default password assigned to the user
    """
    if applicant_type == "migrant":
        message = f"Congratulations {name}! Your migrant registration has been approved. Your Unique ID: {unique_id} and Password: {default_password}. Please login and change your password immediately."
    elif applicant_type == "employer":
        message = f"Congratulations {name}! Your employer registration has been approved. Your Unique ID: {unique_id} and Password: {default_password}. Please login and change your password immediately."
    elif applicant_type == "ngo":
        message = f"Congratulations {name}! Your NGO registration has been approved. Your Unique ID: {unique_id} and Password: {default_password}. Please login and change your password immediately."
    elif applicant_type == "bg_checker":
        message = f"Congratulations {name}! Your Background Checker registration has been approved. Your Unique ID: {unique_id} and Password: {default_password}. Please login and change your password immediately."
    else:
        return False
        
    return send_sms(mobile_number, message)

def send_verification_notification(mobile_number, otp):
    """
    Send OTP verification code via SMS
    """
    message = f"Your MigrantConnectTN verification code is {otp}. This code is valid for 10 minutes."
    return send_sms(mobile_number, message)

def send_rejection_notification(mobile_number, applicant_type, reason=None):
    """
    Send rejection notification
    """
    reason_text = f" Reason: {reason}" if reason else ""
    
    if applicant_type == "migrant":
        message = f"Your migrant registration application has been rejected.{reason_text} Please contact our support center for assistance."
    elif applicant_type == "employer":
        message = f"Your company registration application has been rejected.{reason_text} Please contact our support center for assistance."
    else:
        return False
        
    return send_sms(mobile_number, message)
