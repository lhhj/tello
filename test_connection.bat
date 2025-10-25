@echo off
echo Tello Drone Connection Test
echo ===========================
echo.
echo Make sure you are connected to your Tello drone's WiFi network!
echo (Usually named TELLO-XXXXXX)
echo.
echo Choose test type:
echo 1. Full connection test (recommended)
echo 2. Quick battery check
echo 3. Basic commands test
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Running full connection test...
    C:\Users\leh\source\tello\.venv\Scripts\python.exe test_connection.py
) else if "%choice%"=="2" (
    echo.
    echo Checking battery level...
    C:\Users\leh\source\tello\.venv\Scripts\python.exe test_connection.py battery
) else if "%choice%"=="3" (
    echo.
    echo Testing basic commands...
    C:\Users\leh\source\tello\.venv\Scripts\python.exe test_connection.py commands
) else (
    echo Invalid choice. Running full test...
    C:\Users\leh\source\tello\.venv\Scripts\python.exe test_connection.py
)

echo.
pause