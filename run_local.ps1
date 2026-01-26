# PowerShell script to run Django project locally

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& "..\venv\Scripts\Activate.ps1"

Write-Host "`nRunning migrations..." -ForegroundColor Cyan
python manage.py migrate

Write-Host "`nStarting Django development server..." -ForegroundColor Green
Write-Host "`nServer will be available at: http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

python manage.py runserver
