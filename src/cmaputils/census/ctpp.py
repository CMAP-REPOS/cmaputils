"""
This module contains functions for interfacing with CTPP API # TODO: ADD documentation.
"""

"""
Author: Aaron Rumph
Date: 05/20/2026
Description: Module containing the source code for CTPP Census API functions/tools as part of the Modeling Procedures and Maintenance project.
Input Files: N/A
Output Files: N/A
"""

# - External dependencies
import requests
import logging

# - Internal dependencies
from api_key import load_census_api_key

# - Constants
CTPP_BASE_URL = "https://ctppdata.transportation.org/api"
DATASET_ENDPOINT = f"{CTPP_BASE_URL}/datasets"
GROUP_ENDPOINT = f"{CTPP_BASE_URL}/groups"
DATA_ENDPOINT = f"{CTPP_BASE_URL}/data"

CTPP_SUMMARY_LEVELS = [
    "Nation",
    "State",
    "State-County",
    "State-County-MCD",
    "State-Place",
    "State-PUMA5",
    "MSA",
    "MSA-Principal-Cities",
    "State-County-Tract",
    "TAD",
    "TAZ",
]

CTPP_AVAILABLE_YEARS = [2000, 2010, 2016, 2021]


# TODO: other helpful constants?

# - Functions


# AR: be warned, there are lots and lots of helper functions here in order
# to keep the code modular and the logic easier to work with
# (and fix if the API changes)

# NOTE: not supporting the "Accept parameter for any query because I assume
# there is no point in changing query from json (default) to xml


def _sanitize_params(params: dict) -> dict | None:
    """
    Helper function: cleans up params dictionary, removing any None key-value
    pairs and returning None if no params
    """
    _params = {key: value for key, value in params.items() if value != ""}
    return _params


def _datasets_base_param_builder(
    size: int | None = None, page: int | None = None
) -> dict:
    """Helper function: builds params dictionary for the /datasets endpoint."""

    # page and size must be between 0 and 4 as there are only 4 products
    if (size <= 0 or size > 4) and size is not None:
        raise ValueError(
            f"'size' parameter for {CTPP_BASE_URL}/datasets endpoint must be"
            " greater than 0 and less than or equal to four"
        )

    if (page <= 0 or page > 4) and page is not None:
        raise ValueError(
            f"'page' parameter for {CTPP_BASE_URL}/datasets must be greater "
            "than 0 and less than or equal to four"
        )

    # if have page, must have size param and vice versa (!xor(page, size))
    # TODO: implement !xor logic for page and size params

    _params = {"size": f"{size}", "page": f"{page}"}
    return _sanitize_params(_params)


def _datasets_year_param_builder(year: int | None = None) -> dict | None:
    """
    Helper function: builds params dictionary for
    the /datasets/{year} endpoint. None if no params
    """
    # year must be one of the acceptable products
    if year not in CTPP_AVAILABLE_YEARS and year is not None:
        raise ValueError(
            f"'year' paramater for {CTPP_BASE_URL}/datasets/{{year}} "
            f"must be one of: {CTPP_AVAILABLE_YEARS}"
        )

    _params = {"year": f"{year}"}
    return _sanitize_params(_params)


def _datasets_year_groups_param_builder(
    year: int | None = None,
    keyword: str | None = None,
    size: int | None = None,
    page: int | None = None,
):
    """
    Helper function: builds params dictionary for the
    /datasets/{year}/groups endpoint.
    """
    # check year (year cannot be None for this query)
    if year not in CTPP_AVAILABLE_YEARS:
        raise ValueError(
            f"'year' parameter is required for "
            f"{CTPP_BASE_URL}/datasets/{{year}}/groups and "
            f"must be one of: {CTPP_AVAILABLE_YEARS}"
        )

    # check size
    if size <= 0 and size is not None:
        raise ValueError(
            f"'size' parameter for {CTPP_BASE_URL}/datasets endpoint must be"
            " greater than 0"
        )

    # check page param
    if page <= 0 or page > 4 and page is not None:
        raise ValueError(
            f"'page' parameter for {CTPP_BASE_URL}/datasets must be greater than 0"
        )

    _params = {
        "year": f"{year}",
        "keyword": f"{keyword}",
        "size": f"{size}",
        "page": f"{page}",
    }
    return _sanitize_params(_params)


def _datasets_year_groups_id_param_builder(
    year: int | None = None, id: str | None = None
):
    """
    Helper function: builds params for the
    /datasets/{year}/groups/{id} endpoint.
    """
    # check year (year cannot be None for this query)
    if year not in CTPP_AVAILABLE_YEARS:
        raise ValueError(
            f"'year' parameter is required for "
            f"{CTPP_BASE_URL}/datasets/{{year}}/groups and "
            f"must be one of: {CTPP_AVAILABLE_YEARS}"
        )

    # TODO: check group id?
    if id is None:
        raise ValueError(
            "'id' parameter is required for "
            f"{CTPP_BASE_URL}/datasets/{{year}}/groups/{{id}}"
        )

    _params = {"year": f"{year}", "id": f"{id}"}
    return _sanitize_params(_params)


def _datasets_param_builder(
    endpoint: str,
    params: dict | None = None,
    year: int | None = None,
    size: int | None = None,
    page: int | None = None,
    id: str | None = None,
    keyword: str | None = None,
):
    """
    Helper function: builds the params dictionary for the CTPP API query
    for the /datasets(/*) endpoints. Wraps all the endpoints that
    fall under /datasets.
    """
    pass


def _groups_param_builder(args):
    pass


def _data_param_builder(args):
    pass


def _query_param_builder(args):
    """
    Helper function: used to build the params dictionary for
    CTPP API query. Serves as wrapper for
    the _data, _groups, and _datasets_param_builder functions
    """
    pass


# helpful function for getting dataset metadata
def get_ctpp_metadata_datasets(args):
    pass


# helfpul function for getting group metadata
def get_ctpp_metadata_groups(args):
    pass


# main CTPP query function
def get_data_ctpp(args):
    pass
