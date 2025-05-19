from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import current_user
from app import mongo
from bson.objectid import ObjectId

main = Blueprint('main', __name__)

# Function to get employer info for templates
def get_employer_info(employer_id):
    """Get employer info from employer_id for job listings"""
    if not employer_id:
        return None
    
    try:
        # First try to look up by ObjectId
        if ObjectId.is_valid(employer_id):
            employer = mongo.db.employers.find_one({"_id": ObjectId(employer_id)})
            if employer:
                return employer
        
        # If not found, try to look up by employer_id string
        employer = mongo.db.employers.find_one({"employer_id": employer_id})
        return employer
    except Exception as e:
        print(f"Error fetching employer info: {e}")
        return None

# Register template utility functions
@main.app_template_global()
def get_employer_info_template(employer_id):
    return get_employer_info(employer_id)

@main.route('/')
@main.route('/home')
def index():
    # Get latest schemes/policies for homepage
    latest_schemes = list(mongo.db.policies.find().sort('created_at', -1).limit(3))
    
    # Get latest job opportunities 
    latest_jobs = list(mongo.db.jobs.find({'status': 'active'}).sort('created_at', -1).limit(4))
    
    # Get some statistics for homepage
    migrant_count = mongo.db.migrants.count_documents({'status': 'approved'})
    employer_count = mongo.db.employers.count_documents({})
    job_count = mongo.db.jobs.count_documents({'status': 'active'})
    
    return render_template('main/index.html', 
                           latest_schemes=latest_schemes,
                           latest_jobs=latest_jobs,
                           stats={
                               'migrants': migrant_count,
                               'employers': employer_count,
                               'jobs': job_count
                           })

@main.route('/about')
def about():
    return render_template('main/about.html')

@main.route('/contact')
def contact():
    return render_template('main/contact.html')

@main.route('/schemes')
def schemes():
    # Get all public schemes/policies
    schemes = list(mongo.db.policies.find().sort('created_at', -1))
    
    return render_template('main/schemes.html', schemes=schemes)

@main.route('/scheme/<scheme_id>')
def view_scheme(scheme_id):
    scheme = mongo.db.policies.find_one({'_id': scheme_id})
    
    if not scheme:
        flash('Scheme not found', 'warning')
        return redirect(url_for('main.schemes'))
    
    return render_template('main/view_scheme.html', scheme=scheme)

@main.route('/jobs')
def jobs():
    # Get all active job postings
    jobs = list(mongo.db.jobs.find({'status': 'active'}).sort('created_at', -1))
    
    # Get sectors for filtering
    sectors = mongo.db.jobs.distinct('details.sector')
    
    return render_template('main/jobs.html', jobs=jobs, sectors=sectors)

@main.route('/filter-jobs')
def filter_jobs():
    sector = request.args.get('sector')
    location = request.args.get('location')
    
    # Build filter query

@main.route('/job/<job_id>')
def view_job(job_id):
    """View details of a specific job posting"""
    # Get the job details
    job = mongo.db.jobs.find_one({"job_id": job_id})
    
    if not job:
        # Try finding by ObjectId
        if ObjectId.is_valid(job_id):
            job = mongo.db.jobs.find_one({"_id": ObjectId(job_id)})
        
        if not job:
            flash("Job not found", "danger")
            return redirect(url_for('main.jobs'))
    
    # Get employer details
    employer = None
    if job.get('employer_id'):
        employer = get_employer_info(job['employer_id'])
    
    # Increment view counter
    mongo.db.jobs.update_one(
        {"_id": job["_id"]},
        {"$inc": {"views": 1}}
    )
    
    # Get similar jobs
    similar_jobs = list(mongo.db.jobs.find({
        "_id": {"$ne": job["_id"]},  # Not the current job
        "status": "active",
        "$or": [
            {"location": job.get("location")},
            {"job_type": job.get("job_type")}
        ]
    }).limit(3))
    
    return render_template('main/view_job.html', job=job, employer=employer, similar_jobs=similar_jobs)
    query = {'status': 'active'}
    
    if sector and sector != 'all':
        query['details.sector'] = sector
    
    if location and location != 'all':
        query['details.location'] = location
    
    # Get filtered jobs
    jobs = list(mongo.db.jobs.find(query).sort('created_at', -1))
    
    return jsonify({
        'jobs': jobs
    })

@main.route('/faqs')
def faqs():
    return render_template('main/faqs.html')

@main.route('/languages')
def languages():
    language = request.args.get('lang', 'en')
    # Logic to set language preference would go here
    return redirect(request.referrer or url_for('main.index'))
