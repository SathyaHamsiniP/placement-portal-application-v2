"""
jobs_api.py
-----------
REST endpoints for triggering and monitoring Celery background jobs.

Routes (all prefixed /api/jobs):
  POST /export/student          – Student triggers their own CSV export
  POST /export/company          – Company triggers their applicant CSV export
  GET  /task/<task_id>          – Poll Celery task status
  POST /trigger/reminders       – Admin manually fires interview reminders
  POST /trigger/monthly-report  – Admin manually fires placement report
  GET  /reports                 – Admin lists generated HTML reports
  GET  /reports/<filename>      – Admin downloads a specific HTML report
  GET  /exports/<filename>      – Student/Company downloads their CSV
"""

import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from .auth import token_required
from .models import Student, Company
from .tasks import (
    export_student_csv,
    export_company_csv,
    send_interview_reminders,
    generate_monthly_placement_report,
)

jobs_bp = Blueprint("jobs", __name__)

_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPORTS_DIR = os.path.join(_BASE, "instance", "exports")
REPORTS_DIR = os.path.join(_BASE, "instance", "reports")


# ── Student: trigger CSV export ────────────────────────────────────────────────

@jobs_bp.route("/export/student", methods=["POST"])
@token_required
def trigger_student_export(current_user):
    if current_user.role != "Student":
        return jsonify({"message": "Unauthorized"}), 403

    student = current_user.student_profile
    if not student:
        return jsonify({"message": "Student profile not found"}), 404

    task = export_student_csv.delay(student.id)
    return jsonify({
        "message": "Export started. You will receive an in-app notification when ready.",
        "task_id": task.id,
    }), 202


# ── Company: trigger CSV export ────────────────────────────────────────────────

@jobs_bp.route("/export/company", methods=["POST"])
@token_required
def trigger_company_export(current_user):
    if current_user.role != "Company":
        return jsonify({"message": "Unauthorized"}), 403

    company = current_user.company_profile
    if not company:
        return jsonify({"message": "Company profile not found"}), 404

    task = export_company_csv.delay(company.id)
    return jsonify({
        "message": "Export started. You will receive an in-app notification when ready.",
        "task_id": task.id,
    }), 202


# ── Poll task status ───────────────────────────────────────────────────────────

@jobs_bp.route("/task/<task_id>", methods=["GET"])
@token_required
def get_task_status(current_user, task_id):
    from .celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "status": result.status,   # PENDING / STARTED / SUCCESS / FAILURE
        "result": result.result if result.successful() else None,
    }
    if result.failed():
        response["error"] = str(result.result)
    return jsonify(response)


# ── Admin: manually trigger reminders ─────────────────────────────────────────

@jobs_bp.route("/trigger/reminders", methods=["POST"])
@token_required
def trigger_reminders(current_user):
    if current_user.role != "Admin":
        return jsonify({"message": "Unauthorized"}), 403
    task = send_interview_reminders.delay()
    return jsonify({"message": "Interview reminder job queued.", "task_id": task.id}), 202


# ── Admin: manually trigger monthly report ────────────────────────────────────

@jobs_bp.route("/trigger/monthly-report", methods=["POST"])
@token_required
def trigger_monthly_report(current_user):
    if current_user.role != "Admin":
        return jsonify({"message": "Unauthorized"}), 403
    task = generate_monthly_placement_report.delay()
    return jsonify({"message": "Monthly placement report job queued.", "task_id": task.id}), 202


# ── Admin: list generated reports ─────────────────────────────────────────────

@jobs_bp.route("/reports", methods=["GET"])
@token_required
def list_reports(current_user):
    if current_user.role != "Admin":
        return jsonify({"message": "Unauthorized"}), 403
    os.makedirs(REPORTS_DIR, exist_ok=True)
    files = sorted(
        [f for f in os.listdir(REPORTS_DIR) if f.endswith(".html")],
        reverse=True,
    )
    return jsonify(files)


# ── Admin: download a specific report ─────────────────────────────────────────

@jobs_bp.route("/reports/<filename>", methods=["GET"])
@token_required
def download_report(current_user, filename):
    if current_user.role != "Admin":
        return jsonify({"message": "Unauthorized"}), 403
    return send_from_directory(REPORTS_DIR, filename)


# ── Student / Company: download their CSV export ──────────────────────────────

@jobs_bp.route("/exports/<filename>", methods=["GET"])
@token_required
def download_export(current_user, filename):
    # Allow only if filename belongs to the requesting user
    allowed = False
    if current_user.role == "Admin":
        allowed = True
    elif current_user.role == "Student":
        s = current_user.student_profile
        allowed = s and filename.startswith(f"student_{s.id}_")
    elif current_user.role == "Company":
        c = current_user.company_profile
        allowed = c and filename.startswith(f"company_{c.id}_")

    if not allowed:
        return jsonify({"message": "Unauthorized"}), 403

    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)
