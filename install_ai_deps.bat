@echo off
echo Installing AI Tello Controller Dependencies...
echo.

echo Activating virtual environment...
call .\.venv\Scripts\activate.bat

echo.
echo Installing basic requirements...
pip install requests pillow

echo.
echo Installing AI/ML dependencies (this may take a while)...
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers

echo.
echo Installing optional dependencies...
pip install scikit-image
pip install nltk

echo.
echo Installation complete!
echo.
echo To use the AI features, you'll need a Hugging Face API token.
echo Get one from: https://huggingface.co/settings/tokens
echo Then edit ai_config.py and add your token.
echo.
pause