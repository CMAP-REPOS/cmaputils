"""
This script does the proper logging setup for the 'cmaputils'
project, so that contributors/maintainers can view logs
for any 'compile-time' (commit-time) macros.
"""

# SECTION: External dependencies
import os
import logging
from pathlib import Path

# SECTION: Internal dependencies

# SECTION: Constants
CONTRIBUTORS_DIR_PATH = Path(__file__).parent
LOGGING_DIR_PATH = os.path.join(CONTRIBUTORS_DIR_PATH)

# SECTION: Classes


# SECTION: Functions
def _setup_logging_dirs():
    """
    Creates logging dirs if they don't already exist.
    """
    os.makedirs(LOGGING_DIR_PATH, exist_ok=True)


def setup_logging(logger_name: str, log_level: int):
    """
    Factory function for the creation and setup of logging
    for 'cmaputils' contributors. Sets up directories and
    files for logging commit-time macros.

    Par
    """
