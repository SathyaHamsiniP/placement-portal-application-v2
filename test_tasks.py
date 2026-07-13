"""
test_tasks.py
-------------
Manually trigger every Celery background task and print results.
Run from project root:
    python test_tasks.py

The Celery worker must be running in another terminal.
Results will also appear in the worker's log.
"""

import sys
import backend.tasks as _tasks_module
# Disable email for this test run — tests job logic & file output only
_tasks_module._mail_ready = lambda app: False

from backend.tasks import (
    send_interview_reminders,
    send_deadline_reminders,
    generate_monthly_placement_report,
    generate_monthly_company_report,
    export_student_csv,
    export_company_csv,
)

SEP = "-" * 60


def run(label, task, *args):
    print(f"\n{SEP}")
    print(f"  RUNNING: {label}")
    print(SEP)
    try:
        result = task.apply(args=args)          # runs synchronously (no broker needed)
        print(f"  RESULT : {result.result}")
    except Exception as e:
        print(f"  ERROR  : {e}")


if __name__ == "__main__":
    print("\n=== Placement Portal — Background Job Test ===")
    print("(Running tasks synchronously inside this process)\n")

    run("Interview Reminders (daily 8 AM)",      send_interview_reminders)
    run("Deadline Reminders (daily 9 AM)",        send_deadline_reminders)
    run("Monthly Admin Placement Report",         generate_monthly_placement_report)
    run("Monthly Company Reports (all companies)",generate_monthly_company_report)
    run("Student CSV Export  [student_id=21]",    export_student_csv, 21)
    run("Company CSV Export  [company_id=1]",     export_company_csv, 1)

    print(f"\n{SEP}")
    print("  All tasks executed.  Check:")
    print("  - instance/reports/   for HTML reports")
    print("  - instance/exports/   for CSV files")
    print("  - Celery worker log   for email dispatch details")
    print(SEP)
