from flask import Blueprint, jsonify, request, send_file
from .database import db
from .models import User, Company, Student, JobPosition, Application, Notification
from .auth import token_required
from .cache import cache_response, invalidate_cache
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
        'placed': len([a for a in apps if a.status in ['Selected', 'Placed']]),
        'in_progress': len([a for a in apps if a.status in ['Applied', 'Review Pending', 'Shortlisted', 'Interviewed', 'Offered']])
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
            'interview_date': app.interview_date.isoformat() if getattr(app, 'interview_date', None) else None
        })
        
    return jsonify({
        'stats': stats,
        'applications': apps_data,
        'profile': {
            'full_name': student.full_name,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'grad_year': student.grad_year,
            'skills': student.skills or [],
            'education_details': student.education_details or '',
            'experience': student.experience or '',
            'resume_url': student.resume_url or ''
        }
    })

@student_bp.route('/jobs', methods=['GET'])
@token_required
@cache_response(timeout=300, key_prefix="jobs_cache")
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
            'allowed_branches': job.allowed_branches or [],
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
    # Invalidate cached job listings because the apply state of this user changes
    invalidate_cache("jobs_cache:*")
    return jsonify({'message': 'Application submitted successfully'})

@student_bp.route('/profile', methods=['POST'])
@token_required
def update_profile(current_user):
    if current_user.role != 'Student':
        return jsonify({'message': 'Unauthorized'}), 403
    student = current_user.student_profile
    data = request.get_json()
    
    student.full_name = data.get('full_name', student.full_name)
    student.branch = data.get('branch', student.branch)
    student.cgpa = data.get('cgpa', student.cgpa)
    student.grad_year = data.get('grad_year', student.grad_year)
    student.skills = data.get('skills', student.skills)
    student.education_details = data.get('education_details', student.education_details)
    student.experience = data.get('experience', student.experience)
    student.resume_url = data.get('resume_url', student.resume_url)
    
    db.session.commit()
    # Invalidate student list cache for administrators, and job eligibility listings for this student
    invalidate_cache("admin_students:*")
    invalidate_cache("jobs_cache:*")
    return jsonify({'message': 'Profile updated successfully'})


@student_bp.route('/upload-resume', methods=['POST'])
@token_required
def upload_resume(current_user):
    if current_user.role != 'Student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    if 'resume' not in request.files:
        return jsonify({'message': 'No file part'}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
        
    if file:
        from werkzeug.utils import secure_filename
        from flask import current_app
        import os
        filename = secure_filename(f"resume_{current_user.id}_{file.filename}")
        uploads_dir = os.path.join(current_app.root_path, 'uploads')
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        file_path = os.path.join(uploads_dir, filename)
        file.save(file_path)
        
        student = current_user.student_profile
        student.resume_url = f"/api/student/resume/download/{filename}"
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'resume_url': student.resume_url
        })


@student_bp.route('/resume/download/<filename>', methods=['GET'])
def download_resume_file(filename):
    from flask import current_app
    import os
    uploads_dir = os.path.join(current_app.root_path, 'uploads')
    file_path = os.path.join(uploads_dir, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return jsonify({'message': 'File not found'}), 404


@student_bp.route('/offer-letter/<int:app_id>', methods=['GET'])
@token_required
def download_letter(current_user, app_id):
    if current_user.role != 'Student':
        return jsonify({'message': 'Unauthorized'}), 403
        
    app = Application.query.get_or_404(app_id)
    if app.student_id != current_user.student_profile.id:
        return jsonify({'message': 'Unauthorized'}), 403
        
    if app.status not in ['Offered', 'Placed']:
        return jsonify({'message': 'Offer letter not available. Current status is ' + app.status}), 400
        
    job = JobPosition.query.get(app.job_id)
    company = Company.query.get(job.company_id)
    student = current_user.student_profile
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: auto; border: 1px solid #ddd; line-height: 1.6; background-color: #ffffff; color: #333333;">
        <div style="text-align: center; border-bottom: 2px solid #1a365d; padding-bottom: 20px; margin-bottom: 30px;">
            <h1 style="margin: 0; color: #1a365d; text-transform: uppercase; font-size: 28px;">{company.name}</h1>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">{company.industry or 'Corporate Partner'} | {company.website or ''}</p>
        </div>
        <p style="text-align: right; color: #666; font-weight: bold;">Date: {datetime.utcnow().strftime('%B %d, %Y')}</p>
        
        <p style="font-size: 15px;">
            <strong>To,</strong><br>
            <strong>{student.full_name}</strong><br>
            Roll Number: {student.roll_number}<br>
            Branch: {student.branch or 'N/A'}
        </p>
        
        <h3 style="color: #1a365d; margin-top: 30px; font-size: 18px; border-bottom: 1px solid #edf2f7; padding-bottom: 8px;">Subject: Offer of Employment - {job.title}</h3>
        
        <p style="font-size: 15px;">Dear {student.full_name},</p>
        
        <p style="font-size: 15px;">We are pleased to offer you the position of <strong>{job.title}</strong> at <strong>{company.name}</strong>. We were highly impressed by your academic background, performance, and overall capabilities during our potential recruitment rounds.</p>
        
        <p style="font-size: 15px;">The details of your offer are as follows:</p>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 15px;">
            <tr style="background-color: #f7fafc;">
                <td style="padding: 12px; border: 1px solid #edf2f7; font-weight: bold; width: 40%;">Position</td>
                <td style="padding: 12px; border: 1px solid #edf2f7;">{job.title}</td>
            </tr>
            <tr>
                <td style="padding: 12px; border: 1px solid #edf2f7; font-weight: bold;">Compensation (CTC)</td>
                <td style="padding: 12px; border: 1px solid #edf2f7;">{job.salary or 'Confidential'}</td>
            </tr>
            <tr style="background-color: #f7fafc;">
                <td style="padding: 12px; border: 1px solid #edf2f7; font-weight: bold;">Job Location</td>
                <td style="padding: 12px; border: 1px solid #edf2f7;">{company.location or 'Institute Placement Drive'}</td>
            </tr>
        </table>
        
        <p style="font-size: 15px;">Please review coordinates and guidelines provided in the onboarding portal. To accept this offer, kindly sign and submit this letter on the Campus Placement Portal.</p>
        
        <div style="margin-top: 60px; display: flex; justify-content: space-between; font-size: 15px;">
            <div>
                <p style="margin-bottom: 60px;">Sincerely,</p>
                <strong>HR Department</strong><br>
                {company.name}
            </div>
            <div style="text-align: right;">
                <p style="margin-bottom: 60px;">Accepted By:</p>
                <strong>{student.full_name}</strong><br>
                Date: _________________
            </div>
        </div>
    </div>
    """
    return jsonify({
        'success': True,
        'html': html_content,
        'filename': f"Offer_Letter_{company.name.replace(' ', '_')}_{student.full_name.replace(' ', '_')}.html"
    })
