from flask import Flask
from .database import db
from .models import User, Company, Student, JobPosition, Application, Placement, Notification

import os

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
    
    db.init_app(app)
    
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from flask_cors import CORS
    CORS(app)
    
    @app.route('/')
    def index():
        return {"message": "Placement Portal API is running"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
