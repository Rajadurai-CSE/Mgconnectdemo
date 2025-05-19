from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import mongo
from bson.objectid import ObjectId
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get statistics for dashboard
    migrant_count = mongo.db.migrants.count_documents({})
    employer_count = mongo.db.employers.count_documents({})
    ngo_count = mongo.db.ngos.count_documents({})
    job_count = mongo.db.jobs.count_documents({})
    pending_approvals = mongo.db.migrants.count_documents({'status': 'pending'})
    
    # Get recent activities
    recent_migrants = list(mongo.db.migrants.find().sort('created_at', -1).limit(5))
    recent_jobs = list(mongo.db.jobs.find().sort('created_at', -1).limit(5))
    
    return render_template('admin/dashboard.html',
                          stats={
                              'migrants': migrant_count,
                              'employers': employer_count,
                              'ngos': ngo_count,
                              'jobs': job_count,
                              'pending_approvals': pending_approvals
                          },
                          recent_migrants=recent_migrants,
                          recent_jobs=recent_jobs)

@admin.route('/migrants')
@login_required
def manage_migrants():
    if current_user.role != 'admin':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all migrants
    migrants = list(mongo.db.migrants.find())
    
    return render_template('admin/migrants.html', migrants=migrants)

@admin.route('/employers')
@login_required
def manage_employers():
    if current_user.role != 'admin':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all employers
    employers = list(mongo.db.employers.find())
    
    return render_template('admin/employers.html', employers=employers)

@admin.route('/ngos')
@login_required
def manage_ngos():
    if current_user.role != 'admin':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all NGOs
    ngos = list(mongo.db.ngos.find())
    
    return render_template('admin/ngos.html', ngos=ngos)

@admin.route('/policies')
@login_required
def manage_policies():
    if current_user.role != 'admin':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all policies
    policies = list(mongo.db.policies.find())
    
    return render_template('admin/policies.html', policies=policies)

@admin.route('/verify-migrant/<migrant_id>', methods=['GET', 'POST'])
@login_required
def verify_migrant(migrant_id):
    if current_user.role != 'admin':
        flash('Access denied: You are not authorized to view this page', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant details
    migrant = mongo.db.migrants.find_one({'_id': ObjectId(migrant_id)})
    if not migrant:
        flash('Migrant not found', 'danger')
        return redirect(url_for('admin.manage_migrants'))
    
    if request.method == 'POST':
        status = request.form.get('status')
        rejection_reason = request.form.get('rejection_reason', '')
        
        update_data = {
            'status': status,
            'updated_at': datetime.now(),
            'verified_by': current_user.get_id(),
            'verified_at': datetime.now()
        }
        
        if status == 'rejected' and rejection_reason:
            update_data['rejection_reason'] = rejection_reason
        
        mongo.db.migrants.update_one(
            {'_id': ObjectId(migrant_id)},
            {'$set': update_data}
        )
        
        flash('Migrant verification status updated successfully', 'success')
        return redirect(url_for('admin.manage_migrants'))
    
    return render_template('admin/verify_migrant.html', migrant=migrant)
