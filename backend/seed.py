"""
seed.py
-------
Populate the database with demo data for testing.
Run from the project root:
    python -m backend.seed
"""

from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from .main import create_app
from .database import db
from .models import User, Company, Student, JobPosition, Application, Placement, Notification


# ──────────────────────────────────────────────
# Demo data constants
# ──────────────────────────────────────────────
INDUSTRIES = [
    "Software", "Hardware", "Finance", "Consulting",
    "Cloud", "AI/ML", "E-Commerce", "HealthTech", "EdTech", "Logistics"
]

BRANCHES = [
    "Computer Science", "Electrical Engineering",
    "Mechanical Engineering", "Civil Engineering", "Chemical Engineering"
]

SKILL_SETS = [
    ["Python", "SQL", "Problem Solving", "Git"],
    ["JavaScript", "Vue.js", "React", "HTML", "CSS"],
    ["Cloud", "AWS", "Docker", "Python", "SQL"],
    ["Java", "Spring Boot", "Microservices", "SQL"],
    ["Data Analysis", "Machine Learning", "Python", "TensorFlow"],
]

JOB_DESCRIPTIONS = [
    "Work on scalable backend systems and APIs serving millions of users.",
    "Build beautiful, responsive interfaces and deliver great user experience.",
    "Design and maintain cloud infrastructure for critical production workloads.",
    "Analyze large datasets and build ML models to drive business decisions.",
    "Develop and maintain enterprise Java applications for global clients.",
]

LOCATIONS = ["Bangalore", "Hyderabad", "Mumbai", "Pune", "Remote", "Hybrid"]

APP_STATUSES = [
    "Applied", "Review Pending", "Shortlisted",
    "Interviewed", "Offered", "Placed", "Rejected"
]

FEEDBACKS = {
    "Shortlisted":    "Impressive academic record. Moving forward to technical round.",
    "Interviewed":    "Strong problem-solving skills demonstrated. Awaiting final evaluation.",
    "Offered":        "Excellent performance across all rounds. Offer extended.",
    "Placed":         "Congratulations! You have been successfully placed.",
    "Rejected":       "Thank you for your interest. We will consider your profile for future openings.",
}


# ──────────────────────────────────────────────
# Seed function
# ──────────────────────────────────────────────
def seed_data():
    app = create_app()
    with app.app_context():
        print(f"[seed] Target DB → {app.config['SQLALCHEMY_DATABASE_URI']}")

        # ── Wipe everything except the Admin user ──
        print("[seed] Clearing existing demo data…")
        Notification.query.delete()
        Placement.query.delete()
        Application.query.delete()
        JobPosition.query.delete()

        # Delete company + student profiles and their users
        for c in Company.query.all():
            u = User.query.get(c.user_id)
            db.session.delete(c)
            if u:
                db.session.delete(u)
        for s in Student.query.all():
            u = User.query.get(s.user_id)
            db.session.delete(s)
            if u:
                db.session.delete(u)

        db.session.commit()

        # ── Companies ──────────────────────────────
        print("[seed] Seeding 10 companies…")
        companies = []
        for i in range(1, 11):
            # Companies 8 = pending, 9 = not approved, 10 = deactivated
            is_approved = (i not in [8, 9])
            is_active   = (i != 10)

            u = User(
                username=f"company{i}",
                email=f"company{i}@demo.com",
                password_hash=generate_password_hash("Demo@123", method="pbkdf2:sha256", salt_length=8),
                role="Company",
                is_active=is_active,
            )
            db.session.add(u)
            db.session.flush()   # get u.id

            c = Company(
                user_id=u.id,
                name=f"{INDUSTRIES[i-1]} Corp {i}",
                industry=INDUSTRIES[i-1],
                location=LOCATIONS[i % len(LOCATIONS)],
                hr_contact=f"+91 98000 {i:05d}",
                website=f"https://company{i}.demo.com",
                is_approved=is_approved,
                description=f"A leading firm in the {INDUSTRIES[i-1]} domain, delivering innovative solutions since 20{10+i}.",
            )
            db.session.add(c)
            companies.append(c)

        db.session.commit()
        print(f"    ✓ {len(companies)} companies created")

        # ── Students ──────────────────────────────
        print("[seed] Seeding 20 students…")
        students = []
        for i in range(1, 21):
            is_active = (i != 20)   # student 20 is blacklisted
            branch    = BRANCHES[i % 5]
            cgpa      = round(6.5 + (i % 4) * 0.4 + (i * 0.03), 2)
            cgpa      = min(cgpa, 10.0)
            skills    = SKILL_SETS[i % len(SKILL_SETS)]

            u = User(
                username=f"student{i}",
                email=f"student{i}@demo.com",
                password_hash=generate_password_hash("Demo@123", method="pbkdf2:sha256", salt_length=8),
                role="Student",
                is_active=is_active,
            )
            db.session.add(u)
            db.session.flush()

            s = Student(
                user_id=u.id,
                full_name=f"Student {i}",
                roll_number=f"IITM2024{i:03d}",
                branch=branch,
                cgpa=cgpa,
                grad_year=2024 + (i % 2),
                skills=skills,
                education_details=(
                    f"Class 12: {85 + (i % 10)}% | "
                    f"B.Tech {branch}: CGPA {cgpa}"
                ),
                experience=(
                    "Intern at StartupX (6 months) — built REST APIs using Flask and PostgreSQL."
                    if i % 3 == 0 else
                    "Completed 3 academic projects in data structures, web development, and ML."
                ),
            )
            db.session.add(s)
            students.append(s)

        db.session.commit()
        print(f"    ✓ {len(students)} students created")

        # ── Jobs ──────────────────────────────────
        # 7 approved companies each post 2 jobs (14 total).
        # The last approved company's jobs are left 'Pending' (admin hasn't verified yet).
        # One job is 'Closed'.
        print("[seed] Seeding job positions…")
        approved_companies = [c for c in companies if c.is_approved][:7]
        jobs = []
        for idx, company in enumerate(approved_companies):
            for j in range(1, 3):
                if idx == 0 and j == 1:
                    status = "Closed"
                elif idx == 6:
                    status = "Pending"
                else:
                    status = "Approved"

                skill_pool = SKILL_SETS[(idx + j) % len(SKILL_SETS)]
                allowed    = [BRANCHES[k] for k in range(0, 5, j)]

                job = JobPosition(
                    company_id=company.id,
                    title=f"{company.industry} {['Engineer', 'Analyst'][j-1]} — Role {j}",
                    description=JOB_DESCRIPTIONS[(idx + j) % len(JOB_DESCRIPTIONS)],
                    salary=f"{5 + idx + j} LPA",
                    min_cgpa=round(6.5 + (j * 0.2), 1),
                    allowed_branches=allowed,
                    deadline=datetime.utcnow() + timedelta(days=15 + idx * 3),
                    status=status,
                )
                db.session.add(job)
                jobs.append(job)

        db.session.commit()
        print(f"    ✓ {len(jobs)} job positions created")

        # ── Applications ──────────────────────────
        print("[seed] Seeding applications…")
        approved_jobs = [j for j in jobs if j.status == "Approved"]

        # Student 1 gets one application per status (full pipeline demo)
        demo_student = students[0]
        for status_idx, status in enumerate(APP_STATUSES):
            if status_idx >= len(approved_jobs):
                break
            target_job = approved_jobs[status_idx]
            interview_date = (
                datetime.utcnow() + timedelta(days=3)
                if status in ["Interviewed", "Offered", "Placed"]
                else None
            )
            app_rec = Application(
                student_id=demo_student.id,
                job_id=target_job.id,
                status=status,
                feedback=FEEDBACKS.get(status),
                interview_date=interview_date,
            )
            db.session.add(app_rec)

            # Create Placement record if Placed
            if status == "Placed":
                placement = Placement(
                    student_id=demo_student.id,
                    company_id=target_job.company_id,
                    position=target_job.title,
                    salary=target_job.salary,
                    joining_date=date.today() + timedelta(days=60),
                )
                db.session.add(placement)

                # Notify student
                notif = Notification(
                    user_id=demo_student.user_id,
                    message=f"Congratulations! You have been placed at "
                            f"{Company.query.get(target_job.company_id).name} "
                            f"as {target_job.title}.",
                )
                db.session.add(notif)

        # Remaining students: 2 applications each
        for s_idx in range(1, len(students)):
            s = students[s_idx]
            picked = set()
            for offset in [s_idx * 2, s_idx * 3, s_idx + 1]:
                j_idx = offset % len(approved_jobs)
                if j_idx in picked:
                    continue
                picked.add(j_idx)
                target_job = approved_jobs[j_idx]
                # Skip if CGPA too low
                if (s.cgpa or 0) < (target_job.min_cgpa or 0):
                    continue
                existing = Application.query.filter_by(
                    student_id=s.id, job_id=target_job.id
                ).first()
                if existing:
                    continue
                app_rec = Application(
                    student_id=s.id,
                    job_id=target_job.id,
                    status="Applied",
                )
                db.session.add(app_rec)

        db.session.commit()
        print(f"    ✓ Applications seeded")

        # ── Summary ────────────────────────────────
        print("\n[seed] ✅ Done! Summary:")
        print(f"        Companies   : {Company.query.count()}")
        print(f"        Students    : {Student.query.count()}")
        print(f"        Jobs        : {JobPosition.query.count()}")
        print(f"        Applications: {Application.query.count()}")
        print(f"        Placements  : {Placement.query.count()}")
        print("\n  Default credentials for all seeded users → password: Demo@123")
        print("  e.g.  student1 / Demo@123   |   company1 / Demo@123")


if __name__ == "__main__":
    seed_data()
