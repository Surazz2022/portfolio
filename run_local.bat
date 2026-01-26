@echo off
echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

echo.
echo Running migrations...
python manage.py migrate

echo.
echo Starting Django development server...
echo.
echo Server will be available at: http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver
