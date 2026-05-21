"""
This module contains functions/tools for managing and working with Census API keys # TODO: ADD documentation.
"""

"""
Author: Aaron Rumph
Date: 05/20/2026
Description: Module containing the source code for API key functions/tools as part of the Modeling Procedures and Maintenance project
Input Files: N/A
Output Files: N/A
"""

# - External dependencies
import os
import logging

# - Internal dependencies

# - Constants

# - Classes

# - Functions


def _cache_and_return_api_key(api_key: str) -> str:
    """
    Helper function: if API_KEY environ variable is not already set, sets it, logs that api_key was loaded successfully, and then returns key
    """
    if os.environ.get("API_KEY") is None:
        os.environ["API_KEY"] = api_key
    logging.debug("Succesfully loaded api_key")
    return api_key


def load_census_api_key(key: str | None = None, env_path: str | None = None) -> str:
    """
    Function to load a Census API Key. Can take
    either the path to a .env file containing API_KEY
    or CENSUS_API_KEY variable or the actual Census API key itself as arguments

    :param key: The user's Census API key.
    :type key: str or None, optional
    :param env_path: Path to a .env file. File must contain one of: CENSUS_API_KEY or API_KEY
    :type env_path: str or None, optional
    """

    # check whether key passed as argument, and type checking
    if (
        isinstance(key, str) and key is not None
    ):  # Q: Should I add key validation logic?
        return _cache_and_return_api_key(key)

    # check for environent variable
    env_api_key = os.getenv("API_KEY")
    if env_api_key is not None:
        return _cache_and_return_api_key(env_api_key)

    # TODO: if key arg passed that conflicts with env variable logic

    # TODO: implement .env file logic for Census API Key
