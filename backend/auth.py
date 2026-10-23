import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db
from .models import User, Student, Company
from .cache import invalidate_cache

auth_bp = Blueprint('auth', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            # Token format: "Bearer <token>"
            token = token.split(" ")[1]
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Username or Email already exists'}), 400
    
    if len(data['password']) < 6 or '@' not in data['email']:
        return jsonify({'message': 'Invalid email or password format'}), 400
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role='Student'
    )
    
    db.session.add(new_user)
    db.session.flush() # Get user ID
    
    skills_raw = data.get('skills', '')
    if isinstance(skills_raw, list):
        skills_list = skills_raw
    else:
        skills_list = [s.strip() for s in skills_raw.split(',') if s.strip()]

    student_profile = Student(
        user_id=new_user.id,
        full_name=data['full_name'],
        roll_number=data['roll_number'],
        branch=data.get('branch'),
        cgpa=float(data['cgpa']) if data.get('cgpa') else None,
        grad_year=int(data['grad_year']) if data.get('grad_year') else None,
        skills=skills_list,
        education_details=data.get('education_details'),
        experience=data.get('experience')
    )
    
    db.session.add(student_profile)
    db.session.commit()
    # Invalidate student list cache for Admin
    invalidate_cache("admin_students:*")
    
    return jsonify({'message': 'Student registered successfully'}), 201

@auth_bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json()
    
    if User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Username or Email already exists'}), 400
    
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role='Company'
    )
    
    db.session.add(new_user)
    db.session.flush()
    
    company_profile = Company(
        user_id=new_user.id,
        name=data['name'],
        industry=data.get('industry', 'Technology'),
        hr_contact=data['hr_contact'],
        location=data.get('location'),
        website=data.get('website'),
        description=data.get('description'),
        is_approved=False # Pending admin approval
    )
    
    db.session.add(company_profile)
    db.session.commit()
    # Invalidate company listing cache for Admin
    invalidate_cache("admin_companies:*")
    
    return jsonify({'message': 'Company registered successfully. Pending Admin approval.'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if user.role == 'Company':
        company = Company.query.filter_by(user_id=user.id).first()
        if not company.is_approved:
            return jsonify({'message': 'Your account is pending admin approval.'}), 403
            
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated.'}), 403

    token = jwt.encode({
        'user_id': user.id,
        'role': user.role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")
    
    return jsonify({
        'token': token,
        'role': user.role,
        'username': user.username
    })
