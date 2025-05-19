from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import mongo
from app.models.users import User
from app.models.auth import Auth
from app.models.migrant import Migrant
from app.models.employer import Employer
from bson.objectid import ObjectId
from datetime import datetime

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user with pending approval status
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        role = request.form.get('role')
        password = request.form.get('password', 'default123')  # Default password
        
        # Validation
        if not name or not mobile or not role:
            flash('Please fill in all required fields', 'danger')
            return render_template('auth/register.html')
        
        # Check if mobile already registered
        existing_user = Auth.get_user_by_mobile(mobile)
        if existing_user:
            flash('Mobile number already registered', 'danger')
            return render_template('auth/register.html')
        
        # For non-migrant roles, email is required
        if role != 'migrant' and not email:
            flash('Email is required for ' + role + ' registration', 'danger')
            return render_template('auth/register.html')
        
        # Create user profile based on role
        user_profile = {}
        
        if role == 'migrant':
            # Get migrant-specific fields
            dob = request.form.get('dob')
            aadhar = request.form.get('aadhar')
            current_address = request.form.get('current_address')
            current_city = request.form.get('current_city')
            native_state = request.form.get('native_state')
            native_address = request.form.get('native_address')
            job_info_source = request.form.get('job_info_source')
            contact_name = request.form.get('contact_name')
            contact_number = request.form.get('contact_number')
            contractor_name = request.form.get('contractor_name')
            contractor_number = request.form.get('contractor_number')
            company_name = request.form.get('company_name')
            company_type = request.form.get('company_type')
            company_sector = request.form.get('company_sector')
            
            # Create migrant profile
            user_profile = {
                'name': name,
                'dob': dob,
                'aadhar': aadhar,
                'current_address': current_address,
                'current_city': current_city,
                'native_state': native_state,
                'native_address': native_address,
                'job_info_source': job_info_source,
                'contact_name': contact_name if job_info_source in ['friends', 'agency'] else None,
                'contact_number': contact_number if job_info_source in ['friends', 'agency'] else None,
                'contractor_name': contractor_name,
                'contractor_number': contractor_number,
                'company_name': company_name,
                'company_type': company_type,
                'company_sector': company_sector,
                'registration_date': datetime.utcnow(),
                'status': 'pending'
            }
            
            # Insert migrant profile
            user_id = mongo.db.migrants.insert_one(user_profile).inserted_id
            
        elif role == 'employer':
            # Create basic employer profile
            user_profile = {
                'name': name,
                'company_name': name,  # Use name as company name initially
                'registration_date': datetime.utcnow(),
                'status': 'pending'
            }
            
            # Insert employer profile
            user_id = mongo.db.employers.insert_one(user_profile).inserted_id
            
        elif role == 'ngo':
            # Create basic NGO profile
            user_profile = {
                'name': name,
                'organization_name': name,  # Use name as organization name initially
                'registration_date': datetime.utcnow(),
                'status': 'pending'
            }
            
            # Insert NGO profile
            user_id = mongo.db.ngos.insert_one(user_profile).inserted_id
            
        elif role == 'bg_checker':
            # Create basic background checker profile
            user_profile = {
                'name': name,
                'department': 'Verification Department',  # Default department
                'registration_date': datetime.utcnow(),
                'status': 'pending'
            }
            
            # Insert background checker profile
            user_id = mongo.db.bg_checkers.insert_one(user_profile).inserted_id
        
        # Create credentials with pending approval status
        Auth.create_credentials(
            user_id=user_id,
            password=password,
            user_type=role,
            mobile=mobile,
            email=email,
            unique_id=None,  # Will be assigned after approval
            approval_status='pending'
        )
        
        flash('Your registration has been submitted successfully! You will receive your unique ID and password via SMS after approval.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        unique_id = request.form.get('unique_id')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        print(f"Login attempt with unique_id: {unique_id}")
        
        # Verify credentials using Auth model
        user_data = Auth.verify_password(unique_id, password)
        
        if not user_data:
            flash('Please check your login details and try again.', 'danger')
            return render_template('auth/login.html')
        
        # Get user profile based on user type
        user_profile = Auth.get_user_profile(user_data)
        if not user_profile:
            flash('User profile not found. Please contact administrator.', 'danger')
            return render_template('auth/login.html')
        
        # Create User object and login
        user_obj = {
            '_id': user_data['_id'],
            'email': user_data.get('email'),
            'role': user_data['user_type'],
            'user_data': user_profile,
            'unique_id': user_data.get('unique_id'),  # Pass the unique_id from credentials
            'credential_id': str(user_data['_id'])  # Store credential ID for password changes
        }
        user = User(user_obj)
        login_user(user, remember=remember)
        
        # Check if user is using default password (default123)
        if check_password_hash(user_data['password_hash'], 'default123'):
            # Redirect to change password page
            flash('You are using a default password. Please change it for security reasons.', 'warning')
            return redirect(url_for('auth.change_default_password'))
        
        # Redirect based on role
        if user.role == 'migrant':
            return redirect(url_for('migrants.dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('government.admin_dashboard'))
        elif user.role == 'bg_checker':
            return redirect(url_for('government.bg_checker_dashboard'))
        elif user.role == 'employer':
            return redirect(url_for('employers.dashboard'))
        elif user.role == 'ngo':
            return redirect(url_for('ngos.ngo_dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        mobile = request.form.get('mobile')
        
        if not mobile:
            flash('Please enter your mobile number.', 'danger')
            return render_template('auth/forgot_password.html')
        
        # Generate OTP and send SMS
        otp_data = Auth.generate_otp(mobile)
        
        if not otp_data:
            flash('Mobile number not found in our records.', 'danger')
            return render_template('auth/forgot_password.html')
        
        # TODO: Integrate with SMS gateway to send OTP
        # For now, we'll just print it for development purposes
        print(f"OTP sent to {mobile}: {otp_data['otp']}")
        
        # Store mobile in session for verification page
        session['reset_mobile'] = mobile
        
        flash('An OTP has been sent to your mobile number.', 'success')
        return redirect(url_for('auth.verify_otp'))
    
    return render_template('auth/forgot_password.html')

@auth.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if mobile exists in session
    if 'reset_mobile' not in session:
        flash('Please enter your mobile number first.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    mobile = session['reset_mobile']
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        
        if not otp:
            flash('Please enter the OTP sent to your mobile.', 'danger')
            return render_template('auth/verify_otp.html', mobile=mobile)
        
        # Verify OTP
        if Auth.verify_otp(mobile, otp):
            session['verified_mobile'] = mobile
            session['verified_otp'] = otp
            return redirect(url_for('auth.reset_password'))
        else:
            flash('Invalid or expired OTP. Please try again.', 'danger')
            return render_template('auth/verify_otp.html', mobile=mobile)
    
    return render_template('auth/verify_otp.html', mobile=mobile)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    token = request.args.get('token', '')
    
    if not token:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Verify token
    user_data = Auth.verify_reset_token(token)
    if not user_data:
        flash('Invalid or expired password reset link.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # Update password
        if Auth.update_password(user_data['_id'], password):
            flash('Your password has been updated. You can now login with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('An error occurred. Please try again.', 'danger')
            return render_template('auth/reset_password.html', token=token)
    
    return render_template('auth/reset_password.html', token=token)

@auth.route('/change-default-password', methods=['GET', 'POST'])
@login_required
def change_default_password():
    """
    Change default password after first login
    """
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('auth/change_default_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'danger')
            return render_template('auth/change_default_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/change_default_password.html')
        
        # Check if current password is correct
        credential_id = current_user.credential_id
        if not Auth.check_password(credential_id, current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_default_password.html')
        
        # Update password
        if Auth.update_password(credential_id, new_password):
            flash('Your password has been updated successfully.', 'success')
            
            # Redirect based on role
            if current_user.role == 'migrant':
                return redirect(url_for('migrants.dashboard'))
            elif current_user.role == 'admin':
                return redirect(url_for('government.admin_dashboard'))
            elif current_user.role == 'bg_checker':
                return redirect(url_for('government.bg_checker_dashboard'))
            elif current_user.role == 'employer':
                return redirect(url_for('employers.dashboard'))
            elif current_user.role == 'ngo':
                return redirect(url_for('ngos.ngo_dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('An error occurred. Please try again.', 'danger')
            return render_template('auth/change_default_password.html')
    
    return render_template('auth/change_default_password.html')
