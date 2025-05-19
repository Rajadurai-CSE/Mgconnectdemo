from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from app import mongo
from app.models.ngo import NGO
from bson.objectid import ObjectId
import json
from datetime import datetime

ngos = Blueprint('ngos', __name__)

@ngos.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        flash('Access denied. You must be an NGO to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Debug information
    print(f"Current user ID: {current_user.get_id()}")
    print(f"Current user role: {current_user.role}")
    
    ngo_profile = NGO.get_profile(current_user.get_id())
    if not ngo_profile:
        flash('NGO profile not found. Please contact administrator.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get services from the services collection for this NGO
    services = list(mongo.db.services.find({"ngo_id": ngo_profile['unique_id']}))
    
    # Group services by category
    housing_services = [s for s in services if s.get('category') == 'Housing']
    legal_services = [s for s in services if s.get('category') == 'Legal Aid']
    education_services = [s for s in services if s.get('category') == 'Education']
    healthcare_services = [s for s in services if s.get('category') == 'Healthcare']
    
    return render_template('ngos/dashboard.html', 
                           ngo=ngo_profile,
                           housing_services=housing_services,
                           legal_services=legal_services,
                           education_services=education_services,
                           healthcare_services=healthcare_services)

@ngos.route('/ngo/register', methods=['GET', 'POST'])
def ngo_register():
    if request.method == 'POST':
        # Process registration form
        user_id = current_user.get_id()
        ngo_info = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'address': request.form.get('address'),
            'city': request.form.get('city'),
            'state': request.form.get('state'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'website': request.form.get('website'),
            'services_offered': request.form.getlist('services_offered')
        }
        
        documents = {
            'registration_certificate': request.form.get('registration_certificate'),
            'tax_exemption': request.form.get('tax_exemption')
        }
        
        NGO.create_profile(user_id, ngo_info, documents)
        flash('NGO registration submitted successfully! It will be reviewed by the administrators.', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('ngos/register.html')

@ngos.route('/ngo/add-housing-service', methods=['GET', 'POST'])
@login_required
def add_housing_service():
    if current_user.role != 'ngo':
        flash('Access denied. You must be an NGO to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    ngo_profile = NGO.get_profile(current_user.get_id())
    if not ngo_profile or ngo_profile.get('status') != 'approved':
        flash('Your NGO profile is not approved yet. Please wait for approval.', 'warning')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    if request.method == 'POST':
        housing_details = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'address': request.form.get('address'),
            'capacity': request.form.get('capacity'),
            'eligibility': request.form.get('eligibility'),
            'cost': request.form.get('cost'),
            'facilities': request.form.getlist('facilities'),
            'contact_person': request.form.get('contact_person'),
            'contact_number': request.form.get('contact_number'),
            'contact_email': request.form.get('contact_email')
        }
        
        NGO.add_housing_service(str(ngo_profile.get('_id')), housing_details)
        flash('Housing service added successfully!', 'success')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    return render_template('ngos/add_housing_service.html')

@ngos.route('/ngo/add-legal-service', methods=['GET', 'POST'])
@login_required
def add_legal_service():
    if current_user.role != 'ngo':
        flash('Access denied. You must be an NGO to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    ngo_profile = NGO.get_profile(current_user.get_id())
    if not ngo_profile or ngo_profile.get('status') != 'approved':
        flash('Your NGO profile is not approved yet. Please wait for approval.', 'warning')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    if request.method == 'POST':
        legal_details = {
            'service_name': request.form.get('service_name'),
            'description': request.form.get('description'),
            'type_of_service': request.form.get('type_of_service'),
            'eligibility': request.form.get('eligibility'),
            'cost': request.form.get('cost'),
            'documents_required': request.form.getlist('documents_required'),
            'contact_person': request.form.get('contact_person'),
            'contact_number': request.form.get('contact_number'),
            'contact_email': request.form.get('contact_email'),
            'languages_supported': request.form.getlist('languages_supported')
        }
        
        NGO.add_legal_service(str(ngo_profile.get('_id')), legal_details)
        flash('Legal service added successfully!', 'success')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    return render_template('ngos/add_legal_service.html')

@ngos.route('/ngo/add-education-service', methods=['GET', 'POST'])
@login_required
def add_education_service():
    if current_user.role != 'ngo':
        flash('Access denied. You must be an NGO to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    ngo_profile = NGO.get_profile(current_user.get_id())
    if not ngo_profile or ngo_profile.get('status') != 'approved':
        flash('Your NGO profile is not approved yet. Please wait for approval.', 'warning')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    if request.method == 'POST':
        education_details = {
            'service_name': request.form.get('service_name'),
            'description': request.form.get('description'),
            'type_of_service': request.form.get('type_of_service'),
            'age_group': request.form.get('age_group'),
            'eligibility': request.form.get('eligibility'),
            'documents_required': request.form.getlist('documents_required'),
            'contact_person': request.form.get('contact_person'),
            'contact_number': request.form.get('contact_number'),
            'contact_email': request.form.get('contact_email'),
            'address': request.form.get('address')
        }
        
        NGO.add_education_service(str(ngo_profile.get('_id')), education_details)
        flash('Education service added successfully!', 'success')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    return render_template('ngos/add_education_service.html')

@ngos.route('/ngo/add-scholarship', methods=['GET', 'POST'])
@login_required
def add_scholarship():
    if current_user.role != 'ngo':
        flash('Access denied. You must be an NGO to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    ngo_profile = NGO.get_profile(current_user.get_id())
    if not ngo_profile or ngo_profile.get('status') != 'approved':
        flash('Your NGO profile is not approved yet. Please wait for approval.', 'warning')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    if request.method == 'POST':
        scholarship_details = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'education_level': request.form.get('education_level'),
            'eligibility': request.form.get('eligibility'),
            'amount': request.form.get('amount'),
            'duration': request.form.get('duration'),
            'application_process': request.form.get('application_process'),
            'documents_required': request.form.getlist('documents_required'),
            'deadline': request.form.get('deadline'),
            'contact_person': request.form.get('contact_person'),
            'contact_number': request.form.get('contact_number'),
            'contact_email': request.form.get('contact_email')
        }
        
        NGO.add_scholarship(str(ngo_profile.get('_id')), scholarship_details)
        flash('Scholarship added successfully!', 'success')
        return redirect(url_for('ngos.ngo_dashboard'))
    
    return render_template('ngos/add_scholarship.html')

@ngos.route('/ngo/service-stats/<service_type>/<service_id>')
@login_required
def service_stats(service_type, service_id):
    if current_user.role != 'ngo':
        flash('Access denied. You must be an NGO to view this page.', 'danger')
        return redirect(url_for('main.index'))
    
    ngo_profile = NGO.get_profile(current_user.get_id())
    if not ngo_profile:
        flash('NGO profile not found.', 'warning')
        return redirect(url_for('main.index'))
    
    # Fetch view statistics for the service
    # This would be implemented with a proper view tracking mechanism
    # For now, we'll simulate some data
    stats = {
        'views': 120,  # Example value
        'inquiries': 15,  # Example value
        'viewed_by_districts': {
            'Chennai': 40,
            'Coimbatore': 25,
            'Madurai': 20,
            'Others': 35
        }
    }
    
    return render_template('ngos/service_stats.html', 
                           service_type=service_type,
                           service_id=service_id,
                           stats=stats)
