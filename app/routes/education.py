from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, jsonify
from flask_login import login_required, current_user
from app import mongo
from app.models.education import ChildEducation
from app.models.auth import Auth
from bson.objectid import ObjectId
import json
from datetime import datetime

education = Blueprint('education', __name__)

@education.route('/child-education')
def child_education_services():
    """
    Public page showing all child education services and scholarships
    """
    # Get all enrollment services
    enrollment_services = ChildEducation.get_all_enrollment_services()
    
    # Get all scholarships
    scholarships = ChildEducation.get_all_scholarships()
    
    return render_template('education/services.html', 
                           enrollment_services=enrollment_services,
                           scholarships=scholarships)

@education.route('/child-education/enrollment')
def enrollment_services():
    """
    Page showing only enrollment services
    """
    # Get enrollment services
    ngo_services = ChildEducation.get_all_enrollment_services('ngo')
    govt_services = ChildEducation.get_all_enrollment_services('government')
    
    return render_template('education/enrollment.html',
                           ngo_services=ngo_services,
                           govt_services=govt_services)

@education.route('/child-education/scholarships')
def scholarship_services():
    """
    Page showing only scholarships
    """
    # Get scholarships filtered by education level
    education_level = request.args.get('level')
    
    # Get scholarship services
    if education_level:
        scholarships = ChildEducation.get_all_scholarships(education_level)
    else:
        scholarships = ChildEducation.get_all_scholarships()
    
    return render_template('education/scholarships.html', 
                           scholarships=scholarships,
                           selected_level=education_level)

@education.route('/child-education/enrollment/apply/<service_id>', methods=['GET', 'POST'])
@login_required
def apply_enrollment(service_id):
    """
    Apply for enrollment service
    """
    # Get the service details
    service = mongo.db.enrollment_services.find_one({"_id": ObjectId(service_id)})
    
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('education.enrollment_services'))
    
    if request.method == 'POST':
        # Check if current user is a migrant
        if current_user.role != 'migrant':
            flash('Only migrant workers can apply for child education services.', 'danger')
            return redirect(url_for('education.enrollment_services'))
        
        # Get form data
        child_name = request.form.get('child_name')
        child_age = request.form.get('child_age')
        child_gender = request.form.get('child_gender')
        previous_education = request.form.get('previous_education')
        additional_info = request.form.get('additional_info')
        
        # TODO: Handle document uploads
        documents = {}
        
        # Apply for enrollment
        ChildEducation.apply_for_enrollment(
            migrant_id=current_user.get_id(),
            service_id=service_id,
            child_name=child_name,
            child_age=child_age,
            child_gender=child_gender,
            previous_education=previous_education,
            documents=documents,
            additional_info=additional_info
        )
        
        flash('Your enrollment application has been submitted successfully!', 'success')
        return redirect(url_for('education.my_applications'))
    
    return render_template('education/apply_enrollment.html', service=service)

@education.route('/child-education/scholarship/apply/<scholarship_id>', methods=['GET', 'POST'])
@login_required
def apply_scholarship(scholarship_id):
    """
    Apply for scholarship
    """
    # Get the scholarship details
    scholarship = mongo.db.scholarships.find_one({"_id": ObjectId(scholarship_id)})
    
    if not scholarship:
        flash('Scholarship not found.', 'danger')
        return redirect(url_for('education.scholarship_services'))
    
    if request.method == 'POST':
        # Check if current user is a migrant
        if current_user.role != 'migrant':
            flash('Only migrant workers can apply for scholarships.', 'danger')
            return redirect(url_for('education.scholarship_services'))
        
        # Get form data
        child_name = request.form.get('child_name')
        child_age = request.form.get('child_age')
        current_education = request.form.get('current_education')
        additional_info = request.form.get('additional_info')
        
        # TODO: Handle document uploads
        documents = {}
        
        # Apply for scholarship
        ChildEducation.apply_for_scholarship(
            migrant_id=current_user.get_id(),
            scholarship_id=scholarship_id,
            child_name=child_name,
            child_age=child_age,
            current_education=current_education,
            documents=documents,
            additional_info=additional_info
        )
        
        flash('Your scholarship application has been submitted successfully!', 'success')
        return redirect(url_for('education.my_applications'))
    
    return render_template('education/apply_scholarship.html', scholarship=scholarship)

@education.route('/child-education/my-applications')
@login_required
def my_applications():
    """
    View all applications by the current migrant
    """
    # Check if current user is a migrant
    if current_user.role != 'migrant':
        flash('Only migrant workers can view their applications.', 'danger')
        return redirect(url_for('main.index'))
    
    # Get all applications by the migrant
    applications = ChildEducation.get_migrant_applications(current_user.get_id())
    
    # Get service and scholarship details for each application
    for app in applications['enrollment']:
        service_id = app.get('service_id')
        if service_id:
            app['service'] = mongo.db.enrollment_services.find_one({"_id": ObjectId(service_id)})
    
    for app in applications['scholarships']:
        scholarship_id = app.get('scholarship_id')
        if scholarship_id:
            app['scholarship'] = mongo.db.scholarships.find_one({"_id": ObjectId(scholarship_id)})
    
    return render_template('education/my_applications.html', applications=applications)
