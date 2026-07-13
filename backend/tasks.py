"""
tasks.py  –  All Celery background tasks

  1. send_interview_reminders       – Daily 8 AM: email students with interviews in 24 h
  2. send_deadline_reminders        – Daily 9 AM: email students about deadlines in 48 h
  3. generate_monthly_placement_report – 1st of month 7 AM: HTML report emailed to admin
  4. generate_monthly_company_report   – 1st of month 7:30 AM: per-company HTML report
  5. export_student_csv             – User-triggered async CSV + email alert
  6. export_company_csv             – User-triggered async CSV + email alert
"""

from __future__ import annotations

import csv
import io
import logging
import os
from datetime import datetime, timedelta, timezone

from .celery_app import celery_app

log = logging.getLogger(__name__)

# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_app():
    """Import create_app lazily to avoid circular imports."""
    from .main import create_app
    return create_app()


def _instance_dir():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    d = os.path.join(base, "instance")
    os.makedirs(d, exist_ok=True)
    return d


def _mail_ready(app) -> bool:
    """
    Returns True only when SMTP credentials are genuinely configured —
    i.e. not empty and not still containing the placeholder defaults.
    Logs a clear warning when email is skipped so it's never silent.
    """
    PLACEHOLDERS = {"your_email@gmail.com", "your_gmail_app_password", "", None}
    username = app.config.get("MAIL_USERNAME")
    password = app.config.get("MAIL_PASSWORD")
    if username in PLACEHOLDERS or password in PLACEHOLDERS:
        log.warning(
            "[MAIL] SMTP not configured — email skipped. "
            "Set MAIL_USERNAME and MAIL_PASSWORD in your .env file to enable real delivery."
        )
        return False
    return True


# ── Task 1: Interview Reminders (Scheduled daily) ─────────────────────────────

@celery_app.task(name="backend.tasks.send_interview_reminders", bind=True)
def send_interview_reminders(self):
    """
    Find all applications whose interview_date falls within the next 24 hours
    and log a reminder. In production swap the log.info() calls with actual
    SMTP / GChat / SMS API calls.
    """
    app = _get_app()
    with app.app_context():
        from .models import Application, Student, JobPosition, Company, Notification
        from .database import db

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        window_end = now + timedelta(hours=24)

        upcoming = (
            Application.query
            .filter(
                Application.interview_date != None,
                Application.interview_date >= now,
                Application.interview_date <= window_end,
                Application.status.in_(["Shortlisted", "Interviewed"]),
            )
            .all()
        )

        sent = 0
        for app_rec in upcoming:
            student = Student.query.get(app_rec.student_id)
            job = JobPosition.query.get(app_rec.job_id)
            company = Company.query.get(job.company_id) if job else None

            if not student or not job or not company:
                continue

            msg = (
                f"Reminder: Your interview for '{job.title}' at {company.name} "
                f"is scheduled on {app_rec.interview_date.strftime('%d %b %Y, %I:%M %p')}. "
                "All the best!"
            )

            # Log reminder (replace with email/SMS in production)
            log.info("[REMINDER] Student=%s | %s", student.full_name, msg)

            # Store as in-app notification
            notif = Notification(user_id=student.user_id, message=msg)
            db.session.add(notif)
            sent += 1

            # Email Dispatch if SMTP is configured
            if _mail_ready(app):
                try:
                    from flask_mail import Message
                    from .database import mail
                    from .models import User
                    u = User.query.get(student.user_id)
                    if u and u.email:
                        msg_mail = Message(
                            subject="Interview Reminder - Placement Portal",
                            recipients=[u.email],
                            body=msg
                        )
                        mail.send(msg_mail)
                        log.info("[REMINDER] Email notification sent to %s", u.email)
                except Exception as e:
                    log.error("[REMINDER] Failed to send email notification to %s: %s", student.full_name, str(e))

        db.session.commit()
        log.info("[REMINDER] Sent %d interview reminders.", sent)
        return {"reminders_sent": sent, "timestamp": now.isoformat()}


# ── Task 2: Monthly Placement Report (Scheduled 1st of month) ─────────────────

@celery_app.task(name="backend.tasks.generate_monthly_placement_report", bind=True)
def generate_monthly_placement_report(self):
    """
    Generate an HTML placement report for the previous month and save it to
    instance/reports/placement_report_YYYY_MM.html.
    In production this could be emailed as a PDF attachment.
    """
    app = _get_app()
    with app.app_context():
        from .models import Placement, Student, Company, Application

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        # Report covers the previous calendar month
        first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_of_prev_month = (first_of_this_month - timedelta(days=1)).replace(day=1)

        placements = (
            Placement.query
            .filter(
                Placement.created_at >= first_of_prev_month,
                Placement.created_at < first_of_this_month,
            )
            .all()
        )

        total_apps = Application.query.filter(
            Application.applied_at >= first_of_prev_month,
            Application.applied_at < first_of_this_month,
        ).count()

        rows_html = ""
        for p in placements:
            student = Student.query.get(p.student_id)
            company = Company.query.get(p.company_id)
            rows_html += (
                f"<tr>"
                f"<td>{student.full_name if student else 'N/A'}</td>"
                f"<td>{student.roll_number if student else 'N/A'}</td>"
                f"<td>{company.name if company else 'N/A'}</td>"
                f"<td>{p.position}</td>"
                f"<td>{p.salary}</td>"
                f"<td>{p.joining_date}</td>"
                f"</tr>"
            )

        month_label = first_of_prev_month.strftime("%B %Y")
        html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset='utf-8'>
  <title>Placement Report — {month_label}</title>
  <style>
    body {{ font-family: 'Inter', sans-serif; color: #0f172a; padding: 40px; }}
    h1 {{ color: #f97316; }} h2 {{ color: #475569; font-size: 1rem; font-weight: 500; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 24px; }}
    th {{ background: #0f172a; color: white; padding: 10px 14px; text-align: left; font-size: .8rem; text-transform: uppercase; }}
    td {{ padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-size: .875rem; }}
    tr:nth-child(even) td {{ background: #f8fafc; }}
    .summary {{ display: flex; gap: 40px; margin: 32px 0; }}
    .stat {{ background: #f1f5f9; border-radius: 12px; padding: 20px 28px; }}
    .stat-val {{ font-size: 2rem; font-weight: 800; color: #f97316; }}
    .stat-lbl {{ font-size: .75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: .08em; }}
  </style>
</head>
<body>
  <h1>Campus Placement Portal</h1>
  <h2>Monthly Placement Report — {month_label}</h2>
  <p>Generated on {now.strftime('%d %B %Y, %I:%M %p IST')}</p>
  <div class='summary'>
    <div class='stat'><div class='stat-val'>{len(placements)}</div><div class='stat-lbl'>Placements</div></div>
    <div class='stat'><div class='stat-val'>{total_apps}</div><div class='stat-lbl'>Total Applications</div></div>
    <div class='stat'><div class='stat-val'>{round(len(placements)/total_apps*100, 1) if total_apps else 0}%</div><div class='stat-lbl'>Placement Rate</div></div>
  </div>
  <table>
    <thead><tr><th>Student</th><th>Roll No.</th><th>Company</th><th>Position</th><th>Salary</th><th>Joining</th></tr></thead>
    <tbody>{rows_html if rows_html else "<tr><td colspan='6' style='text-align:center;color:#94a3b8'>No placements this month.</td></tr>"}</tbody>
  </table>
</body>
</html>"""

        reports_dir = os.path.join(_instance_dir(), "reports")
        os.makedirs(reports_dir, exist_ok=True)
        filename = f"placement_report_{first_of_prev_month.strftime('%Y_%m')}.html"
        filepath = os.path.join(reports_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        log.info("[REPORT] Saved %s", filepath)

        # ── Email to admin if SMTP is ready ──────────────────────────────────
        if _mail_ready(app):
            try:
                from flask_mail import Message
                from .database import mail
                from .models import User
                admin = User.query.filter_by(role='Admin').first()
                if admin and admin.email:
                    mail_msg = Message(
                        subject=f"Monthly Placement Report – {month_label}",
                        recipients=[admin.email],
                        html=html,
                    )
                    mail.send(mail_msg)
                    log.info("[REPORT] Admin report emailed to %s", admin.email)
            except Exception as e:
                log.error("[REPORT] Failed to email admin report: %s", e)

        return {"report": filename, "placements": len(placements)}


# ── Task 2b: Daily Deadline Reminders (Scheduled daily) ───────────────────────

@celery_app.task(name="backend.tasks.send_deadline_reminders", bind=True)
def send_deadline_reminders(self):
    """
    Find all approved job positions whose deadline falls within the next 48 h
    and remind eligible students who have NOT yet applied.
    """
    app = _get_app()
    with app.app_context():
        from .models import JobPosition, Student, Application, Notification, User
        from .database import db

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        window_end = now + timedelta(hours=48)

        expiring_jobs = JobPosition.query.filter(
            JobPosition.status == 'Approved',
            JobPosition.deadline != None,
            JobPosition.deadline >= now,
            JobPosition.deadline <= window_end,
        ).all()

        reminded = 0
        for job in expiring_jobs:
            already_applied_ids = {
                a.student_id for a in Application.query.filter_by(job_id=job.id).all()
            }
            # Find eligible students who haven't applied
            eligible = Student.query.filter(
                Student.cgpa >= (job.min_cgpa or 0),
                Student.id.notin_(already_applied_ids),
            ).all()

            for student in eligible:
                deadline_str = job.deadline.strftime('%d %b %Y, %I:%M %p')
                msg = (
                    f"Deadline Alert: '{job.title}' closes on {deadline_str}. "
                    "Don't miss out — apply now on the Placement Portal!"
                )
                notif = Notification(user_id=student.user_id, message=msg)
                db.session.add(notif)
                log.info("[DEADLINE] Remind student=%s job='%s'", student.full_name, job.title)

                if _mail_ready(app):
                    try:
                        from flask_mail import Message
                        from .database import mail
                        u = User.query.get(student.user_id)
                        if u and u.email:
                            mail.send(Message(
                                subject=f"Deadline Reminder: {job.title}",
                                recipients=[u.email],
                                body=msg,
                            ))
                    except Exception as e:
                        log.error("[DEADLINE] Email failed for %s: %s", student.full_name, e)
                reminded += 1

        db.session.commit()
        log.info("[DEADLINE] %d deadline reminders dispatched.", reminded)
        return {"reminded": reminded}


# ── Task 4: Monthly Company Report (Scheduled 1st of month) ───────────────────

@celery_app.task(name="backend.tasks.generate_monthly_company_report", bind=True)
def generate_monthly_company_report(self):
    """
    Generate a per-company HTML report for the previous month and email it
    to each company's registered user.
    """
    app = _get_app()
    with app.app_context():
        from .models import Company, JobPosition, Application, Student, User
        from .database import db

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_of_prev_month = (first_of_this_month - timedelta(days=1)).replace(day=1)
        month_label = first_of_prev_month.strftime("%B %Y")

        companies = Company.query.filter_by(is_approved=True).all()
        sent_count = 0

        for company in companies:
            job_ids = [j.id for j in company.job_positions]
            if not job_ids:
                continue

            apps_this_month = Application.query.filter(
                Application.job_id.in_(job_ids),
                Application.applied_at >= first_of_prev_month,
                Application.applied_at < first_of_this_month,
            ).all()

            total      = len(apps_this_month)
            shortlisted = sum(1 for a in apps_this_month if a.status == 'Shortlisted')
            offered     = sum(1 for a in apps_this_month if a.status in ('Offered', 'Placed'))
            rejected    = sum(1 for a in apps_this_month if a.status == 'Rejected')

            rows_html = ""
            for a in apps_this_month:
                s = Student.query.get(a.student_id)
                j = JobPosition.query.get(a.job_id)
                rows_html += (
                    f"<tr><td>{s.full_name if s else 'N/A'}</td>"
                    f"<td>{s.roll_number if s else 'N/A'}</td>"
                    f"<td>{j.title if j else 'N/A'}</td>"
                    f"<td>{a.status}</td>"
                    f"<td>{a.applied_at.strftime('%d %b %Y') if a.applied_at else ''}</td></tr>"
                )

            html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
<title>Company Report – {month_label}</title>
<style>
  body{{font-family:Inter,sans-serif;color:#0f172a;padding:40px;}}
  h1{{color:#f97316;}} h2{{color:#475569;font-size:1rem;font-weight:500;}}
  table{{border-collapse:collapse;width:100%;margin-top:24px;}}
  th{{background:#0f172a;color:white;padding:10px 14px;text-align:left;font-size:.8rem;text-transform:uppercase;}}
  td{{padding:10px 14px;border-bottom:1px solid #e2e8f0;font-size:.875rem;}}
  tr:nth-child(even) td{{background:#f8fafc;}}
  .summary{{display:flex;gap:32px;margin:28px 0;}}
  .stat{{background:#f1f5f9;border-radius:12px;padding:18px 24px;}}
  .stat-val{{font-size:1.8rem;font-weight:800;color:#f97316;}}
  .stat-lbl{{font-size:.75rem;font-weight:600;color:#64748b;text-transform:uppercase;}}
</style></head><body>
<h1>{company.name}</h1>
<h2>Recruitment Report — {month_label}</h2>
<p>Generated on {now.strftime('%d %B %Y, %I:%M %p IST')}</p>
<div class='summary'>
  <div class='stat'><div class='stat-val'>{total}</div><div class='stat-lbl'>Applications</div></div>
  <div class='stat'><div class='stat-val'>{shortlisted}</div><div class='stat-lbl'>Shortlisted</div></div>
  <div class='stat'><div class='stat-val'>{offered}</div><div class='stat-lbl'>Offered</div></div>
  <div class='stat'><div class='stat-val'>{rejected}</div><div class='stat-lbl'>Rejected</div></div>
</div>
<table><thead><tr><th>Student</th><th>Roll No.</th><th>Position</th><th>Status</th><th>Applied On</th></tr></thead>
<tbody>{rows_html if rows_html else "<tr><td colspan='5' style='text-align:center;color:#94a3b8'>No applications this month.</td></tr>"}</tbody>
</table></body></html>"""

            # Save to disk
            reports_dir = os.path.join(_instance_dir(), "reports")
            os.makedirs(reports_dir, exist_ok=True)
            fname = f"company_{company.id}_report_{first_of_prev_month.strftime('%Y_%m')}.html"
            with open(os.path.join(reports_dir, fname), "w", encoding="utf-8") as f:
                f.write(html)

            # Email to company user
            if _mail_ready(app):
                try:
                    from flask_mail import Message
                    from .database import mail
                    u = User.query.get(company.user_id)
                    if u and u.email:
                        mail.send(Message(
                            subject=f"{company.name} – Monthly Recruitment Report ({month_label})",
                            recipients=[u.email],
                            html=html,
                        ))
                        log.info("[CO-REPORT] Emailed to %s", u.email)
                        sent_count += 1
                except Exception as e:
                    log.error("[CO-REPORT] Failed for %s: %s", company.name, e)

        log.info("[CO-REPORT] Sent %d company reports.", sent_count)
        return {"companies_reported": sent_count, "month": month_label}


# ── Task 3: Student CSV Export (User-triggered) ────────────────────────────────

@celery_app.task(name="backend.tasks.export_student_csv", bind=True)
def export_student_csv(self, student_id: int):
    """
    Export a student's full application history to a CSV file in
    instance/exports/ and store the path as an in-app notification.
    """
    app = _get_app()
    with app.app_context():
        from .models import Student, Application, JobPosition, Company, Notification
        from .database import db

        student = Student.query.get(student_id)
        if not student:
            return {"error": "Student not found"}

        applications = Application.query.filter_by(student_id=student_id).all()

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "Application ID", "Job Title", "Company", "Salary",
            "Applied On", "Status", "Feedback", "Interview Date"
        ])
        for a in applications:
            job = JobPosition.query.get(a.job_id)
            company = Company.query.get(job.company_id) if job else None
            writer.writerow([
                a.id,
                job.title if job else "N/A",
                company.name if company else "N/A",
                job.salary if job else "N/A",
                a.applied_at.strftime("%Y-%m-%d") if a.applied_at else "",
                a.status,
                a.feedback or "",
                a.interview_date.strftime("%Y-%m-%d %H:%M") if a.interview_date else "",
            ])

        exports_dir = os.path.join(_instance_dir(), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"student_{student_id}_applications_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(exports_dir, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(buf.getvalue())

        # In-app notification
        notif = Notification(
            user_id=student.user_id,
            message=f"Your application history export is ready. File: {filename}",
        )
        db.session.add(notif)
        db.session.commit()

        # Email Dispatch if SMTP is configured
        if _mail_ready(app):
            try:
                from flask_mail import Message
                from .database import mail
                from .models import User
                u = User.query.get(student.user_id)
                if u and u.email:
                    email_msg = Message(
                        subject="Your Job Applications Export Ready",
                        recipients=[u.email],
                        body=(
                            f"Hello {student.full_name},\n\n"
                            "Your requested application history csv export is now complete.\n"
                            f"Filename: {filename}\n"
                            f"Download URL: http://127.0.0.1:5000/api/jobs/exports/{filename}\n\n"
                            "Best regards,\nPlacement Portal Team"
                        )
                    )
                    email_msg.attach(filename, "text/csv", buf.getvalue())
                    mail.send(email_msg)
                    log.info("[EXPORT] Send email export success to %s", u.email)
            except Exception as e:
                log.error("[EXPORT] Failed to send email to %s: %s", student.full_name, str(e))

        log.info("[EXPORT] Student CSV: %s", filepath)
        return {"status": "done", "file": filename, "rows": len(applications)}


# ── Task 4: Company CSV Export (User-triggered) ────────────────────────────────

@celery_app.task(name="backend.tasks.export_company_csv", bind=True)
def export_company_csv(self, company_id: int):
    """
    Export a company's complete applicant data to CSV in instance/exports/
    and store filepath as an in-app notification.
    """
    app = _get_app()
    with app.app_context():
        from .models import Company, JobPosition, Application, Student, Notification
        from .database import db

        company = Company.query.get(company_id)
        if not company:
            return {"error": "Company not found"}

        job_ids = [j.id for j in company.job_positions]
        applications = (
            Application.query.filter(Application.job_id.in_(job_ids)).all()
            if job_ids else []
        )

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "Application ID", "Student Name", "Roll No.", "Branch", "CGPA",
            "Job Title", "Applied On", "Status", "Feedback", "Interview Date"
        ])
        for a in applications:
            student = Student.query.get(a.student_id)
            job = JobPosition.query.get(a.job_id)
            writer.writerow([
                a.id,
                student.full_name if student else "N/A",
                student.roll_number if student else "N/A",
                student.branch if student else "N/A",
                student.cgpa if student else "N/A",
                job.title if job else "N/A",
                a.applied_at.strftime("%Y-%m-%d") if a.applied_at else "",
                a.status,
                a.feedback or "",
                a.interview_date.strftime("%Y-%m-%d %H:%M") if a.interview_date else "",
            ])

        exports_dir = os.path.join(_instance_dir(), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        filename = f"company_{company_id}_applicants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(exports_dir, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(buf.getvalue())

        # In-app notification for company user
        notif = Notification(
            user_id=company.user_id,
            message=f"Your applicant data export is ready. File: {filename}",
        )
        db.session.add(notif)
        db.session.commit()

        # Email Dispatch if SMTP is configured
        if _mail_ready(app):
            try:
                from flask_mail import Message
                from .database import mail
                from .models import User
                u = User.query.get(company.user_id)
                if u and u.email:
                    email_msg = Message(
                        subject="Your Candidate Applications Export Ready",
                        recipients=[u.email],
                        body=(
                            f"Hello {company.name} Recruiter,\n\n"
                            "Your requested candidate applications history csv export is now complete.\n"
                            f"Filename: {filename}\n"
                            f"Download URL: http://127.0.0.1:5000/api/jobs/exports/{filename}\n\n"
                            "Best regards,\nPlacement Portal Team"
                        )
                    )
                    email_msg.attach(filename, "text/csv", buf.getvalue())
                    mail.send(email_msg)
                    log.info("[EXPORT] Send email export success to %s", u.email)
            except Exception as e:
                log.error("[EXPORT] Failed to send email to %s: %s", company.name, str(e))

        log.info("[EXPORT] Company CSV: %s", filepath)
        return {"status": "done", "file": filename, "rows": len(applications)}
