@echo off
REM Setup script for Book Features - PDF Summaries and Personalized Recommendations
REM Run this script from the project root directory

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  Book Store Features Setup - PDF ^& Recommendations            ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if we're in the right directory
if not exist "manage.py" (
    color 4F
    echo ❌ Error: manage.py not found. Please run this script from the Django project root.
    color 07
    pause
    exit /b 1
)

REM Step 1: Create migrations
echo [Step 1] Creating database migrations...
python manage.py makemigrations myapp
if %errorlevel% neq 0 (
    color 4F
    echo ❌ Failed to create migrations
    color 07
    pause
    exit /b 1
)
color 2F
echo ✓ Migrations created successfully
color 07
echo.

REM Step 2: Apply migrations
echo [Step 2] Applying database migrations...
python manage.py migrate myapp
if %errorlevel% neq 0 (
    color 4F
    echo ❌ Failed to apply migrations
    color 07
    pause
    exit /b 1
)
color 2F
echo ✓ Migrations applied successfully
color 07
echo.

REM Step 3: Create directories
echo [Step 3] Creating required directories...
if not exist "media\book_summaries" (
    mkdir media\book_summaries
    echo ✓ Directories created
) else (
    echo ✓ Directories already exist
)
echo.

REM Step 4: Collect static files
echo [Step 4] Collecting static files (optional)...
python manage.py collectstatic --noinput >nul 2>&1
echo ✓ Static files collected
echo.

REM Success message
color 2F
echo ╔════════════════════════════════════════════════════════════════╗
echo ✓ Setup completed successfully!
echo ╚════════════════════════════════════════════════════════════════╝
color 07
echo.

echo Next steps:
echo 1. Go to Django Admin (/admin/)
echo 2. Add PDF summaries to book products
echo 3. Add recommendation tags to books
echo 4. Test the features by completing a purchase
echo.
echo For detailed documentation, see: BOOK_FEATURES_GUIDE.md
echo.

pause
