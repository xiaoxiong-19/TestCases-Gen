@echo off
setlocal EnableExtensions EnableDelayedExpansion

chcp 65001 >nul

set "REPO_URL=https://github.com/xiaoxiong-19/TestCases-Gen.git"
set "REPO_DIR=%~dp0"
set "TARGET_ROOT=%USERPROFILE%\.cursor\skills"

if not "%~1"=="" (
  set "TARGET_ROOT=%~1"
)

echo [INFO] Skill repo: %REPO_DIR%
echo [INFO] Target skills: %TARGET_ROOT%
echo.

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git is not installed or not in PATH.
  goto :fail
)

cd /d "%REPO_DIR%" || (
  echo [ERROR] Failed to enter repo directory.
  goto :fail
)

if not exist ".git" (
  echo [ERROR] Current directory is not a Git repository: %REPO_DIR%
  goto :fail
)

git remote get-url origin >nul 2>nul
if errorlevel 1 (
  echo [INFO] Adding origin: %REPO_URL%
  git remote add origin "%REPO_URL%" || goto :fail
) else (
  for /f "delims=" %%u in ('git remote get-url origin') do set "CURRENT_URL=%%u"
  if /i not "!CURRENT_URL!"=="%REPO_URL%" (
    echo [INFO] Updating origin from !CURRENT_URL! to %REPO_URL%
    git remote set-url origin "%REPO_URL%" || goto :fail
  )
)

for /f "delims=" %%s in ('git status --porcelain') do (
  echo [ERROR] Skill repo has local changes. Please commit, stash, or discard them before updating.
  echo.
  git status --short
  goto :fail
)

for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%b"
if "%BRANCH%"=="HEAD" set "BRANCH=main"

echo [INFO] Fetching origin/%BRANCH% ...
git fetch origin "%BRANCH%" || goto :fail

echo [INFO] Pulling latest changes with --ff-only ...
git pull --ff-only origin "%BRANCH%" || goto :fail

if not exist "%TARGET_ROOT%" (
  echo [INFO] Creating target directory: %TARGET_ROOT%
  mkdir "%TARGET_ROOT%" || goto :fail
)

call :copy_skill "tc-gen" || goto :fail
call :copy_skill "tc-convert" || goto :fail

echo.
echo [OK] Local Cursor skills updated successfully.
echo [OK] Target: %TARGET_ROOT%
goto :done

:copy_skill
set "SKILL_NAME=%~1"
set "SRC=%REPO_DIR%%SKILL_NAME%"
set "DST=%TARGET_ROOT%\%SKILL_NAME%"

if not exist "%SRC%\SKILL.md" (
  echo [WARN] Skip %SKILL_NAME% because SKILL.md was not found: %SRC%
  exit /b 0
)

echo [INFO] Syncing %SKILL_NAME% ...
if not exist "%DST%" mkdir "%DST%" || exit /b 1
robocopy "%SRC%" "%DST%" /E /R:2 /W:1 /XD .git __pycache__ /XF *.pyc >nul

set "ROBOCOPY_EXIT=%ERRORLEVEL%"
if %ROBOCOPY_EXIT% GEQ 8 (
  echo [ERROR] Failed to sync %SKILL_NAME%. Robocopy exit code: %ROBOCOPY_EXIT%
  exit /b %ROBOCOPY_EXIT%
)

exit /b 0

:fail
echo.
echo [FAILED] Update did not complete.
exit /b 1

:done
echo.
pause
exit /b 0
