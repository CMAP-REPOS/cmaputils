#!/usr/bin/env bash

# Author: Aaron Rumph
# Date: 08/07/2026
# Description: Bash script for contributers to cmaputils to run to
#   properly setup their environment.
# Input Files: N/A
# Output Files: N/A

# Commentary:
# - This script assumes that all contributors are using Windows because CMAP does not provide
#       Linux.


set -o pipefail

echo "Setting up 'cmaputils' development environment"

# SECTION: Constants
CMAPUTILS_PATH=""

# SECTION: Helper functions
find_census_api_key() {
    # Function to find adequate Census API key to install in correct place
    # for contributors

    # check env variables first
    possible_api_key_names=("CENSUS_API_KEY" "CENSUS_KEY" "API_KEY" "ACS_API_KEY" "ACS_KEY")
    

    for possible_name in "${possible_api_key_names[@]}"; do
        env_var_value="${!possible_name}"

        if [[ -n "$env_var_value" ]]; then 
            # check valid 40-char Census key
            if [[ "$env_var_value" =~ ^[a-zA-Z0-9]{40}$ ]]; then
                CENSUS_API_KEY="$env_var_value"
                break
            fi

            if [[ "$CENSUS_API_KEY" == "" ]]; then
                echo "No valid Census API key found!"
                return 1
            fi
        fi
    done

    
    echo "$CENSUS_API_KEY"
    return 0
    # TODO: Add .env search code?
}

# SECTION: Main script logic

# Check git installed
echo "Checking whether git is installed"
git_installed=false

if command -v git &>/dev/null; then
    echo "git is installed"
    git_installed=true
else
    echo "ERROR: git is not installed!"
    
    # Will ask user if would like to install git from script (using winget/powershell)
    read -p "Would you like to try to install Git from this script? (y/N): " try_git_install
    if [[ "$try_git_install" != "y" && "$try_git_install" != "yes" ]]; then
        echo $'Will not try to install git from this script, please download manually from: https://git-scm.com/install/windows\n'
        exit 1
    fi

    # Need to install winget if doesn't currently exist on system
    echo "Will try to install Git using winget"
    if ! command -v winget &>/dev/null; then
        read -p "winget is not installed, would you like to install it? (Y/n): " try_winget_install
        if [[ "$try_winget_install" != "n" && "$try_winget_install" != "no" ]]; then
            echo "Trying to install winget"
            powershell -Command - << 'EOF'
                $progressPreference = 'silentlyContinue'
                Install-PackageProvider -Name NuGet -Force | Out-Null
                Install-Module -Name Microsoft.WinGet.Client -Force -Repository PSGallery
                Repair-WinGetPackageManager
EOF

            echo "Installed winget!"
        else 
            echo $'Not installing winget and exiting script\n'
            exit 1
        fi
    fi

    # Now can install git with winget
    echo "Trying to install Git with winget now"

    powershell -Command "winget install --id Git.Git -e --source winget"
    if ! command -v git &>/dev/null; then
        echo $'Git install failed. Please manually install git (preferably with Git Bash included) at: https://git-scm.com/install/windows\n'
        exit 1
    else 
        echo "Git installed succesfully!"
    fi
fi   

# Check that Python installed
echo "Checking whether python is installed"
python_installed=false

if command -v python &>/dev/null; then
    echo "python is installed"
    python_installed=true
elif command -v python3 &>/dev/null; then
    echo "python is installed (as 'python3')"
    python_installed=true
else
    echo "WARNING: Python is not installed!"
fi

# Check conda/mamba/pip
echo "Checking whether conda or mamba is installed"
conda_installed=false
mamba_installed=false

if command -v conda &>/dev/null; then
    echo "Conda is installed"
    conda_installed=true
fi 
if command -v mamba &>/dev/null; then
    echo "Mamba is installed"
    mamba_installed=true
fi

# If no python, conda, or mamba then need to stop
if [[ "$conda_installed" == "false" && "$mamba_installed" == "false" && "$python_installed" == "false" ]]; then
    echo $'Python, Conda, and Mamba are not installed, please install one of those!\n'
    exit 1
fi

# Now check if uv installed, if not install using pipx
echo "Checking whether uv is installed"
uv_installed=false
pipx_installed=false

if ! command -v uv &>/dev/null; then
    echo "uv is not currently installed, will try to install it"

    if ! command -v pipx &>/dev/null; then
        echo "Need pipx to install uv, will try to install now"
        python -m pip install --user pipx
        pipx ensurepath
    fi

    # Check that install succeeded
    if command -v pipx &>/dev/null; then
        echo "pipx installed successfully"
    else
        echo $'Could not install pipx, please try installing it yourself\n'
        exit 1
    fi
    
    echo "Installing uv"
    pipx install uv

    # Check that uv install suceeded
    if command -v uv &>/dev/null; then
        echo "uv installed succesfully!"
    else
        echo $'uv install failed. Please install manually\n'
        exit 1
    fi
else
    echo "uv is installed"
fi

# Check if cmaputils already cloned
echo "Checking to find your cmaputils location"

cmaputils_matches=$(find "$HOME" -type d \
    \( -path "$HOME/AppData" -prune -o -path "$HOME/ProgramData" -prune \) \
    -o -iwholename "*cmaputils/src/cmaputils" -print 2>/dev/null)
number_matches=$(find "$HOME" -type d \
    \( -path "$HOME/AppData" -prune -o -path "$HOME/ProgramData" -prune \) \
    -o -iwholename "*cmaputils/src/cmaputils" -print 2>/dev/null | wc -l)

# check number of matches
if [[ $number_matches -eq 1 ]]; then
    echo "Great, you already have cmaputils downloaded!"
    CMAPUTILS_PATH="${cmaputils_matches%\/src\/cmaputils}"

elif [[ $number_matches -eq 0 ]]; then
    read -p "It appears you do not yet have 'cmaputils' source code, would you like to clone it from GitHub? (Y/n): " clone_cmaputils
    if [[ "$clone_cmaputils" == "no" || "$clone_cmaputils" == "n" ]]; then
        echo $'Will not clone, exiting script\n'
        exit 1
    fi

    # will try to clone using GitHub CLI first (because still private repo)
    gh_repo_clone_succeeded=false
    path_to_clone_to=""
    read -p "Please enter path where you would like to clone cmaputils (excluding cmaputils in path): " path_to_clone_to

    if command -v gh &>/dev/null; then
        echo "GitHub CLI is installed. Will clone using 'gh'"
        if gh repo clone CMAP-REPOS/cmaputils "$path_to_clone_to/cmaputils"; then
            echo "cmaputils cloned successfully"
            gh_repo_clone_succeeded=true
        else
            echo "'gh repo clone' failed. Will try to use git"
        fi
    fi

    # will try to clone using git other wise
    if ! gh_repo_clone_succeeded; then
        if git clone https://github.com/CMAP-REPOS/cmaputils.git "$path_to_clone_to/cmaputils"; then
            echo "cmaputils cloned successfully"
        else
            echo $'Git clone of cmaputils failed, you may not have setup up Github properly yet! See the following for info on setting up Github access: https://carinadocs.stanford.edu/carina-resources/connect-carina/clone-github\n'
            exit 1
        fi
    fi
else
    echo $'You appear to have multiple cmaputils locations! Please delete one before running this script again!\n'
    exit 1
fi

echo "cmaputils path: $CMAPUTILS_PATH"

# Syncing env using uv
cd $CMAPUTILS_PATH

uv_venv_path="$CMAPUTILS_PATH/.venv"
uv_venv_activate_bash="$uv_venv_path/Scripts/activate"
uv_venv_activate_bat="$uv_venv_path/Scripts/activate.bat"
uv_venv_activate_pwsh="$uv_venv_path/Scripts/activate.ps1"

echo "Syncing dev environment using uv"
if uv sync --all-groups &>/dev/null; then
    echo "Venv set up correctly at: $uv_venv_path"
    echo "You can activate that environment with the following:
        Bash: $uv_venv_activate_bash
        Command Prompt: $uv_venv_activate_bat 
        Powershell: $uv_venv_activate_pwsh"
else
    echo "uv sync failed! Try running manually or with 'uv sync --all-groups --locked'"
fi

# Installing pre-commit hooks to git hooks
echo "Installing pre-commit hook for Fips codes"
if uv run pre-commit --version &>/dev/null; then
    echo "'pre-commit' was installed correctly by uv"
else
    echo "uv failed to install 'pre-commit!'"
fi

if uv run pre-commit install &>/dev/null; then
    echo "Hooks installed succesfully!"
fi

# Check for API Keys files
echo "Checking for Census API keys for FIPS updating!"

CONTRIBUTOR_API_KEYS_PATH="$CMAPUTILS_PATH/contributors/api_keys.env"

# the below will be 1 if true, and 0 if false
has_contributors_api_keys_file=$(find "$HOME" -type f \
    \( -path "$HOME/AppData" -prune -o -path "$HOME/ProgramData" -prune \) \
    -o -iwholename "$CONTRIBUTOR_API_KEYS_PATH" -print \
    2>/dev/null | wc -l)

if [[ $has_contributors_api_keys_file -eq 1 ]]; then
    echo "Found 'api_keys.env' in proper location at $CONTRIBUTOR_API_KEYS_PATH"
else
    echo "You do not have an existing 'api_keys.env' in the proper location at $CONTRIBUTOR_API_KEYS_PATH"

    read -p "Would you like this script to search for API keys/env variables to try to fill it in automatically? \
None of your information will be saved or shared in any way (Y/n): " search_for_keys

    if [[ "$search_for_keys" != "no" && "$search_for_keys" != "n" ]]; then
        if CENSUS_API_KEY=$(find_census_api_key); then
            echo "Valid API key found!"
            echo "CENSUS_API_KEY=$CENSUS_API_KEY" > "$CONTRIBUTOR_API_KEYS_PATH"
            read -p "Would you like to preview your contributors/api_keys.env file? (y/N): " preview_api_keys
            if [[ "$preview_api_keys" == "y" || "$preview_api_keys" == "yes" || "$preview_api_keys" == "Y" ]]; then
                cat "$CONTRIBUTOR_API_KEYS_PATH"
            fi
        else

            echo "Could not find a Valid API key, please manually create a api_keys.env file at $CONTRIBUTOR_API_KEYS_PATH \
with CENSUS_API_KEY=your_api_key!"

        fi

    else 
        echo "Ok will not look for API keys, but please create file at $CONTRIBUTOR_API_KEYS_PATH with CENSUS_API_KEY=your_api_key !"
    fi
fi

echo $'Development environment for cmaputils fully setup!\n'

echo "Script succeeded (exit code 0)"
exit 0
