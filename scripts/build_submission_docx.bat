@echo off
setlocal
cd /d "%~dp0.."
python scripts\build_submission_docx.py
endlocal
