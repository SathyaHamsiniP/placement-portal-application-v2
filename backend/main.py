from flask import Flask
from flask_cors import CORS
from .database import db, mail
from .models import User, Company, Student, JobPosition, Application, Placement, Notification
from .auth import auth_bp
from .admin import admin_bp
from .company import company_bp
from .student import student_bp
from .jobs_api import jobs_bp
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    # Set instance path to project root/instance
    root_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.dirname(root_dir)
    instance_path = os.path.join(project_root, 'instance')
    
    app = Flask(__name__, instance_path=instance_path)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sathya-key'
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
    # Flask-Mail (configure with real SMTP credentials for production)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'noreply@placementportal.app')
    
    db.init_app(app)
    mail.init_app(app)
    CORS(app)
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    
    @app.route('/')
    def index():
        return {"message": "Placement Portal API is running"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
