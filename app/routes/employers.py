from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import mongo
from app.models.users import Employer, Migrant
from bson.objectid import ObjectId
from datetime import datetime

employers = Blueprint('employers', __name__)

@employers.route('/employers/dashboard')
@login_required
def dashboard():
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get employer profile
    employer_profile = Employer.get_profile(str(current_user._id))
    
    # Get posted jobs
    if employer_profile and 'jobs_posted' in employer_profile:
        jobs = list(mongo.db.jobs.find({'job_id': {'$in': employer_profile['jobs_posted']}}))
    else:
        jobs = []
    
    # Get employees if any
    employees = []
    if employer_profile and 'employees' in employer_profile:
        migrant_ids = [emp['migrant_id'] for emp in employer_profile['employees']]
        employees = list(mongo.db.migrants.find({'_id': {'$in': [ObjectId(mid) for mid in migrant_ids]}}))
    
    return render_template('employers/dashboard.html', 
                           profile=employer_profile,
                           jobs=jobs,
                           employees=employees)

@employers.route('/employers/setup-profile', methods=['GET', 'POST'])
@login_required
def setup_profile():
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Check if profile already exists
    existing_profile = Employer.get_profile(str(current_user._id))
    if existing_profile:
        return redirect(url_for('employers.dashboard'))
    
    if request.method == 'POST':
        company_info = {
            'name': request.form.get('company_name'),
            'industry': request.form.get('industry'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'contact_person': request.form.get('contact_person'),
            'contact_phone': request.form.get('contact_phone'),
            'company_size': request.form.get('company_size'),
            'description': request.form.get('description'),
            'registration_number': request.form.get('registration_number')
        }
        
        # Create employer profile
        Employer.create_profile(str(current_user._id), company_info)
        
        flash('Company profile created successfully!', 'success')
        return redirect(url_for('employers.dashboard'))
    
    return render_template('employers/setup_profile.html')

@employers.route('/employers/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get employer profile
    employer_profile = Employer.get_profile(str(current_user._id))
    if not employer_profile:
        flash('Please complete your company profile first', 'warning')
        return redirect(url_for('employers.setup_profile'))
    
    if request.method == 'POST':
        job_details = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'sector': request.form.get('sector'),
            'location': request.form.get('location'),
            'salary_range': request.form.get('salary_range'),
            'skills_required': request.form.get('skills_required').split(','),
            'experience_required': request.form.get('experience_required'),
            'education_required': request.form.get('education_required'),
            'number_of_positions': int(request.form.get('number_of_positions', 1)),
            'benefits': request.form.get('benefits'),
            'job_type': request.form.get('job_type'),  # Full-time, Part-time, Contract
            'company_name': employer_profile['company_info']['name']
        }
        
        # Post job
        job_id = Employer.post_job(str(employer_profile['_id']), job_details)
        
        flash('Job posted successfully!', 'success')
        return redirect(url_for('employers.view_jobs'))
    
    return render_template('employers/post_job.html')

@employers.route('/employers/view-jobs')
@login_required
def view_jobs():
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get employer profile
    employer_profile = Employer.get_profile(str(current_user._id))
    
    # Get jobs
    if employer_profile and 'jobs_posted' in employer_profile:
        jobs = list(mongo.db.jobs.find({'job_id': {'$in': employer_profile['jobs_posted']}}))
    else:
        jobs = []
    
    return render_template('employers/view_jobs.html', jobs=jobs)

@employers.route('/employers/view-job/<job_id>')
@login_required
def view_job(job_id):
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    job = mongo.db.jobs.find_one({'job_id': job_id})
    
    if not job:
        flash('Job not found', 'warning')
        return redirect(url_for('employers.view_jobs'))
    
    # Get employees for this job
    employees = []
    if 'employees' in job:
        migrant_ids = [emp['migrant_id'] for emp in job['employees']]
        employees = list(mongo.db.migrants.find({'_id': {'$in': [ObjectId(mid) for mid in migrant_ids]}}))
    
    return render_template('employers/view_job.html', job=job, employees=employees)

@employers.route('/employers/add-migrant', methods=['GET', 'POST'])
@login_required
def add_migrant():
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get employer profile
    employer_profile = Employer.get_profile(str(current_user._id))
    if not employer_profile:
        flash('Please complete your company profile first', 'warning')
        return redirect(url_for('employers.setup_profile'))
    
    # Get jobs for dropdown
    if 'jobs_posted' in employer_profile:
        jobs = list(mongo.db.jobs.find({'job_id': {'$in': employer_profile['jobs_posted']}}))
    else:
        jobs = []
        
    if len(jobs) == 0:
        flash('Please post a job first', 'warning')
        return redirect(url_for('employers.post_job'))
    
    if request.method == 'POST':
        migrant_id = request.form.get('migrant_id')
        job_id = request.form.get('job_id')
        
        # Verify migrant exists and is approved
        migrant = mongo.db.migrants.find_one({
            'migrant_id': migrant_id,
            'status': 'approved'
        })
        
        if not migrant:
            flash('Migrant not found or not approved', 'danger')
            return render_template('employers/add_migrant.html', jobs=jobs)
        
        # Get job details
        job = mongo.db.jobs.find_one({'job_id': job_id})
        
        if not job:
            flash('Job not found', 'danger')
            return render_template('employers/add_migrant.html', jobs=jobs)
        
        # Add migrant to job
        job_details = {
            'job_id': job_id,
            'title': job['details']['title'],
            'sector': job['details']['sector'],
            'salary_range': job['details']['salary_range']
        }
        
        # Add migrant to employer's records
        Employer.add_migrant(str(employer_profile['_id']), str(migrant['_id']), job_details)
        
        # Add migrant to job's employee list
        mongo.db.jobs.update_one(
            {'job_id': job_id},
            {'$push': {'employees': {
                'migrant_id': str(migrant['_id']),
                'start_date': datetime.utcnow(),
                'status': 'active'
            }}}
        )
        
        flash('Migrant added successfully!', 'success')
        return redirect(url_for('employers.dashboard'))
    
    return render_template('employers/add_migrant.html', jobs=jobs)

@employers.route('/employers/view-employees')
@login_required
def view_employees():
    if current_user.role != 'employer':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get employer profile
    employer_profile = Employer.get_profile(str(current_user._id))
    
    # Get employees
    employees = []
    if employer_profile and 'employees' in employer_profile:
        employee_records = employer_profile['employees']
        
        for record in employee_records:
            migrant = mongo.db.migrants.find_one({'_id': ObjectId(record['migrant_id'])})
            if migrant:
                migrant['job_details'] = record['job_details']
                migrant['start_date'] = record['start_date']
                migrant['status'] = record['status']
                employees.append(migrant)
    
    return render_template('employers/view_employees.html', employees=employees)
