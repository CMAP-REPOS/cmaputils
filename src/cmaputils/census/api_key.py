"""
This module contains functions/tools for managing and working with Census API keys # TODO: ADD documentation.
"""

"""
Author: Aaron Rumph
Date: 05/26/2026
Description: Module containing the source code for API key functions/tools as part of the Modeling Procedures and Maintenance project
Input Files: N/A
Output Files: N/A
"""

# - External dependencies
import os
import logging
from pathlib import Path
import re
import dotenv

# - Internal dependencies

# - Constants


# - Exceptions
class ApiKeyException(Exception):
    """Exception raised in case of API key problems"""

    pass


# - Classes

# - Functions


def _cache_census_api_key(api_key: str | None) -> str:
    """
    Helper function: if API_KEY environ variable is not already set, sets it,
    logs that api_key was loaded successfully, and then returns key
    """
    # throws if api_key is None
    if api_key is None:
        raise ApiKeyException(
            "Could not find Census API key in either CENSUS_API_KEY"
            " or API_KEY variables. Please ensure your API key is in either of these two."
        )

    # Census API Key should be 40 letters/numbers (helps disambiguate env var API_KEY)
    if not re.match(pattern=r"[a-zA-Z0-9]{40}", string=api_key):
        raise ApiKeyException(
            "Census API key should be 40 chars long and only contain alphanumerics."
            "Please check that the API key you inputted is for the Census API"
            "and not another (such as CTPP)"
        )

    if os.environ.get("CENSUS_API_KEY") is None:
        os.environ["CENSUS_API_KEY"] = api_key
    logging.debug("Succesfully loaded Census API key")
    return api_key


def load_api_key_census(key: str | None = None, env_path: str | None = None) -> str:
    """
    Function to load a Census API Key. Can take
    either the path to a .env file containing API_KEY
    or CENSUS_API_KEY variable or the actual Census API key itself as arguments

    :param key: The user's Census API key.
    :type key: str or None, optional
    :param env_path: Path to a .env file. File must contain one of: CENSUS_API_KEY or API_KEY
    :type env_path: str or None, optional

    :return: the Census API Key
    :rtype: str
    """

    # check whether key passed as argument, and type checking
    if (
        isinstance(key, str) and key is not None
    ):  # Q: Should I add key validation logic?
        return _cache_census_api_key(key)

    # check for environent variable
    env_census_api_key = os.getenv("CENSUS_API_KEY")
    if env_census_api_key is not None:
        return _cache_census_api_key(env_census_api_key)

    env_api_key = os.getenv("API_KEY")
    if env_api_key is not None:
        return _cache_census_api_key(env_api_key)

    # check for key in provided .env file
    if isinstance(env_path, str) and key is not None:
        # expanduser allows for ~ as home
        _env_path_obj = Path(env_path).expanduser()
        if not _env_path_obj.exists():
            raise FileNotFoundError(f".env file not found at: {env_path}")

        dotenv.load_dotenv(_env_path_obj)
        _env_census_api_key = os.environ.get("CENSUS_API_KEY")
        _env_api_key = os.environ.get("API_KEY")
        api_key = ""  # outer scope decleration for return value

        # CENSUS_API_KEY var prioritized, then API_KEY
        # throws if both ^^ are None or non 40 char alphanumeric
        try:
            api_key = _cache_census_api_key(_env_census_api_key)
        except ApiKeyException:
            api_key = _cache_census_api_key(_env_api_key)

        return api_key

    raise ApiKeyException(
        "Could not find a valid Census API key! Please provide set API_KEY or"
        " CENSUS_API_KEY variable in your environment or in a .env file"
        " (must provide path as argument to this function)"
    )


def _cache_ctpp_api_key(api_key: str | None) -> str:
    """
    Helper function: if API_KEY environ variable is not already set, sets it,
    logs that api_key was loaded successfully, and then returns key
    """
    # throws if api_key is None
    if api_key is None:
        raise ApiKeyException(
            "Could not find CTPP API key in either CTPP_API_KEY"
            " or API_KEY variables. Please ensure your API key is in one of these."
        )

    # Census API Key should be 40 letters/numbers (helps disambiguate env var API_KEY)
    if not re.match(pattern=r"[a-zA-Z0-9]{24}", string=api_key):
        raise ApiKeyException(
            "CTPP API key should be 24 chars long and only contain alphanumerics."
            "Please check that the API key you inputted is for the Census API"
            "and not another (such as a Census API Key)"
        )

    if os.environ.get("CTPP_API_KEY") is None:
        os.environ["CTPP_API_KEY"] = api_key
    logging.debug("Succesfully loaded CTPP API key")
    return api_key


def load_api_key_ctpp(key: str | None = None, env_path: str | None = None) -> str:
    """
    Function to load a CTPP API Key. Can take
    either the path to a .env file containing API_KEY
    or CTPP_API_KEY variable or the actual CTPP API key itself as arguments

    :param key: The user's CTPP API key.
    :type key: str or None, optional
    :param env_path: Path to a .env file. File must contain one of: CTPP_API_KEY or API_KEY
    :type env_path: str or None, optional
    """

    # check whether key passed as argument, and type checking
    if (
        isinstance(key, str) and key is not None
    ):  # Q: Should I add key validation logic?
        return _cache_census_api_key(key)

    # check for environent variable
    env_census_api_key = os.getenv("CTPP_API_KEY")
    if env_census_api_key is not None:
        return _cache_census_api_key(env_census_api_key)

    env_api_key = os.getenv("API_KEY")
    if env_api_key is not None:
        return _cache_census_api_key(env_api_key)

    # check for key in provided .env file
    if isinstance(env_path, str) and key is not None:
        # expanduser allows for ~ as home
        _env_path_obj = Path(env_path).expanduser()
        if not _env_path_obj.exists():
            raise FileNotFoundError(f".env file not found at: {env_path}")

        dotenv.load_dotenv(_env_path_obj)
        _env_census_api_key = os.environ.get("CTPP_API_KEY")
        _env_api_key = os.environ.get("API_KEY")
        api_key = ""  # outer scope decleration for return value

        # CTPP_API_KEY var prioritized, then API_KEY
        # throws if both ^^ are None or non 24 char alphanumeric
        try:
            api_key = _cache_census_api_key(_env_census_api_key)
        except ApiKeyException:
            api_key = _cache_census_api_key(_env_api_key)

        return api_key

    raise ApiKeyException(
        "Could not find a valid Census API key! Please provide set API_KEY or"
        " CTPP_API_KEY variable in your environment or in a .env file"
        " (must provide path as argument to this function)"
    )
