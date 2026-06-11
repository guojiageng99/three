@echo off
setlocal
cd /d "%~dp0.."
python scripts\build_submission_docx.py
python scripts\extend_group_ppt.py
endlocal
