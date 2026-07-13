from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

def auto_update_passed_interviews():
    from datetime import datetime
    from .models import Application
    from .cache import invalidate_cache
    try:
        now = datetime.now()
        # Find Shortlisted apps where interview date/time has passed
        passed_apps = Application.query.filter(
            Application.status == 'Shortlisted',
            Application.interview_date != None,
            Application.interview_date <= now
        ).all()
        if passed_apps:
            for app in passed_apps:
                app.status = 'Interviewed'
            db.session.commit()
            invalidate_cache("jobs_cache:*")
    except Exception:
        pass
