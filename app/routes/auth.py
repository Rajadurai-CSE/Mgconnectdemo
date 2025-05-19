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
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        # Validation
        if User.is_email_taken(email):
            flash('Email already registered', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('auth/register.html')
        
        # Create user
        hashed_password = generate_password_hash(password)
        user_data = {
            'email': email,
            'password': hashed_password,
            'role': role,
            'created_at': __import__('datetime').datetime.utcnow()
        }
        
        user_id = mongo.db.users.insert_one(user_data).inserted_id
        
        # Create role-specific profile
        if role == 'migrant':
            flash('Account created successfully! Please complete your profile', 'success')
            login_user(User(user_data))
            return redirect(url_for('migrants.setup_profile'))
        elif role == 'employer':
            flash('Account created successfully! Please complete your company profile', 'success')
            login_user(User(user_data))
            return redirect(url_for('employers.setup_profile'))
        else:
            flash('Account created successfully!', 'success')
            login_user(User(user_data))
            return redirect(url_for('main.index'))
    
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
            'unique_id': user_data.get('unique_id')  # Pass the unique_id from credentials
        }
        user = User(user_obj)
        login_user(user, remember=remember)
        
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
    
    # Check if verified mobile and OTP exist in session
    if 'verified_mobile' not in session or 'verified_otp' not in session:
        flash('Please verify your mobile number first.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    mobile = session['verified_mobile']
    otp = session['verified_otp']
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('Please enter both password fields.', 'danger')
            return render_template('auth/reset_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/reset_password.html')
        
        # Reset password
        if Auth.reset_password(mobile, otp, new_password):
            # Clear session variables
            session.pop('reset_mobile', None)
            session.pop('verified_mobile', None)
            session.pop('verified_otp', None)
            
            flash('Your password has been reset successfully. Please login with your new password.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Failed to reset password. Please try again.', 'danger')
            return render_template('auth/reset_password.html')
    
    return render_template('auth/reset_password.html')
