# Author: Aaron Rumph
# Date: 08/07/2026
# Description: PowerShell script for contributors to cmaputils to properly set up their environment.

# NOTE:
#     !! This script is a Copilot blind translation of a bash script I wrote by hand.
#     !! I do not know Powershell, and thus, cannot verify that it works correctly and
#     !! that there are no bugs. It seems to work ok for me, but if you encounter errors
#     !! I will not be able to help debug. Instead, would recommend using the known-good
#     !! bash script provided!

Write-Output "WARNING:
This script is a Copilot blind translation of a bash script I wrote by hand. \
I do not know Powershell, and thus, cannot verify that it works correctly and \
that there are no bugs. It seems to work ok for me, but if you encounter errors \
I will not be able to help debug. Instead, would recommend using the known-good \
bash script provided!"

$ErrorActionPreference = "Stop"

Write-Output "Setting up 'cmaputils' development environment"

# SECTION: Constants
$CMAPUTILS_PATH = ""

# SECTION: Helper functions
function Test-Command {
    param([Parameter(Mandatory)][string]$Name)
    return (Get-Command $Name -ErrorAction SilentlyContinue) -ne $null
}

function Find-CensusApiKey {
    <#
        Looks for a valid Census API key in multiple scopes:
        - Process env
        - User env
        - Machine env
        Valid format: exactly 40 alphanumeric characters.
        Returns: key string or empty ("") if not found.
    #>
    $possibleNames = @("CENSUS_API_KEY", "CENSUS_KEY", "API_KEY", "ACS_API_KEY", "ACS_KEY")
    foreach ($name in $possibleNames) {
        $candidates = @()
        # Process env (current PowerShell process)
        $candidates += (Get-Item -Path "Env:$name" -ErrorAction SilentlyContinue).Value
        # User and Machine env
        $candidates += :GetEnvironmentVariable($name, "User")
        $candidates += :GetEnvironmentVariable($name, "Machine")

        foreach ($value in $candidates | Where-Object { $_ }) {
            if ($value -match '^[a-zA-Z0-9]{40}$') {
                return $value
            } else {
                Write-Output "Found $name but value failed regex check (must be 40 alphanumeric): $value"
            }
        }
    }
    return ""
}

# SECTION: Main script logic

# Check git installed
Write-Output "Checking whether git is installed"
$gitInstalled = Test-Command git

if ($gitInstalled) {
    Write-Output "Git installed!"
} else {
    Write-Output "ERROR: Git is not installed!"
    
    $tryGitInstall = Read-Host "Would you like to try to install Git from this script? (y/N)"
    if ($tryGitInstall.ToLower() -notin @("y","yes")) {
        Write-Output "Will not try to install git from this script, please download manually from: https://git-scm.com/install/windows"
        exit 1
    }

    Write-Output "Will try to install Git using winget"
    $wingetInstalled = Test-Command winget
    if (-not $wingetInstalled) {
        $tryWingetInstall = Read-Host "winget is not installed, would you like to install it? (Y/n)"
        if ($tryWingetInstall.ToLower() -in @("n","no")) {
            Write-Output "Not installing winget and exiting script"
            exit 1
        }

        Write-Output "Trying to install winget"
        try {
            $ProgressPreference = 'SilentlyContinue'
            Install-PackageProvider -Name NuGet -Force | Out-Null
            Install-Module -Name Microsoft.WinGet.Client -Force -Repository PSGallery -Scope CurrentUser
            Repair-WinGetPackageManager
            Write-Output "Installed winget!"
        } catch {
            Write-Output "Failed to install winget automatically. Please install it manually."
            exit 1
        }
    }

    Write-Output "Trying to install Git with winget now"
    try { winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements } catch { Write-Output "Attempted winget installation; verifying..." }

    if (-not (Test-Command git)) {
        Write-Output "Git install failed. Please manually install git (preferably with Git Bash included) at: https://git-scm.com/install/windows"
        exit 1
    } else {
        Write-Output "Git install succeeded!"
    }
}

# Check that Python installed
Write-Output "Checking whether Python is installed"
$pythonInstalled = (Test-Command python) -or (Test-Command python3)

if ($pythonInstalled) {
    if (Test-Command python) { Write-Output "Python is properly installed!" }
    else { Write-Output "Python is properly installed (as 'python3')" }
} else {
    Write-Output "WARNING: Python is not installed!"
}

# Check conda/mamba
Write-Output "Checking whether conda or mamba is installed"
$condaInstalled = Test-Command conda
$mambaInstalled = Test-Command mamba

if (-not $condaInstalled -and -not $mambaInstalled -and -not $pythonInstalled) {
    Write-Output "Python, Conda, and Mamba are not installed, please install one of those!"
    exit 1
} else {
    if ($condaInstalled) { Write-Output "Conda is installed" }
    if ($mambaInstalled) { Write-Output "Mamba is installed" }
}

# Now check if uv installed, if not install using pipx
Write-Output "Checking whether uv is installed"
$uvInstalled = Test-Command uv

if (-not $uvInstalled) {
    Write-Output "uv is not currently installed, will try to install it"

    $pipxInstalled = Test-Command pipx
    if (-not $pipxInstalled) {
        Write-Output "Need pipx to install uv, will try to install now"
        if (Test-Command python) { python -m pip install --user pipx }
        elseif (Test-Command python3) { python3 -m pip install --user pipx }
        else { Write-Output "No Python found to install pipx; please install Python first."; exit 1 }

        try { pipx ensurepath } catch { Write-Output "pipx ensurepath failed; continuing" }
    }

    if (-not (Test-Command pipx)) { Write-Output "Could not install pipx, please try installing it yourself"; exit 1 }
    else { Write-Output "pipx installed successfully" }
    
    Write-Output "Installing uv"
    try { pipx install uv } catch { Write-Output "pipx install uv encountered an error; verifying installation..." }

    if (-not (Test-Command uv)) { Write-Output "uv install failed. Please install manually"; exit 1 }
    else { Write-Output "uv install succeeded" }
} else {
    Write-Output "uv is installed already!"
}

# Check if cmaputils already cloned
Write-Output "Checking to find your cmaputils location"

$homeRoot = $HOME
$excludePatterns = @(
    [IO.Path]::Combine($homeRoot, "AppData"),
    [IO.Path]::Combine($homeRoot, "ProgramData")
)

$searchMatches = @()
try {
    Get-ChildItem -Path $homeRoot -Directory -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $full = $_.FullName
            ($excludePatterns | ForEach-Object { $full -like "$_*" }) -notcontains $true
        } |
        Where-Object { $_.FullName -match 'cmaputils[\\/]+src[\\/]+cmaputils$' } |
        ForEach-Object { $searchMatches += $_ }
} catch {
    Write-Output "Directory traversal encountered an error: $_"
}

$numberMatches = $searchMatches.Count

if ($numberMatches -eq 1) {
    Write-Output "Great, you already have cmaputils downloaded!"
    $srcCmaputilsDir = $searchMatches[0].FullName
    $parent1 = Split-Path -Path $srcCmaputilsDir -Parent
    $parent2 = Split-Path -Path $parent1 -Parent
    $CMAPUTILS_PATH = $parent2
} elseif ($numberMatches -eq 0) {
    $cloneCmaputils = Read-Host "It appears you do not yet have 'cmaputils' source code, would you like to clone it from GitHub? (Y/n)"
    if ($cloneCmaputils.ToLower() -in @("n","no")) { Write-Output "Will not clone, exiting script"; exit 1 }

    $pathToCloneTo = Read-Host "Please enter path where you would like to clone cmaputils (excluding 'cmaputils' in path)"
    if (-not (Test-Path $pathToCloneTo)) { try { New-Item -ItemType Directory -Path $pathToCloneTo | Out-Null } catch { Write-Output "Could not create the directory $pathToCloneTo"; exit 1 } }

    $ghRepoCloneSucceeded = $false
    if (Test-Command gh) {
        Write-Output "GitHub CLI is installed. Will clone using 'gh'"
        gh repo clone CMAP-REPOS/cmaputils (Join-Path $pathToCloneTo "cmaputils")
        if ($LASTEXITCODE -eq 0) { Write-Output "cmaputils cloned successfully"; $ghRepoCloneSucceeded = $true }
        else { Write-Output "'gh repo clone' failed. Will try to use git" }
    }

    if (-not $ghRepoCloneSucceeded) {
        git clone https://github.com/CMAP-REPOS/cmaputils.git (Join-Path $pathToCloneTo "cmaputils")
        if ($LASTEXITCODE -ne 0) {
            Write-Output "Git clone of cmaputils failed; you may not have setup GitHub properly yet!
See the following for info on setting up GitHub access: https://carinadocs.stanford.edu/carina-resources/connect-carina/clone-github"
            exit 1
        } else { Write-Output "cmaputils cloned successfully" }
    }
    $CMAPUTILS_PATH = Join-Path $pathToCloneTo "cmaputils"
} else {
    Write-Output "You appear to have multiple cmaputils locations! Please delete one before running this script again!"
    exit 1
}

Write-Output "cmaputils path: $CMAPUTILS_PATH"

# Syncing env using uv
Set-Location $CMAPUTILS_PATH

$uvVenvPath = Join-Path $CMAPUTILS_PATH ".venv"
$uvVenvActivateBash = Join-Path $uvVenvPath "Scripts/activate"
$uvVenvActivateBat  = Join-Path $uvVenvPath "Scripts/activate.bat"
$uvVenvActivatePwsh = Join-Path $uvVenvPath "Scripts/activate.ps1"

Write-Output "Syncing dev environment using uv"
uv sync --all-groups
if ($LASTEXITCODE -eq 0) {
    Write-Output "Venv set up correctly at: $uvVenvPath"
    Write-Output "You can activate that environment with the following:`n`\
        Bash: $uvVenvActivateBash`n`\
        Command Prompt: $uvVenvActivateBat`n`\
        PowerShell: $uvVenvActivatePwsh"
} else {
    Write-Output "uv sync failed! Try running manually or with 'uv sync --all-groups --locked'"
}

# Installing pre-commit hooks to git hooks
Write-Output "Installing pre-commit hook for FIPS codes"
uv run pre-commit --version | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Output "'pre-commit' was installed correctly by uv" }
else { Write-Output "uv failed to install 'pre-commit!'" }

uv run pre-commit install | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Output "Hooks installed successfully!" }

# Check for API Keys files
Write-Output "Checking for Census API keys for FIPS updating!"

$CONTRIBUTOR_API_KEYS_PATH = Join-Path $CMAPUTILS_PATH "contributors/api_keys.env"

if (Test-Path $CONTRIBUTOR_API_KEYS_PATH) {
    Write-Output "Found 'api_keys.env' in proper location at $CONTRIBUTOR_API_KEYS_PATH"
} else {
    Write-Output "You do not have an existing 'api_keys.env' in the proper location at $CONTRIBUTOR_API_KEYS_PATH"
    $searchForKeys = Read-Host "Would you like this script to search for API keys/env variables to try to fill it in automatically? None of your information will be saved or shared in any way (Y/n)"
    if ($searchForKeys.ToLower() -in @("n","no")) {
        Write-Output "Ok will not look for API keys, but please create file at $CONTRIBUTOR_API_KEYS_PATH with CENSUS_API_KEY=your_api_key!"
        Write-Output "Setup completed without API key file."
        exit 2
    } else {
        Write-Output "Searching for a valid Census API key..."
        $CENSUS_API_KEY = Find-CensusApiKey
        if (-not $CENSUS_API_KEY) {
            Write-Output "Could not find a valid Census API key."
            $manual = Read-Host "Paste your Census API key now (or press Enter to skip)"
            if ($manual -and ($manual -match '^[a-zA-Z0-9]{40}$')) {
                "CENSUS_API_KEY=$manual" | Out-File -FilePath $CONTRIBUTOR_API_KEYS_PATH -Encoding utf8
                Write-Output "Valid API key provided. Wrote to $CONTRIBUTOR_API_KEYS_PATH"
                $preview = Read-Host "Would you like to preview your contributors/api_keys.env file? (y/N)"
                if ($preview.ToLower() -in @("y","yes")) { Get-Content -Path $CONTRIBUTOR_API_KEYS_PATH | Write-Output }
            } else {
                Write-Output "No valid key provided. Please manually create: $CONTRIBUTOR_API_KEYS_PATH with:"
                Write-Output "    CENSUS_API_KEY=your_api_key"
                exit 3
            }
        } else {
            "CENSUS_API_KEY=$CENSUS_API_KEY" | Out-File -FilePath $CONTRIBUTOR_API_KEYS_PATH -Encoding utf8
            Write-Output "Valid API key found!"
            $preview = Read-Host "Would you like to preview your contributors/api_keys.env file? (y/N)"
            if ($preview.ToLower() -in @("y","yes")) { Get-Content -Path $CONTRIBUTOR_API_KEYS_PATH | Write-Output }
        }
    }
}

Write-Output "Development environment for cmaputils fully setup!"
Write-Output "Script succeeded (exit code 0)"
exit 0
