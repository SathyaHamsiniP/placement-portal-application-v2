from datetime import datetime
from .database import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # Admin, Company, Student
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('Student', backref='user', uselist=False)
    company_profile = db.relationship('Company', backref='user', uselist=False)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(255))
    is_approved = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)

    # Relationships
    job_positions = db.relationship('JobPosition', backref='company', lazy=True)
    placements = db.relationship('Placement', backref='company', lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    branch = db.Column(db.String(50))
    cgpa = db.Column(db.Float)
    grad_year = db.Column(db.Integer)
    resume_url = db.Column(db.String(255))
    skills = db.Column(db.JSON)  # Stores list of skills

    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True)
    placements = db.relationship('Placement', backref='student', lazy=True)

class JobPosition(db.Model):
    __tablename__ = 'job_position'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    salary = db.Column(db.String(50))
    min_cgpa = db.Column(db.Float)
    allowed_branches = db.Column(db.JSON)  # Stores list of branches
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Closed

    # Relationships
    applications = db.relationship('Application', backref='job_position', lazy=True)

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job_position.id'), nullable=False)
    status = db.Column(db.String(20), default='Applied')  # Applied, Shortlisted, Selected, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

class Placement(db.Model):
    __tablename__ = 'placement'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    position = db.Column(db.String(100))
    salary = db.Column(db.String(50))
    joining_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
