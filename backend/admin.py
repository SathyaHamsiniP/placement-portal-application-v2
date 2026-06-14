from flask import Blueprint, jsonify, request
from .database import db
from .models import User, Company, Student, JobPosition, Application
from .auth import token_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
        
    stats = {
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_jobs': JobPosition.query.count(),
        'total_applications': Application.query.count(),
        'pending_approvals': Company.query.filter_by(is_approved=False).count() + \
                             JobPosition.query.filter_by(status='Pending').count()
    }
    return jsonify(stats)

@admin_bp.route('/companies', methods=['GET'])
@token_required
def get_companies(current_user):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    companies = Company.query.all()
    output = []
    for company in companies:
        user = User.query.get(company.user_id)
        output.append({
            'id': company.id,
            'name': company.name,
            'industry': company.industry,
            'is_approved': company.is_approved,
            'is_active': user.is_active,
            'user_id': user.id,
            'email': user.email
        })
    return jsonify(output)

@admin_bp.route('/company/approve/<int:company_id>', methods=['POST'])
@token_required
def approve_company(current_user, company_id):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    return jsonify({'message': 'Company approved successfully'})

@admin_bp.route('/jobs', methods=['GET'])
@token_required
def get_jobs(current_user):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    jobs = JobPosition.query.all()
    output = []
    for job in jobs:
        company = Company.query.get(job.company_id)
        output.append({
            'id': job.id,
            'title': job.title,
            'company_name': company.name,
            'status': job.status,
            'salary': job.salary,
            'deadline': job.deadline.isoformat() if job.deadline else None
        })
    return jsonify(output)

@admin_bp.route('/job/approve/<int:job_id>', methods=['POST'])
@token_required
def approve_job(current_user, job_id):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    job = JobPosition.query.get_or_404(job_id)
    job.status = 'Approved'
    db.session.commit()
    return jsonify({'message': 'Job posting approved'})

@admin_bp.route('/students', methods=['GET'])
@token_required
def get_students(current_user):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    students = Student.query.all()
    output = []
    for student in students:
        user = User.query.get(student.user_id)
        output.append({
            'id': student.id,
            'full_name': student.full_name,
            'roll_number': student.roll_number,
            'branch': student.branch,
            'is_active': user.is_active,
            'user_id': user.id,
            'email': user.email
        })
    return jsonify(output)

@admin_bp.route('/user/toggle-active/<int:user_id>', methods=['POST'])
@token_required
def toggle_user_active(current_user, user_id):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'message': f'User {"activated" if user.is_active else "deactivated"} successfully'})

@admin_bp.route('/company/<int:company_id>', methods=['DELETE'])
@token_required
def delete_company(current_user, company_id):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    company = Company.query.get_or_404(company_id)
    user = User.query.get(company.user_id)
    db.session.delete(company)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Company removed successfully'})
