from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from app import mongo
from app.models.government import Government
from werkzeug.security import generate_password_hash
from datetime import datetime
from bson.objectid import ObjectId
import json

government = Blueprint('government', __name__)

@government.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    stats = Government.get_migration_stats()
    
    # Format stats for charts
    sector_labels = [stat['_id'] if stat['_id'] else 'Unknown' for stat in stats['sector_stats']]
    sector_values = [stat['count'] for stat in stats['sector_stats']]
    
    state_labels = [stat['_id'] if stat['_id'] else 'Unknown' for stat in stats['state_stats']]
    state_values = [stat['count'] for stat in stats['state_stats']]
    
    months = [f"{stat['_id']['month']}/{stat['_id']['year']}" for stat in stats['monthly_stats']]
    monthly_values = [stat['count'] for stat in stats['monthly_stats']]
    
    return render_template('government/admin_dashboard.html', 
                           stats=stats,
                           sector_labels=json.dumps(sector_labels),
                           sector_values=json.dumps(sector_values),
                           state_labels=json.dumps(state_labels),
                           state_values=json.dumps(state_values),
                           months=json.dumps(months),
                           monthly_values=json.dumps(monthly_values),
                           current_time=datetime.utcnow())

@government.route('/admin/bg-checkers')
@login_required
def manage_bg_checkers():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    bg_checkers = Government.get_all_bg_checkers()
    return render_template('government/bg_checkers.html', bg_checkers=bg_checkers)

@government.route('/admin/add-bg-checker', methods=['GET', 'POST'])
@login_required
def add_bg_checker():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        area_assigned = request.form.get('area_assigned')
        
        # Check if email is already taken
        if mongo.db.credentials.find_one({'email': email}):
            flash('Email already in use. Please choose another.', 'danger')
            return redirect(url_for('government.add_bg_checker'))
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        Government.create_bg_checker(name, email, password_hash, phone, area_assigned)
        flash('Background checker account created successfully!', 'success')
        return redirect(url_for('government.manage_bg_checkers'))
    
    return render_template('government/add_bg_checker.html')

@government.route('/admin/policies')
@login_required
def manage_policies():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    policies = Government.get_all_policies()
    return render_template('government/policies.html', policies=policies)

@government.route('/admin/add-policy', methods=['GET', 'POST'])
@login_required
def add_policy():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        sector = request.form.get('sector') or None
        document_url = request.form.get('document_url') or None
        published_date = datetime.strptime(request.form.get('published_date'), '%Y-%m-%d') if request.form.get('published_date') else None
        
        Government.add_policy(title, description, sector, document_url, published_date)
        flash('Policy added successfully!', 'success')
        return redirect(url_for('government.manage_policies'))
    
    return render_template('government/add_policy.html')

@government.route('/admin/helplines')
@login_required
def manage_helplines():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    helplines = Government.get_all_helplines()
    return render_template('government/helplines.html', helplines=helplines)

@government.route('/admin/add-helpline', methods=['GET', 'POST'])
@login_required
def add_helpline():
    if current_user.role != 'admin':
        flash('Access denied. You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        district = request.form.get('district')
        police_helpline = request.form.get('police_helpline')
        labor_helpline = request.form.get('labor_helpline')
        women_helpline = request.form.get('women_helpline')
        child_helpline = request.form.get('child_helpline')
        
        Government.add_emergency_helpline(district, police_helpline, labor_helpline, women_helpline, child_helpline)
        flash('Helpline information added successfully!', 'success')
        return redirect(url_for('government.manage_helplines'))
    
    return render_template('government/add_helpline.html')

@government.route('/bg-checker/dashboard')
@login_required
def bg_checker_dashboard():
    """
    Background checker dashboard with city-based filtering
    """
    if current_user.role != 'bg_checker':
        flash('Access denied. You must be a background checker to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get the user's unique_id from the current_user object
    unique_id = current_user.get_id()
    
    # Find the background checker by their unique_id
    bg_checker = mongo.db.bg_checkers.find_one({'unique_id': unique_id})
        
    if not bg_checker:
        flash('Error: Could not find your profile. Please contact administrator.', 'danger')
        return redirect(url_for('main.index'))
        
    area_assigned = bg_checker.get('area_assigned', 'All Areas')
    
    # Get city filter from request if provided
    city_filter = request.args.get('city_filter', '')
    
    # Get pending verifications for this area, filtered by city if specified
    pending_verifications = Government.get_pending_verifications(area_assigned, city_filter)
    
    # Get all available cities for the filter dropdown
    available_cities = Government.get_available_cities()
    
    return render_template('government/bg_checker_dashboard.html', 
                           pending_verifications=pending_verifications,
                           area_assigned=area_assigned,
                           bg_checker=bg_checker,
                           city_filter=city_filter,
                           available_cities=available_cities)

@government.route('/bg-checker/verify/<migrant_id>', methods=['GET', 'POST'])
@login_required
def verify_migrant(migrant_id):
    if current_user.role != 'bg_checker':
        flash('Access denied. You must be a background checker to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get migrant details
    migrant = mongo.db.migrants.find_one({'_id': ObjectId(migrant_id)})
    if not migrant:
        flash('Migrant not found.', 'danger')
        return redirect(url_for('government.bg_checker_dashboard'))
    
    if request.method == 'POST':
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        if status not in ['approved', 'rejected']:
            flash('Invalid status.', 'danger')
            return redirect(url_for('government.verify_migrant', migrant_id=migrant_id))
        
        success = Government.process_verification(
            migrant_id,
            status,
            notes,
            verified_by=current_user.get_id()
        )
        
        if success:
            flash(f'Migrant {status} successfully!', 'success')
        else:
            flash('Error processing verification.', 'danger')
        
        return redirect(url_for('government.bg_checker_dashboard'))
    
    return render_template('government/verify_migrant.html', migrant=migrant)

@government.route('/helplines')
def public_helplines():
    helplines = Government.get_all_helplines()
    return render_template('government/public_helplines.html', helplines=helplines)

@government.route('/policies')
def public_policies():
    sector = request.args.get('sector')
    policies = Government.get_all_policies(sector)
    return render_template('government/public_policies.html', policies=policies)
