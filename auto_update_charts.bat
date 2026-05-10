@echo off
setlocal

set "REPO_DIR=D:\02_Clone git\01_github\youtube-charts-vn"
set "LOG_FILE=%REPO_DIR%\auto_update_charts.log"

cd /d "%REPO_DIR%"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy/MM/dd"') do set "TODAY=%%i"
set "COMMIT_MESSAGE=update lasted data - %TODAY%"

>> "%LOG_FILE%" echo [%date% %time%] Starting YouTube Charts update

python scripts\update_static_pages.py >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  >> "%LOG_FILE%" echo [%date% %time%] Python update failed
  git add auto_update_charts.log >> "%LOG_FILE%" 2>&1
  git commit -m "%COMMIT_MESSAGE%" >> "%LOG_FILE%" 2>&1
  git push >> "%LOG_FILE%" 2>&1
  exit /b 1
)

git status --short >> "%LOG_FILE%" 2>&1

git add top_songs.html trending.html scripts\update_static_pages.py README.md auto_update_charts.log >> "%LOG_FILE%" 2>&1

git diff --cached --quiet
if not errorlevel 1 (
  >> "%LOG_FILE%" echo [%date% %time%] No chart file changes; committing log only
  git add auto_update_charts.log >> "%LOG_FILE%" 2>&1
)

git diff --cached --quiet
if not errorlevel 1 (
  >> "%LOG_FILE%" echo [%date% %time%] No changes to commit
  exit /b 0
)

git commit -m "%COMMIT_MESSAGE%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  >> "%LOG_FILE%" echo [%date% %time%] Git commit failed
  exit /b 1
)

git push >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
  >> "%LOG_FILE%" echo [%date% %time%] Git push failed
  exit /b 1
)

>> "%LOG_FILE%" echo [%date% %time%] Update, commit, and push completed
git add auto_update_charts.log >> "%LOG_FILE%" 2>&1
git commit -m "%COMMIT_MESSAGE%" >> "%LOG_FILE%" 2>&1
git push >> "%LOG_FILE%" 2>&1
exit /b 0
