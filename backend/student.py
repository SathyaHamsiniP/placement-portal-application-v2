from flask import Blueprint, jsonify, request, send_file
from .database import db
from .models import User, Company, Student, JobPosition, Application, Notification
from .auth import token_required
from datetime import datetime
import os

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard', methods=['GET'])
@token_required
def get_student_dashboard(current_user):
    if current_user.role != 'Student':
        return jsonify({'message': 'Unauthorized'}), 403
    
    student = current_user.student_profile
    apps = Application.query.filter_by(student_id=student.id).all()
    
    # Calculate stats
    stats = {
        'applied': len(apps),
        'shortlisted': len([a for a in apps if a.status == 'Shortlisted']),
        'placed': len([a for a in apps if a.status == 'Selected']),
        'in_progress': len([a for a in apps if a.status in ['Applied', 'Shortlisted']])
    }
    
    # Applications with extra info
    apps_data = []
    for app in apps:
        job = JobPosition.query.get(app.job_id)
        company = Company.query.get(job.company_id)
        apps_data.append({
            'id': app.id,
            'job_title': job.title,
            'company_name': company.name,
            'applied_at': app.applied_at.isoformat(),
            'status': app.status,
            'match_percent': 85.0, # Placeholder for AI logic
            'success_prob': 92.4, # Placeholder for AI logic
            'feedback': getattr(app, 'feedback', None),
            'interview_date': getattr(app, 'interview_date', None)
        })
        
    return jsonify({
        'stats': stats,
        'applications': apps_data,
        'profile': {
            'full_name': student.full_name,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'grad_year': student.grad_year,
            'skills': student.skills or []
        }
    })

@student_bp.route('/jobs', methods=['GET'])
@token_required
def get_jobs(current_user):
    if current_user.role != 'Student':
        return jsonify({'message': 'Unauthorized'}), 403
    
    # Filter: Admin Approved AND not Closed
    # Using 'Approved' as the status for active.
    jobs = JobPosition.query.filter_by(status='Approved').all()
    student = current_user.student_profile
    
    # One-Placement Rule: Check if already placed
    is_placed = Application.query.filter_by(student_id=student.id, status='Placed').first() is not None
    
    applied_job_ids = [a.job_id for a in student.applications]
    
    output = []
    for job in jobs:
        company = Company.query.get(job.company_id)
        # Eligibility Check
        eligible = (student.cgpa or 0) >= (job.min_cgpa or 0)
        
        output.append({
            'id': job.id,
            'title': job.title,
            'company_name': company.name,
            'salary': job.salary,
            'description': job.description,
            'min_cgpa': job.min_cgpa,
            'deadline': job.deadline.isoformat() if job.deadline else None,
            'already_applied': job.id in applied_job_ids,
            'is_placed_locked': is_placed,
            'cgpa_eligible': eligible
        })
    return jsonify(output)

@student_bp.route('/apply/<int:job_id>', methods=['POST'])
@token_required
def apply_job(current_user, job_id):
    if current_user.role != 'Student':
        return jsonify({'message': 'Unauthorized'}), 403
    
    student = current_user.student_profile
    
    # Rule 1: One-Placement Rule
    if Application.query.filter_by(student_id=student.id, status='Placed').first():
        return jsonify({'message': 'You are already placed and cannot submit new applications.'}), 403
        
    # Rule 3: CGPA Hard Filter (Backend Enforcement)
    job = JobPosition.query.get_or_404(job_id)
    if (student.cgpa or 0) < (job.min_cgpa or 0):
        return jsonify({'message': 'You do not meet the minimum CGPA requirement for this role.'}), 403

    # Rule 5: Duplicate Guard
    existing = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
    if existing:
        return jsonify({'message': 'Duplicate application detected.'}), 400
        
    new_app = Application(student_id=student.id, job_id=job_id, status='Applied')
    db.session.add(new_app)
    db.session.commit()
    return jsonify({'message': 'Application submitted successfully'})

@student_bp.route('/offer-letter/<int:app_id>', methods=['GET'])
@token_required
def download_letter(current_user, app_id):
    # For now, just return a dummy message or file if exists
    return jsonify({'message': 'Offer letter generation is being finalized. Tracking available.'})
