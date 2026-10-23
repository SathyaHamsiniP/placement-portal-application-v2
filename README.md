# Campus Placement Portal

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
*   Redis Server (see running Redis instructions below)

### 2. Backend Setup
From the project root directory, choose the method matching your terminal type:

#### Option A: Command Prompt (CMD) or Git Bash / macOS / Linux
```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate  # On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Initialize database (Creates schemas and Admin user)
python -m backend.init_db

# (Optional) Seed the database with dummy test data
python -m backend.seed

# Run the development server
python -m backend.main
```

#### Option B: Windows PowerShell (Recommended if Option A has permission/restricted script errors)
```powershell
# Create virtual environment
python -m venv venv

# Install dependencies using the venv pip directly
.\venv\Scripts\pip install -r backend/requirements.txt

# Initialize database using the venv python directly
.\venv\Scripts\python -m backend.init_db

# (Optional) Seed the database with dummy test data
.\venv\Scripts\python -m backend.seed

# Run the development server
.\venv\Scripts\python -m backend.main
```

### 3. Frontend Setup
From the `frontend` folder:
```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

### 4. Background Tasks (Celery)
In two separate terminals, run these commands from the project root directory:

#### Option A: Command Prompt (CMD) or Git Bash / macOS / Linux (venv activated)
```bash
# Start Celery Worker (solo pool is required on native Windows)
celery -A backend.celery_app:celery_app worker --loglevel=info --pool=solo

# Start Celery Beat (for scheduled jobs)
celery -A backend.celery_app:celery_app beat --loglevel=info
```

#### Option B: Windows PowerShell (Forces use of venv without script approval issues)
```powershell
# Start Celery Worker
.\venv\Scripts\celery -A backend.celery_app:celery_app worker --loglevel=info --pool=solo

# Start Celery Beat
.\venv\Scripts\celery -A backend.celery_app:celery_app beat --loglevel=info
```

---

## Running Redis Server

### Windows Native Setup:
Download and run the Redis server installer/portable zip for Windows and verify it runs on default port `6379`.

### WSL Setup (Recommended):
If you are using Windows Subsystem for Linux (WSL), install and run Redis Server with:
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
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

## Automated Testing

The project includes a `pytest`-based test suite covering authentication, validation, and route protection.

### Test File Location
```
backend/tests/test_app.py
```

### Tests Included

| Test | Description | Expected |
| :--- | :--- | :--- |
| `test_home` | API root health check | `200 OK` |
| `test_register` | Valid student registration | `201 Created` |
| `test_short_password` | Password under 6 characters | `400 Bad Request` |
| `test_login` | Valid login returns JWT token | `200 OK + access_token` |
| `test_wrong_password` | Invalid credentials | `401 Unauthorized` |
| `test_dashboard_without_token` | Accessing protected route without JWT | `401 Unauthorized` |

### Running Tests

```bash
# Install pytest (once)
pip install pytest

# Run from project root
pytest backend/tests/test_app.py -v
```

> **Note:** Tests use an isolated in-memory SQLite database and do not affect the production database.

---

