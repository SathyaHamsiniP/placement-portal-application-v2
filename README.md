# Placement Portal Application (PPA) V2

A comprehensive campus recruitment management system designed to streamline the interaction between **Educational Institutes (Admin)**, **Recruiting Companies**, and **Students**.

## Key Features

### Admin (Placement Cell)
*   **Approval Workflow:** Review and approve company registrations and placement drives.
*   **User Management:** Search, manage, and blacklist/deactivate students or companies.
*   **System Analytics:** View dashboard statistics on total registrations and recruitment success.
*   **Reporting:** Automatic generation of monthly placement activity reports (PDF/HTML).

### Company
*   **Profile Management:** Register and maintain a verifiable company profile.
*   **Placement Drives:** Create recruitment events (post-approval) with specific eligibility criteria.
*   **Applicant Tracking:** View student applications, shortlist candidates, and update selection results.

### Student
*   **Personal Dashboard:** Browse all approved placement drives tailored to eligibility.
*   **Application System:** Apply for drives, track status in real-time, and download history.
*   **Profile Building:** Update academic details and upload professional resumes.

---

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Flask (Python) |
| **Frontend** | VueJS + Bootstrap |
| **Database** | SQLite |
| **Caching** | Redis |
| **Batch Processing** | Celery |
| **Styling** | Vanilla CSS + Bootstrap 5 |

---

## Installation & Setup

### 1. Prerequisites
Ensure you have the following installed:
*   Python 3.9+
*   Node.js & npm
*   Redis Server

### 2. Backend Setup
```bash
# Clone the repository
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (Creates schemas and Admin user)
python init_db.py

# Run the development server
python main.py
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

### 4. Background Tasks (Celery)
In two separate terminals:
```bash
# Start Celery Worker
celery -A main.celery worker --loglevel=info

# Start Celery Beat (for scheduled jobs)
celery -A main.celery beat --loglevel=info
```

---

## Core Background Jobs
*   **Daily Reminders:** Automatic notifications to students regarding upcoming application deadlines.
*   **Monthly Reports:** Automated activity summaries emailed to the Admin on the 1st of every month.
*   **Async Exports:** Students can trigger a CSV export of their application history, processed in the background.

## Security & Performance
*   **RBAC:** Strict Role-Based Access Control using Flask-Security/JWT.
*   **Caching:** Optimized API responses using Redis to reduce database load.
*   **Validation:** Multi-layer validation (Frontend JS + Backend Marshmallow/SQLAlchemy models).

---

© 2026 Institute Recruitment Cell. Built for excellence.
