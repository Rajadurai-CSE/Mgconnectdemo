import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# SMS API configuration
SMS_API_KEY = os.environ.get("SMS_API_KEY", "demo_key")
SMS_SENDER_ID = os.environ.get("SMS_SENDER_ID", "MGCTNN")
SMS_API_URL = os.environ.get("SMS_API_URL", "https://api.textlocal.in/send/")

# Setup logging
logger = logging.getLogger(__name__)

def send_sms(mobile_number, message):
    """
    Send SMS to the specified mobile number
    
    For development/demo, this function just logs the message
    In production, it would connect to an actual SMS gateway
    """
    if not mobile_number or not message:
        logger.error("Mobile number or message is empty")
        return False
        
    try:
        # In development mode, just log the message
        if os.environ.get("FLASK_ENV") == "development" or not SMS_API_KEY or SMS_API_KEY == "demo_key":
            logger.info(f"SMS to {mobile_number}: {message}")
            print(f"\n[SMS NOTIFICATION] To: {mobile_number}\nMessage: {message}\n")
            return True
            
        # In production, send actual SMS
        params = {
            'apikey': SMS_API_KEY,
            'numbers': mobile_number,
            'message': message,
            'sender': SMS_SENDER_ID
        }
        
        response = requests.post(SMS_API_URL, data=params)
        response_data = response.json()
        
        if response_data.get('status') == 'success':
            logger.info(f"SMS sent successfully to {mobile_number}")
            return True
        else:
            logger.error(f"Failed to send SMS: {response_data.get('errors')}")
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
