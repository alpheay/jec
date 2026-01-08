@echo off
setlocal

:: Check for version argument
if "%~1"=="" (
    echo [ERROR] No version argument provided.
    echo Usage: %0 [version]
    echo Example: %0 0.0.4
    exit /b 1
)

set "VERSION=%~1"
set "ROOT=%~dp0.."

echo [INFO] Starting setup for version %VERSION%...

:: 1. Create changelog structure
echo [INFO] Creating changelog directory and file...
if not exist "%ROOT%\changelog\%VERSION%" mkdir "%ROOT%\changelog\%VERSION%"
if not exist "%ROOT%\changelog\%VERSION%\changelog.md" (
    type nul > "%ROOT%\changelog\%VERSION%\changelog.md"
    echo [INFO] Created changelog\%VERSION%\changelog.md
)

:: 2. Create test structure
echo [INFO] Creating test directory and file...
if not exist "%ROOT%\test\%VERSION%" mkdir "%ROOT%\test\%VERSION%"
if not exist "%ROOT%\test\%VERSION%\feat_test.py" (
    type nul > "%ROOT%\test\%VERSION%\feat_test.py"
    echo [INFO] Created test\%VERSION%\feat_test.py
)

:: 3. Move dist content to last version
echo [INFO] Finding last modified version folder...
set "LAST_VERSION="
:: dir /B /AD /O-D lists directories, oldest last? No, /O-D is date (newest first). 
:: No wait, /OD is date (oldest first). /O-D is date (newest first).
:: Default dir sort order is by name if no /O specified.
:: User asked for "last modified subfolder".
:: If I do `dir /O-D`, the FIRST item is the most recently modified.
for /f "delims=" %%i in ('dir "%ROOT%\versions" /B /AD /O-D') do (
    set "LAST_VERSION=%%i"
    goto :FoundLastVersion
)

:FoundLastVersion
if defined LAST_VERSION (
    echo [INFO] Last version found: %LAST_VERSION%
    echo [INFO] Moving dist content to versions\%LAST_VERSION%...
    if exist "%ROOT%\dist\*" (
        move /Y "%ROOT%\dist\*" "%ROOT%\versions\%LAST_VERSION%\"
    ) else (
        echo [INFO] Dist folder is empty, nothing to move.
    )
) else (
    echo [WARN] No previous versions found in versions directory. Skipping move.
)

:: 4. Wait 1 second and create new version folder
echo [INFO] Waiting 1 second...
timeout /t 1 /nobreak >nul

echo [INFO] Creating new version folder versions\%VERSION%...
if not exist "%ROOT%\versions\%VERSION%" (
    mkdir "%ROOT%\versions\%VERSION%"
    echo [INFO] Created versions\%VERSION%
)

:: 5. Update version in pyproject.toml
echo [INFO] Updating version in pyproject.toml...
powershell -Command "(Get-Content '%ROOT%\pyproject.toml') -replace '^version = \".*\"$', 'version = \"%VERSION%\"' | Set-Content '%ROOT%\pyproject.toml'"

echo [INFO] Done.
endlocal
