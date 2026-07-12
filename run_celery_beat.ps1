# run_celery_beat.ps1
# Run from project root: .\run_celery_beat.ps1
# Starts the Celery Beat scheduler (triggers scheduled tasks)
Write-Host "[Celery Beat] Starting scheduler..." -ForegroundColor Green
celery -A backend.celery_app:celery_app beat --loglevel=info
