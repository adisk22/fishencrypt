@echo off
REM Simple startup script for Fish KMS Server (Windows)

echo Starting Fish KMS Server...
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

