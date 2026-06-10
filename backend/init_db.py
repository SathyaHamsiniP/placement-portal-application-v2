from werkzeug.security import generate_password_hash
from backend.main import create_app
from backend.database import db
from backend.models import User

def init_db():
    app = create_app()
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if admin exists
        admin = User.query.filter_by(role='Admin').first()
        if not admin:
            print("Creating default admin user...")
            admin_user = User(
                username='admin',
                email='admin@institute.edu',
                password_hash=generate_password_hash('admin123'), # Default password
                role='Admin',
                is_active=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_db()
