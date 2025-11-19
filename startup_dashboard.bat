# startup_dashboard.bat
@echo off
cd /d "E:\Smart\Smart-Traffic-Optimizer\Smart-Traffic-Optimizer"
echo Starting Smart Traffic Optimizer Dashboard...
.\ids_env\Scripts\activate
python progress_tracker.py
pause
