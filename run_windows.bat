@echo off
echo ==========================================
echo Starting EdgeLab (Windows)
echo ==========================================
echo.

echo Initializing database...
cd api
python database.py
cd ..

echo.
echo Starting API server...
start cmd /k "cd api && python app.py"

timeout /t 3 /nobreak > nul

echo.
echo Starting UI server...
start cmd /k "cd ui && streamlit run streamlit_app.py"

echo.
echo ==========================================
echo EdgeLab is starting!
echo.
echo API:  http://localhost:5000
echo UI:   http://localhost:8501
echo.
echo Two windows will open. Keep them running.
echo Press Ctrl+C in each to stop.
echo ==========================================
