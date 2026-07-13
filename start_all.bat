@echo off
echo Starting Placement Portal...

start "Flask Backend" cmd /k "cd /d %~dp0 && python -m backend.main"
timeout /t 2 /nobreak >nul

start "Celery Worker" cmd /k "cd /d %~dp0 && celery -A backend.celery_app:celery_app worker --loglevel=info --pool=solo"
timeout /t 2 /nobreak >nul

start "Celery Beat" cmd /k "cd /d %~dp0 && celery -A backend.celery_app:celery_app beat --loglevel=info"
timeout /t 2 /nobreak >nul

start "Vue Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo All services started in separate windows.
