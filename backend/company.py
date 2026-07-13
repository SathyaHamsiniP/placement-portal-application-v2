from flask import Blueprint, jsonify, request
from .database import db, auto_update_passed_interviews
from .models import User, Company, Student, JobPosition, Application, Notification
from .auth import token_required
from .cache import invalidate_cache
from datetime import datetime

company_bp = Blueprint('company', __name__)

@company_bp.route('/stats', methods=['GET'])
@token_required
def get_company_stats(current_user):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    auto_update_passed_interviews()
    
    company = current_user.company_profile
    if not company:
        return jsonify({'message': 'Company profile not found'}), 404
        
    job_ids = [j.id for j in company.job_positions]
    total_apps = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted = Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'Shortlisted').count() if job_ids else 0
    in_review = Application.query.filter(Application.job_id.in_(job_ids), Application.status.in_(['Applied', 'Review Pending'])).count() if job_ids else 0
    interviewed = Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'Interviewed').count() if job_ids else 0
    offered = Application.query.filter(Application.job_id.in_(job_ids), Application.status.in_(['Offered', 'Placed'])).count() if job_ids else 0
    
    placement_rate = int((offered / total_apps * 100)) if total_apps > 0 else 0
    
    stats = {
        'company_name': company.name,
        'industry': company.industry,
        'jobs_posted': len(company.job_positions),
        'active_applications': total_apps,
        'verified_jobs': len([j for j in company.job_positions if j.status == 'Approved']),
        'placement_rate': f"{placement_rate}%",
        'recruitment_status': {
            'in_review': in_review,
            'shortlisted': shortlisted,
            'interviewed': interviewed,
            'offered': offered
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
    # Invalidate cache since a new job was pending/posted
    invalidate_cache("jobs_cache:*")
    return jsonify({'message': 'Job posted successfully and pending Admin approval'})

@company_bp.route('/applicants/<int:job_id>', methods=['GET'])
@token_required
def get_applicants(current_user, job_id):
    if current_user.role != 'Company':
        return jsonify({'message': 'Unauthorized'}), 403
    
    job = JobPosition.query.get_or_404(job_id)
    if job.company_id != current_user.company_profile.id:
        return jsonify({'message': 'Unauthorized'}), 403
        
    auto_update_passed_interviews()
    apps = Application.query.filter_by(job_id=job_id).all()
    output = []
    for app in apps:
        # If student has a Placed application, and it is NOT for this company, reject visibility
        other_placed = Application.query.filter(
            Application.student_id == app.student_id,
            Application.status == 'Placed',
            Application.job_id != job_id
        ).first()
        if other_placed:
            # Skip this application entirely: student has been placed at another company
            continue

        student = Student.query.get(app.student_id)
        output.append({
            'id': app.id,
            'student_id': student.id,
            'student_name': student.full_name,
            'roll_number': student.roll_number,
            'branch': student.branch,
            'cgpa': student.cgpa,
            'grad_year': student.grad_year,
            'skills': student.skills or [],
            'education_details': student.education_details or '',
            'experience': student.experience or '',
            'status': app.status,
            'feedback': app.feedback or '',
            'interview_date': app.interview_date.isoformat() if app.interview_date else None,
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
    feedback = data.get('feedback', '')
    interview_date_str = data.get('interview_date')
    
    valid_statuses = ['Applied', 'Review Pending', 'Shortlisted', 'Interviewed', 'Offered', 'Placed', 'Rejected']
    if new_status not in valid_statuses:
        return jsonify({'message': 'Invalid status'}), 400
        
    app.status = new_status
    app.feedback = feedback
    
    if new_status == 'Shortlisted':
        if interview_date_str:
            try:
                app.interview_date = datetime.fromisoformat(interview_date_str.replace('Z', ''))
            except (ValueError, TypeError):
                pass
        
        # Send immediate email notification to student if SMTP is active
        from flask import current_app
        from .tasks import _mail_ready
        if _mail_ready(current_app):
            try:
                from flask_mail import Message
                from .database import mail
                if app.student.user and app.student.user.email:
                    formatted_dt = app.interview_date.strftime('%d %b %Y, %I:%M %p') if app.interview_date else "TBD"
                    email_msg = Message(
                        subject=f"Interview Scheduled: {app.job_position.title}",
                        recipients=[app.student.user.email],
                        body=(
                            f"Hello {app.student.full_name},\n\n"
                            f"An interview for the position '{app.job_position.title}' at {app.job_position.company.name} has been scheduled.\n"
                            f"Date & Time: {formatted_dt}\n"
                            f"Corporate Feedback / Message: {feedback}\n\n"
                            "Best regards,\nPlacement Portal Team"
                        )
                    )
                    mail.send(email_msg)
            except Exception as e:
                current_app.logger.error(f"Failed to email interview schedule: {e}")
            
    if new_status == 'Placed':
        from .models import Placement
        # check if model placement exists
        existing_placement = Placement.query.filter_by(student_id=app.student_id, company_id=app.job_position.company_id).first()
        if not existing_placement:
            new_placement = Placement(
                student_id=app.student_id,
                company_id=app.job_position.company_id,
                position=app.job_position.title,
                salary=app.job_position.salary
            )
            db.session.add(new_placement)
            
    db.session.commit()
    
    # Create notification for student
    student_user_id = app.student.user_id
    notif = Notification(
        user_id=student_user_id,
        message=f"Update for {app.job_position.title}: You have been marked as {new_status}. Feedback: {feedback}"
    )
    db.session.add(notif)
    db.session.commit()
    
    return jsonify({'message': f'Application updated to {new_status}'})
