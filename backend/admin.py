from flask import Blueprint, jsonify, request
from .database import db
from .models import User, Company, Student, JobPosition, Application
from .auth import token_required
from .cache import cache_response, invalidate_cache

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
        
    placed = Application.query.filter_by(status='Placed').count()
    total_students = Student.query.count()
    placement_rate = round((placed / total_students * 100), 1) if total_students > 0 else 0
    stats = {
        'total_students': total_students,
        'total_companies': Company.query.count(),
        'total_jobs': JobPosition.query.count(),
        'total_applications': Application.query.count(),
        'placement_rate': placement_rate,
        'pending_approvals': Company.query.filter_by(is_approved=False).count() + \
                             JobPosition.query.filter_by(status='Pending').count()
    }
    return jsonify(stats)

@admin_bp.route('/companies', methods=['GET'])
@token_required
@cache_response(timeout=300, key_prefix="admin_companies")
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
    # Invalidate cache since company approval state changed
    invalidate_cache("admin_companies:*")
    invalidate_cache("jobs_cache:*")
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
    # Invalidate cached jobs list
    invalidate_cache("jobs_cache:*")
    return jsonify({'message': 'Job posting approved'})

@admin_bp.route('/students', methods=['GET'])
@token_required
@cache_response(timeout=300, key_prefix="admin_students")
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
    # Invalidate both admin listing caches
    invalidate_cache("admin_companies:*")
    invalidate_cache("admin_students:*")
    invalidate_cache("jobs_cache:*")
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
    # Invalidate because company deleted
    invalidate_cache("admin_companies:*")
    invalidate_cache("jobs_cache:*")
    return jsonify({'message': 'Company removed successfully'})

@admin_bp.route('/student/<int:student_id>', methods=['DELETE'])
@token_required
def delete_student(current_user, student_id):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    student = Student.query.get_or_404(student_id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()
    # Invalidate because student deleted
    invalidate_cache("admin_students:*")
    invalidate_cache("jobs_cache:*")
    return jsonify({'message': 'Student removed successfully'})
@admin_bp.route('/applications', methods=['GET'])
@token_required
def get_applications(current_user):
    if current_user.role != 'Admin':
        return jsonify({'message': 'Unauthorized'}), 403
    
    apps = Application.query.all()
    output = []
    for app in apps:
        student = Student.query.get(app.student_id)
        job = JobPosition.query.get(app.job_id)
        company = Company.query.get(job.company_id)
        output.append({
            'id': app.id,
            'student_name': student.full_name,
            'job_title': job.title,
            'company_name': company.name,
            'status': app.status,
            'applied_on': app.applied_at.isoformat()
        })
    return jsonify(output)
@admin_bp.route('/student/<int:student_id>', methods=['GET'])
@token_required
def get_student_profile(current_user, student_id):
    if current_user.role not in ['Admin', 'Company']:
        return jsonify({'message': 'Unauthorized'}), 403

    student = Student.query.get_or_404(student_id)
    
    if current_user.role == 'Company':
        # Check if student is placed at any company
        other_placed = Application.query.filter(
            Application.student_id == student_id,
            Application.status == 'Placed'
        ).first()
        if other_placed:
            company_profile = current_user.company_profile
            placed_job = JobPosition.query.get(other_placed.job_id)
            if not company_profile or not placed_job or placed_job.company_id != company_profile.id:
                return jsonify({'message': 'Access restricted: Student is already placed at another company.'}), 403

    user = User.query.get(student.user_id)

    apps = Application.query.filter_by(student_id=student.id).all()
    history = []
    for app in apps:
        job = JobPosition.query.get(app.job_id)
        company = Company.query.get(job.company_id)
        history.append({
            'id': app.id,
            'job_title': job.title,
            'company_name': company.name,
            'salary': job.salary,
            'status': app.status,
            'feedback': app.feedback,
            'interview_date': app.interview_date.isoformat() if app.interview_date else None,
            'applied_at': app.applied_at.isoformat()
        })

    return jsonify({
        'id': student.id,
        'full_name': student.full_name,
        'roll_number': student.roll_number,
        'branch': student.branch,
        'cgpa': student.cgpa,
        'grad_year': student.grad_year,
        'skills': student.skills or [],
        'education_details': student.education_details or '',
        'experience': student.experience or '',
        'is_active': user.is_active,
        'email': user.email,
        'application_history': history
    })
