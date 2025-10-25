@echo off
echo Starting AI Tello Controller with StreamVLM...
echo.
echo Make sure you have:
echo 1. Connected to Tello WiFi network
echo 2. Hugging Face API token (optional but recommended)
echo 3. Internet connection for AI analysis
echo.

call .\.venv\Scripts\activate.bat
python ai_tello_controller.py
pause