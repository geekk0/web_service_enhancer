:: Install FastAPI and Uvicorn
pip install fastapi
pip install uvicorn
pip install pillow

:: Change directory to the folder containing main.py
::cd C:\Users\Gekk0\PycharmProjects\web_service_enhancer\web_service_enhancer
cd %~dp0

:: Run your FastAPI application with Uvicorn
start cmd /k "uvicorn main:app --reload --host 0.0.0.0 --port 8000"