@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ================================================================
REM AI WARNING / DISCLOSURE
REM ================================================================
echo WARNING:
echo This script is a Copilot blind translation of a bash script I wrote by hand.
echo I do not know CMD at all. Thus I cannot fully verify that it
echo works correctly and that there are no bugs. It seems to work ok for me, but if
echo you encounter errors I will not be able to help debug. Instead, would recommend
echo using the known-good bash script provided!
echo.

echo Setting up 'cmaputils' development environment

REM SECTION: Constants
set "CMAPUTILS_PATH="

REM ================================================================
REM Helper: Find Census API key from environment variables (exactly 40 alphanumerics)
REM - Checks Process (%CENSUS_API_KEY%), User, and Machine scopes via PowerShell
REM ================================================================
:FindCensusApiKey
set "CENSUS_API_KEY="
for %%N in (CENSUS_API_KEY CENSUS_KEY API_KEY ACS_API_KEY ACS_KEY) do (
    rem Process scope
    call set "env_var_value=%%%N%%"
    if defined env_var_value (
        set "TMP_VAL=!env_var_value!"
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "if ($env:TMP_VAL -match '^[a-zA-Z0-9]{40}$') { exit 0 } else { exit 1 }"
        if not errorlevel 1 (
            set "CENSUS_API_KEY=!env_var_value!"
            goto :FindCensusApiKeyDone
        ) else (
            echo Found %%N but value failed regex check (must be 40 alphanumeric): !env_var_value!
        )
    )

    rem User scope
    for /f "usebackq delims=" %%V in (`powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$v=:GetEnvironmentVariable('%%N','User'); if($v){Write-Output $v}"`) do (
        set "TMP_VAL=%%V"
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "if ($env:TMP_VAL -match '^[a-zA-Z0-9]{40}$') { exit 0 } else { exit 1 }"
        if not errorlevel 1 (
            set "CENSUS_API_KEY=%%V"
            goto :FindCensusApiKeyDone
        ) else (
            echo Found %%N (User scope) but value failed regex check (must be 40 alphanumeric): %%V
        )
    )

    rem Machine scope
    for /f "usebackq delims=" %%V in (`powershell -NoProfile -ExecutionPolicy Bypass -Command ^
        "$v=:GetEnvironmentVariable('%%N','Machine'); if($v){Write-Output $v}"`) do (
        set "TMP_VAL=%%V"
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "if ($env:TMP_VAL -match '^[a-zA-Z0-9]{40}$') { exit 0 } else { exit 1 }"
        if not errorlevel 1 (
            set "CENSUS_API_KEY=%%V"
            goto :FindCensusApiKeyDone
        ) else (
            echo Found %%N (Machine scope) but value failed regex check (must be 40 alphanumeric): %%V
        )
    )
)
:FindCensusApiKeyDone
goto :EOF

REM ================================================================
REM Check git installation
REM ================================================================
echo Checking whether git is installed
where /Q git
if errorlevel 1 (
    echo ERROR: Git is not installed!
    set /p "try_git_install=Would you like to try to install Git from this script? (y/N): "
    if /I not "%try_git_install%"=="y" if /I not "%try_git_install%"=="yes" (
        echo Will not try to install git from this script, please download manually from: https://git-scm.com/install/windows
        exit /b 1
    )

    echo Will try to install Git using winget
    where /Q winget
    if errorlevel 1 (
        set /p "try_winget_install=winget is not installed, would you like to install it? (Y/n): "
        if /I "%try_winget_install%"=="n" (
            echo Not installing winget and exiting script
            exit /b 1
        )
        echo Trying to install winget
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
            "$ProgressPreference='SilentlyContinue';" ^
            "Install-PackageProvider -Name NuGet -Force | Out-Null;" ^
            "Install-Module -Name Microsoft.WinGet.Client -Force -Repository PSGallery -Scope CurrentUser;" ^
            "Repair-WinGetPackageManager"
        if errorlevel 1 (
            echo Failed to install winget automatically. Please install it manually.
            exit /b 1
        )
        echo Installed winget!
    )

    echo Trying to install Git with winget now
    winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        where /Q git
        if errorlevel 1 (
            echo Git install failed. Please manually install git (preferably with Git Bash included) at: https://git-scm.com/install/windows
            exit /b 1
        )
    )
    echo Git install succeeded!
) else (
    echo Git installed!
)

REM ================================================================
REM Check Python installation
REM ================================================================
echo Checking whether Python is installed
set "python_cmd="
where /Q python && set "python_cmd=python"
if not defined python_cmd (
    where /Q python3 && set "python_cmd=python3"
)

if defined python_cmd (
    if /I "%python_cmd%"=="python" (
        echo Python is properly installed!
    ) else (
        echo Python is properly installed (as 'python3')
    )
) else (
    echo WARNING: Python is not installed!
)

REM ================================================================
REM Check conda/mamba
REM ================================================================
echo Checking whether conda or mamba is installed
set "conda_installed="
set "mamba_installed="
where /Q conda && set "conda_installed=1"
where /Q mamba && set "mamba_installed=1"

if not defined conda_installed if not defined mamba_installed if not defined python_cmd (
    echo Python, Conda, and Mamba are not installed, please install one of those!
    exit /b 1
) else (
    if defined conda_installed echo Conda is installed
    if defined mamba_installed echo Mamba is installed
)

REM ================================================================
REM Install uv if needed (via pipx)
REM ================================================================
echo Checking whether uv is installed
where /Q uv
if errorlevel 1 (
    echo uv is not currently installed, will try to install it

    where /Q pipx
    if errorlevel 1 (
        echo Need pipx to install uv, will try to install now
        if defined python_cmd (
            %python_cmd% -m pip install --user pipx
        ) else (
            echo No Python found to install pipx; please install Python first.
            exit /b 1
        )
        pipx ensurepath
    )

    where /Q pipx
    if errorlevel 1 (
        echo Could not install pipx, please try installing it yourself
        exit /b 1
    ) else (
        echo pipx installed successfully
    )

    echo Installing uv
    pipx install uv
    if errorlevel 1 (
        echo pipx install uv encountered an error; verifying installation...
    )

    where /Q uv
    if errorlevel 1 (
        echo uv install failed. Please install manually
        exit /b 1
    ) else (
        echo uv install succeeded
    )
) else (
    echo uv is installed already!
)

REM ================================================================
REM Locate cmaputils repo: look for "*\cmaputils\src\cmaputils" using PowerShell
REM ================================================================
echo Checking to find your cmaputils location

set "SEARCH_STATUS="
for /f "usebackq delims=" %%O in (`powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$home=$env:USERPROFILE;" ^
    "$items=Get-ChildItem -Path $home -Directory -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'cmaputils[\\/]+src[\\/]+cmaputils$' };" ^
    "$count=$items.Count;" ^
    "if ($count -eq 1) { $repo=Split-Path (Split-Path $items[0].FullName -Parent) -Parent; Write-Output ('FOUND|' + $repo) }" ^
    "elseif ($count -eq 0) { Write-Output 'NOTFOUND' }" ^
    "else { Write-Output 'MULTIPLE' }"`
) do set "SEARCH_STATUS=%%O"

if /I "%SEARCH_STATUS%"=="NOTFOUND" (
    set /p "clone_cmaputils=It appears you do not yet have 'cmaputils' source code, would you like to clone it from GitHub? (Y/n): "
    if /I "%clone_cmaputils%"=="n" (
        echo Will not clone, exiting script
        exit /b 1
    )

    set "path_to_clone_to="
    set /p "path_to_clone_to=Please enter path where you would like to clone cmaputils (excluding 'cmaputils' in path): "
    if not defined path_to_clone_to (
        echo No path provided; exiting.
        exit /b 1
    )
    if not exist "%path_to_clone_to%" (
        mkdir "%path_to_clone_to%" || ( echo Could not create the directory "%path_to_clone_to%" & exit /b 1 )
    )

    set "gh_repo_clone_succeeded="
    where /Q gh
    if not errorlevel 1 (
        echo GitHub CLI is installed. Will clone using 'gh'
        gh repo clone CMAP-REPOS/cmaputils "%path_to_clone_to%\cmaputils"
        if not errorlevel 1 (
            echo cmaputils cloned successfully
            set "gh_repo_clone_succeeded=1"
        ) else (
            echo 'gh repo clone' failed. Will try to use git
        )
    )

    if not defined gh_repo_clone_succeeded (
        git clone https://github.com/CMAP-REPOS/cmaputils.git "%path_to_clone_to%\cmaputils"
        if errorlevel 1 (
            echo Git clone of cmaputils failed; you may not have setup GitHub properly yet!
            echo See the following for info on setting up GitHub access: https://carinadocs.stanford.edu/carina-resources/connect-carina/clone-github
            exit /b 1
        ) else (
            echo cmaputils cloned successfully
        )
    )
    set "CMAPUTILS_PATH=%path_to_clone_to%\cmaputils"
) else if /I "%SEARCH_STATUS%"=="MULTIPLE" (
    echo You appear to have multiple cmaputils locations! Please delete one before running this script again!
    exit /b 1
) else (
    for /f "tokens=1* delims=|" %%A in ("%SEARCH_STATUS%") do (
        if /I "%%A"=="FOUND" (
            set "CMAPUTILS_PATH=%%B"
            echo Great, you already have cmaputils downloaded!
        )
    )
)

echo cmaputils path: %CMAPUTILS_PATH%

REM ================================================================
REM Syncing env using uv
REM ================================================================
pushd "%CMAPUTILS_PATH%" || ( echo Failed to change directory to "%CMAPUTILS_PATH%" & exit /b 1 )

set "uv_venv_path=%CMAPUTILS_PATH%\.venv"
set "uv_venv_activate_bash=%uv_venv_path%\Scripts\activate"
set "uv_venv_activate_bat=%uv_venv_path%\Scripts\activate.bat"
set "uv_venv_activate_pwsh=%uv_venv_path%\Scripts\activate.ps1"

echo Syncing dev environment using uv
uv sync --all-groups
if errorlevel 1 (
    echo uv sync failed! Try running manually or with "uv sync --all-groups --locked"
) else (
    echo Venv set up correctly at: %uv_venv_path%
    echo You can activate that environment with the following:
    echo   Bash:       %uv_venv_activate_bash%
    echo   Cmd (BAT):  %uv_venv_activate_bat%
    echo   PowerShell: %uv_venv_activate_pwsh%
)

REM ================================================================
REM Installing pre-commit hooks
REM ================================================================
echo Installing pre-commit hook for FIPS codes
uv run pre-commit --version >nul 2>&1
if errorlevel 1 (
    echo uv failed to install 'pre-commit!'
) else (
    echo 'pre-commit' was installed correctly by uv
)

uv run pre-commit install >nul 2>&1
if not errorlevel 1 (
    echo Hooks installed successfully!
)

REM ================================================================
REM Check for API Keys file
REM ================================================================
echo Checking for Census API keys for FIPS updating!

set "CONTRIBUTOR_API_KEYS_PATH=%CMAPUTILS_PATH%\contributors\api_keys.env"
if exist "%CONTRIBUTOR_API_KEYS_PATH%" (
    echo Found 'api_keys.env' in proper location at "%CONTRIBUTOR_API_KEYS_PATH%"
) else (
    echo You do not have an existing 'api_keys.env' in the proper location at "%CONTRIBUTOR_API_KEYS_PATH%"
    set /p "search_for_keys=Would you like this script to search for API keys/env variables to try to fill it in automatically? None of your information will be saved or shared in any way (Y/n): "
    if /I "%search_for_keys%"=="n" (
        echo Ok will not look for API keys, but please create file at "%CONTRIBUTOR_API_KEYS_PATH%" with:
        echo   CENSUS_API_KEY=your_api_key
        echo Setup completed without API key file.
        popd
        exit /b 2
    ) else (
        echo Searching for a valid Census API key...
        call :FindCensusApiKey
        if not defined CENSUS_API_KEY (
            echo Could not find a valid Census API key.
            set /p "manual_key=Paste your Census API key now (or press Enter to skip): "
            if not defined manual_key (
                echo No valid key provided. Please manually create "%CONTRIBUTOR_API_KEYS_PATH%" with:
                echo   CENSUS_API_KEY=your_api_key
                popd
                exit /b 3
            ) else (
                set "TMP_VAL=%manual_key%"
                powershell -NoProfile -ExecutionPolicy Bypass -Command ^
                    "if ($env:TMP_VAL -match '^[a-zA-Z0-9]{40}$') { exit 0 } else { exit 1 }"
                if errorlevel 1 (
                    echo Provided key failed regex (must be 40 alphanumeric). Aborting.
                    popd
                    exit /b 3
                )
                >"%CONTRIBUTOR_API_KEYS_PATH%" echo CENSUS_API_KEY=%manual_key%
                if errorlevel 1 (
                    echo Failed to write "%CONTRIBUTOR_API_KEYS_PATH%"
                    popd
                    exit /b 1
                )
                echo Valid API key provided. Wrote to "%CONTRIBUTOR_API_KEYS_PATH%"
                set /p "preview_api_keys=Would you like to preview your contributors/api_keys.env file? (y/N): "
                if /I "%preview_api_keys%"=="y" (
                    type "%CONTRIBUTOR_API_KEYS_PATH%"
                )
            )
        ) else (
            >"%CONTRIBUTOR_API_KEYS_PATH%" echo CENSUS_API_KEY=%CENSUS_API_KEY%
            if errorlevel 1 (
                echo Failed to write "%CONTRIBUTOR_API_KEYS_PATH%"
                popd
                exit /b 1
            )
            echo Valid API key found!
            set /p "preview_api_keys=Would you like to preview your contributors/api_keys.env file? (y/N): "
            if /I "%preview_api_keys%"=="y" (
                type "%CONTRIBUTOR_API_KEYS_PATH%"
            )
        )
    )
)

echo Development environment for cmaputils fully setup!
echo Script succeeded (exit code 0)
popd
exit /b 0
