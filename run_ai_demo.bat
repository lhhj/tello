@echo off
echo Starting AI Tello Controller Demo...
echo.
echo This demo shows AI drone control concepts without requiring
echo heavy ML dependencies like PyTorch or Transformers.
echo.
echo Features demonstrated:
echo - Natural language command parsing
echo - Simulated AI vision analysis
echo - Text-based drone instructions
echo - Real-time video simulation
echo.

call .\.venv\Scripts\activate.bat
python ai_tello_demo.py
pause