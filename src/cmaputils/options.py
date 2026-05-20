"""
This module contains a number of setup options for cmaputils that can easily be used to configure various behaviors,
such as setting the Census API key or setting the default output directory
"""

"""
Author: Aaron Rumph
Date: 05/20/2026
Description: Module containing configuration/options for cmaputils.
Input Files: N/A
Output Files: N/A
Useful External Documentation: N/A
"""


def set_census_api_key(args):
    """
    Thin wrapper around census.api_key.load_api_key
    """
