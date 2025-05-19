from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import mongo
from app.models.users import Migrant
from bson.objectid import ObjectId
import os
from datetime import datetime
from app.routes.main import get_employer_info

migrants = Blueprint('migrants', __name__)

# Register template utility functions
@migrants.app_template_global()
def get_employer_info_template(employer_id):
    return get_employer_info(employer_id)

@migrants.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get job opportunities (limit to 5 for dashboard)
    job_opportunities = list(mongo.db.jobs.find({'status': 'active'}).sort('created_at', -1).limit(5))
    
    # Get latest schemes and announcements
    latest_schemes = list(mongo.db.policies.find().sort('created_at', -1).limit(5))
    
    return render_template('migrants/dashboard.html', 
                           profile=migrant_profile, 
                           schemes=latest_schemes,
                           jobs=job_opportunities)

@migrants.route('/acts')
@login_required
def acts():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get acts and regulations
    acts_list = list(mongo.db.policies.find({'type': 'act'}).sort('created_at', -1))
    
    return render_template('migrants/acts.html', 
                           profile=migrant_profile, 
                           acts=acts_list)

@migrants.route('/jobs')
@login_required
def jobs():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get all job opportunities
    job_opportunities = list(mongo.db.jobs.find({'status': 'active'}).sort('created_at', -1))
    
    return render_template('migrants/jobs.html', 
                           profile=migrant_profile, 
                           jobs=job_opportunities)

@migrants.route('/services')
@login_required
def services():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get legal and housing services from NGOs
    legal_services = list(mongo.db.ngos.aggregate([
        {'$match': {'services.legal_aid': {'$exists': True, '$ne': []}}},
        {'$project': {
            'ngo_name': '$ngo_info.name',
            'services': '$services.legal_aid',
            'contact': '$contact_info'
        }}
    ]))
    
    housing_services = list(mongo.db.ngos.aggregate([
        {'$match': {'services.housing': {'$exists': True, '$ne': []}}},
        {'$project': {
            'ngo_name': '$ngo_info.name',
            'services': '$services.housing',
            'contact': '$contact_info'
        }}
    ]))
    
    return render_template('migrants/services.html', 
                           profile=migrant_profile, 
                           legal_services=legal_services,
                           housing_services=housing_services)

@migrants.route('/education')
@login_required
def education():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get education services and scholarships from NGOs
    education_services = list(mongo.db.ngos.aggregate([
        {'$match': {'services.education': {'$exists': True, '$ne': []}}},
        {'$project': {
            'ngo_name': '$ngo_info.name',
            'services': '$services.education',
            'contact': '$contact_info'
        }}
    ]))
    
    scholarships = list(mongo.db.ngos.aggregate([
        {'$match': {'services.scholarships': {'$exists': True, '$ne': []}}},
        {'$project': {
            'ngo_name': '$ngo_info.name',
            'services': '$services.scholarships',
            'contact': '$contact_info'
        }}
    ]))
    
    return render_template('migrants/education.html', 
                           profile=migrant_profile, 
                           education_services=education_services,
                           scholarships=scholarships)

@migrants.route('/emergency')
@login_required
def emergency():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get all emergency helplines
    helplines = list(mongo.db.helplines.find())
    
    # Get unique districts for filtering
    districts = mongo.db.helplines.distinct('district')
    
    # Filter by district if specified
    selected_district = request.args.get('district')
    if selected_district and selected_district != 'all':
        helplines = list(mongo.db.helplines.find({'district': selected_district}))
    
    # Get a list of all TN districts for police helplines
    all_districts = mongo.db.district_police.distinct('district')
    all_districts.sort()
    
    return render_template('migrants/emergency.html', 
                           profile=migrant_profile, 
                           helplines=helplines,
                           districts=districts,
                           all_districts=all_districts,
                           selected_district=selected_district)

@migrants.route('/district-police')
@login_required
def district_police():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    
    # Get all districts
    districts = list(mongo.db.district_police.distinct('district'))
    districts.sort()
    
    # Get district police info if specified
    selected_district = request.args.get('district')
    district_police_info = None
    
    if selected_district:
        district_police_info = mongo.db.district_police.find_one({'district': selected_district})
    
    return render_template('migrants/district_police.html', 
                           profile=migrant_profile, 
                           districts=districts,
                           district_police_info=district_police_info,
                           selected_district=selected_district)

@migrants.route('/setup-profile', methods=['GET', 'POST'])
@login_required
def setup_profile():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if profile already exists
    existing_profile = Migrant.get_profile(str(current_user._id))
    if existing_profile:
        return redirect(url_for('migrants.dashboard'))
    
    if request.method == 'POST':
        # Personal information
        personal_info = {
            'name': request.form.get('name'),
            'gender': request.form.get('gender'),
            'dob': request.form.get('dob'),
            'phone': request.form.get('phone'),
            'address': request.form.get('address'),
            'home_state': request.form.get('home_state'),
            'skills': request.form.get('skills').split(','),
            'languages': request.form.get('languages').split(','),
            'education': request.form.get('education')
        }
        
        # Handle document uploads
        documents = {}
        document_types = ['id_proof', 'address_proof', 'photo']
        
        for doc_type in document_types:
            if doc_type in request.files and request.files[doc_type].filename:
                file = request.files[doc_type]
                filename = secure_filename(file.filename)
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'migrant_docs', str(current_user._id))
                
                # Create directory if it doesn't exist
                os.makedirs(save_path, exist_ok=True)
                
                file_path = os.path.join(save_path, filename)
                file.save(file_path)
                
                documents[doc_type] = {
                    'filename': filename,
                    'path': file_path,
                    'uploaded_at': datetime.now()
                }
        
        # Create migrant profile
        migrant_data = {
            '_id': ObjectId(current_user._id),
            'personal_info': personal_info,
            'documents': documents,
            'status': 'pending',  # Initial status is pending for verification
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert profile into database
        mongo.db.migrants.insert_one(migrant_data)
        
        flash('Your profile has been submitted and is pending verification.', 'success')
        return redirect(url_for('migrants.dashboard'))
    
    return render_template('migrants/setup_profile.html')

@migrants.route('/view-scheme/<scheme_id>')
@login_required
def view_scheme(scheme_id):
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get scheme details
    scheme = mongo.db.policies.find_one({'_id': ObjectId(scheme_id)})
    if not scheme:
        flash('Scheme not found', 'warning')
        return redirect(url_for('migrants.dashboard'))
    
    return render_template('migrants/view_scheme.html', scheme=scheme)

@migrants.route('/view-job/<job_id>')
@login_required
def view_job(job_id):
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get job details
    job = mongo.db.jobs.find_one({'job_id': job_id})
    if not job:
        flash('Job not found', 'warning')
        return redirect(url_for('migrants.jobs'))
    
    # Get employer information
    employer = get_employer_info(job.get('employer_id'))
    
    # Check if migrant has already applied for this job
    application = mongo.db.job_applications.find_one({
        'migrant_id': str(current_user._id),
        'job_id': job_id
    })
    
    return render_template('migrants/view_job.html', 
                           job=job, 
                           employer=employer,
                           application=application)

@migrants.route('/create-support-request', methods=['GET', 'POST'])
@login_required
def create_support_request():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        request_data = {
            'migrant_id': str(current_user._id),
            'type': request.form.get('request_type'),
            'description': request.form.get('description'),
            'status': 'pending',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Insert request into database
        result = mongo.db.support_requests.insert_one(request_data)
        
        if result.inserted_id:
            flash('Your support request has been submitted. An NGO will contact you soon.', 'success')
            return redirect(url_for('migrants.dashboard'))
        else:
            flash('Failed to submit support request. Please try again.', 'danger')
    
    # Get available support types from NGOs
    support_types = mongo.db.ngos.distinct('services.type')
    
    return render_template('migrants/create_support_request.html', support_types=support_types)

@migrants.route('/view-support-request/<request_id>')
@login_required
def view_support_request(request_id):
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get request details
    support_request = mongo.db.support_requests.find_one({'_id': ObjectId(request_id), 'migrant_id': str(current_user._id)})
    if not support_request:
        flash('Support request not found', 'warning')
        return redirect(url_for('migrants.dashboard'))
    
    return render_template('migrants/view_support_request.html', support_request=support_request)

@migrants.route('/view-profile')
@login_required
def view_profile():
    if current_user.role != 'migrant':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant profile
    migrant_profile = Migrant.get_profile(str(current_user._id))
    if not migrant_profile:
        flash('Profile not found. Please set up your profile first.', 'warning')
        return redirect(url_for('migrants.setup_profile'))
    
    return render_template('migrants/view_profile.html', profile=migrant_profile)
