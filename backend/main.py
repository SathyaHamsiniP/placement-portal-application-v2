from flask import Flask
from .database import db
from .models import User, Company, Student, JobPosition, Application, Placement, Notification

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placement_portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sathya-key' # Change in production
    
    db.init_app(app)
    
    @app.route('/')
    def index():
        return {"message": "Placement Portal API is running"}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
