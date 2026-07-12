# run_celery_worker.ps1
# Run from project root: .\run_celery_worker.ps1
# Starts the Celery worker (processes tasks)
Write-Host "[Celery] Starting worker..." -ForegroundColor Cyan
celery -A backend.celery_app:celery_app worker --loglevel=info --pool=solo
