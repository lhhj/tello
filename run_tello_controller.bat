@echo off
echo Starting Tello Drone Controller...
echo.
echo Make sure you are connected to your Tello drone's WiFi network!
echo (Usually named TELLO-XXXXXX)
echo.
pause
echo.
echo Launching application...
C:\Users\leh\source\tello\.venv\Scripts\python.exe tello_controller.py
pause