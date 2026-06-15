from flask import Blueprint, jsonify, request
from .database import db
from .models import User, Company, Student, JobPosition, Application, Notification
from .auth import token_required
from datetime import datetime

company_bp = Blueprint('company', __name__)

@company_bp.route('/stats', methods=['GET'])
@token_required
def get_company_stats(current_user):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = current_user.company_profile
    if not company:
        return jsonify({'message': 'Company profile not found'}), 404
        
    job_ids = [j.id for j in company.job_positions]
    total_apps = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted = Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'Shortlisted').count() if job_ids else 0
    
    stats = {
        'jobs_posted': len(company.job_positions),
        'active_applications': total_apps,
        'verified_jobs': len([j for j in company.job_positions if j.status == 'Approved']),
        'placement_rate': 0, # Logic can be added later
        'recruitment_status': {
            'in_review': len([a for j in company.job_positions for a in j.applications if a.status == 'Applied']),
            'shortlisted': shortlisted,
            'interviewed': 0,
            'offered': len([a for j in company.job_positions for a in j.applications if a.status == 'Selected'])
        }
    }
    return jsonify(stats)

@company_bp.route('/jobs', methods=['GET'])
@token_required
def get_company_jobs(current_user):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = current_user.company_profile
    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    
    output = []
    for job in jobs:
        output.append({
            'id': job.id,
            'title': job.title,
            'status': job.status,
            'salary': job.salary,
            'applications_count': len(job.applications),
            'verified': job.status != 'Pending'
        })
    return jsonify(output)

@company_bp.route('/post-job', methods=['POST'])
@token_required
def post_job(current_user):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    if not current_user.company_profile.is_approved:
        return jsonify({'message': 'Your company profile is not yet approved by Admin'}), 403
        
    data = request.get_json()
    new_job = JobPosition(
        company_id=current_user.company_profile.id,
        title=data.get('title'),
        description=data.get('description'),
        salary=data.get('salary'),
        min_cgpa=data.get('min_cgpa'),
        allowed_branches=data.get('allowed_branches'),
        deadline=datetime.fromisoformat(data.get('deadline')) if data.get('deadline') else None
    )
    db.session.add(new_job)
    db.session.commit()
    return jsonify({'message': 'Job posted successfully and pending Admin approval'})

@company_bp.route('/applicants/<int:job_id>', methods=['GET'])
@token_required
def get_applicants(current_user, job_id):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    job = JobPosition.query.get_or_404(job_id)
    if job.company_id != current_user.company_profile.id:
        return jsonify({'message': 'Unauthorized'}), 403
        
    apps = Application.query.filter_by(job_id=job_id).all()
    output = []
    for app in apps:
        student = Student.query.get(app.student_id)
        output.append({
            'id': app.id,
            'student_name': student.full_name,
            'roll_number': student.roll_number,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'status': app.status,
            'applied_at': app.applied_at.isoformat()
        })
    return jsonify(output)

@company_bp.route('/application/update-status/<int:app_id>', methods=['POST'])
@token_required
def update_app_status(current_user, app_id):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    app = Application.query.get_or_404(app_id)
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['Shortlisted', 'Selected', 'Rejected']:
        return jsonify({'message': 'Invalid status'}), 400
        
    app.status = new_status
    db.session.commit()
    
    # Notify student (Logic can be expanded)
    return jsonify({'message': f'Application status updated to {new_status}'})
