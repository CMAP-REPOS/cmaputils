"""
This module contains functions for interfacing with CTPP API # TODO: ADD documentation.
"""

"""
Author: Aaron Rumph
Date: 05/26/2026
Description: Module containing the source code for CTPP Census API functions/tools as part of the Modeling Procedures and Maintenance project.
Input Files: N/A
Output Files: N/A
"""

# - External dependencies
import json
from pathlib import Path
import logging
import pandas as pd
import requests

# - Internal dependencies
from api_key import load_api_key_ctpp, ApiKeyException

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


# - Classes
class CTPPClient:
    # TODO: ADD documentation

    def __init__(self, api_key: str | None = None, env_path: str | None = None):
        self.api_key = api_key
        self.env_path = env_path

        # making a persistent session for multiple queries
        self.session = requests.Session()
        _api_key = ""

        # loading in API key
        if api_key is not None:
            _api_key = load_api_key_ctpp(key=self.api_key)
        elif env_path is not None:
            _api_key = load_api_key_ctpp(env_path=self.env_path)
        else:
            # warn if no api_key provided
            try:
                _api_key = load_api_key_ctpp()

            except ApiKeyException:
                print(
                    "ERROR: No CTPP API Key found. Please"
                    " either set a 'CTPP_API_KEY' or 'API_KEY' environment"
                    " variable, or provide your API key when initializing a"
                    " CTPPClient object (see docs)"
                )
        self.session.headers.update({"X-API-Key": _api_key})

    def _query(self, ctpp_url: str = CTPP_BASE_URL, params: dict | None = None) -> dict:
        """
        Helper function: the function that actually queries
        the CTPP API. Thin wrapper around Session.get(...).
        """
        _query_response = ""
        _clean_params = _sanitize_params(params)

        # errors if send empty params dict
        if params is None:
            _query_response = self.session.get(ctpp_url)
        else:
            _query_response = self.session.get(ctpp_url, params=_clean_params)

        # check query status code
        if _query_response.status_code != 200:
            # TODO: better error msg
            print("Something went wrong with your query.")
            _query_response.raise_for_status()
            # FIX: returning here for control flow
            return

        # TODO: Change to return df/gdf?
        _json_response = _query_response.json()
        return _json_response

    # -- /datasets endpoint

    def list_datasets(
        self,
        size: int | None = None,
        page: int | None = None,
        params: dict | None = None,
        output_path: str | Path | None = None,
    ) -> dict:
        # TODO: ADD documentation

        if params is not None and (size is not None or page is not None):
            raise ValueError(
                "Cannot provide both 'params' and 'size'/'page'."
                " If providing 'params', do not provide 'size' or 'page'."
                " If providing 'size' or 'page' do not provide 'params'."
            )

        _query_params = (
            params if params is not None else _list_datasets_param_builder(size, page)
        )
        _query_result = self._query(DATASET_ENDPOINT, params=_query_params)

        _write_json_response(_query_result, output_path)
        return _query_result

    def get_dataset_metadata(
        self, year: int, output_path: str | Path | None = None
    ) -> dict:
        # TODO: ADD documentation

        _query_params = _dataset_metadata_param_builder(year)
        _query_result = self._query(
            ctpp_url=f"{DATASET_ENDPOINT}/{year}", params=_query_params
        )

        _write_json_response(_query_result, output_path)
        return _query_result

    def list_groups_in_dataset(
        self,
        year: int,
        keyword: str | None = None,
        size: int | None = None,
        page: int | None = None,
        params: dict | None = None,
        output_path: str | Path | None = None,
    ) -> dict:
        # TODO: ADD documentation

        # check if params AND other args provided (warn user!)
        if params is not None and (
            year is not None
            or keyword is not None
            or size is not None
            or page is not None
        ):
            raise ValueError(
                "Cannot provide 'params' and other arguments."
                " If providing 'params', do not provide other arguments."
                " If providing other arguments, do not provide 'params'."
            )

        _query_params = (
            params
            if params is not None
            else _list_groups_param_builder(year, keyword, size, page)
        )

        _query_year = _query_params.get("year")
        if _query_year not in CTPP_AVAILABLE_YEARS:
            raise ValueError(
                "Must provide a valid year for this query."
                f" Year must be one of: {CTPP_AVAILABLE_YEARS}"
            )

        _endpoint = f"{DATASET_ENDPOINT}/{_query_year}/groups"
        _query_result = self._query(ctpp_url=_endpoint, params=_query_params)

        _write_json_response(_query_result, output_path)
        return _query_result

    def get_group_metadata(
        self,
        year: int,
        id: str,
        params: dict | None = None,
        output_path: str | Path | None = None,
    ) -> dict:
        # TODO: ADD documentation

        if params is not None and (year is not None or id is not None):
            raise ValueError(
                "Cannot provide 'params' and other arguments."
                " If providing 'params', do not provide other arguments."
                " If providing other arguments, do not provide 'params'."
            )

        _query_params = (
            params if params is not None else _group_metadata_param_builder(year, id)
        )

        _query_year = _query_params.get("year")
        _query_id = _query_params.get("id")

        if _query_year not in CTPP_AVAILABLE_YEARS:
            raise ValueError(
                "Must provide a valid year for this query."
                f" Year must be one of: {CTPP_AVAILABLE_YEARS}"
            )

        # TODO: add _query_id checks

        _endpoint = f"{DATASET_ENDPOINT}/{_query_params}/groups/{_query_id}"
        _query_result = self._query(ctpp_url=_endpoint, params=_query_params)

        _write_json_response(_query_result, output_path)
        return _query_result

    # -- /groups endpoint

    def list_groups(
        args,
    ):  # NOTE: I'm almost certain this is redundant but has seperate endpoint
        pass

    def get_groups_metadata(args):  # NOTE: also redundant?
        pass

    def list_group_variables(args):
        pass

    def list_group_geographies(args):
        pass

    # -- /data endpoint

    def get_data(
        year: int,
        get: str | list[str],
        o_for: str | None = None,
        o_in: str | None = None,
        d_for: str | None = None,
        d_in: str | None = None,
        geo: str | None = None,
        d_geo: str | None = None,
        componenet: str | None = None,
        bbox: str | None = None,
        format: str | None = None,
        size: int | None = None,
        page: int | None = None,
        params: dict | None = None,
        output_path: str | Path | None = None,
    ) -> pd.Dataframe:
        """
        Get data by table name for a given year.

        :param year: The year to retrieve data for.
            Must be one of [2000 | 2010 | 2016 | 2021].
        :type year: int
        :param get: The variables (or group) to retrieve from the specified
            dataset. May pass one variable/group name, or a list of names.
        :type get: str or list
        :param o_for: Geography/summary level to use for the origin for the
            query. Must be one of
            ["Nation" | "State" | "State-County" | "State-County-MCD" | "State-Place" | "State-PUMA5" | "MSA" | "MSA-Principal-Cities" | "State-County-Tract" | "TAD" | "TAZ"]
        :type o_for: str, optional
        :param o_in: Geography to filter the query to. Can be used in
            conjuction with `o_for` to filter for chosen
            geographic unit within larger (e.g. `o_for` selects
            counties as summary level and `o_in` filters to
            include counties with in a specific state)
        :type o_in: str, optional
        :param d_for: Geography/summary level to use for the destination for
            the query. Must be one of
            ["Nation" | "State" | "State-County" | "State-County-MCD" | "State-Place" | "State-PUMA5" | "MSA" | "MSA-Principal-Cities" | "State-County-Tract" | "TAD" | "TAZ"]
        :type d_for: str, optional
        :param d_in: Destination geography to filter the query to. Can be used
            in conjuction with `d_for` to filter for chosen
            geographic unit within larger (e.g. `d_for` selects
            counties as summary level and `d_in` filters to
            include counties with in a specific state)
        :type d_in: str, optional
        :param geo:
        :type geo:
        :param d_geo:
        :type d_geo:
        :param component:
        :type component:
        :param bbox: A bounding box to filter geographies to a specific area.
            Bounding box should be given as a list of floats in the form:
            [minLon, minLat, maxLon, maxLat].
        :type bbox: list float, optional
        :param format: The response format for the query. Must be one of:
            ["array" | "list" | "geojson"]. "list" is the default if no option
            is picked.
        :type format: str, optional
        :param size: The number of results per page.
        :type size: int, optional
        :param page: Page number from query results to fetch.
        :type page: int, optional
        :param params: A dictionary, or list of dictionaries, containing
            parameters that match the arguments of this method.
            Meant to make it easier to structure query parameters.
            Particularly useful for making multiple CTPP queries at once.
            See docs for more!

        :return: A Dataframe containing the table requested in the query
        :rtype: pd.Dataframe
        FINISH!!
        """
        # TODO: FINISH DOCUMENTATION

        # error handling stuff
        if year not in CTPP_AVAILABLE_YEARS:
            raise ValueError(
                f" Invalid Year:'year' paramater for this "
                f"query must be one of: {CTPP_AVAILABLE_YEARS}"
            )

        # TODO: table checking logic?
        if not isinstance(get, str) or not isinstance(get, list[str]):
            raise ValueError(
                "Invalid Get: 'get' parameter for this query must be"
                " a string, or list of strings, containing"
                " valid CTPP table/group/variables names."
            )

        pass

    def get_stats(args):
        pass


# - Functions


# AR: be warned, there are lots and lots of helper functions here in order
# to keep the code modular and the logic easier to work with
# (and fix if the API changes)

# NOTE: not supporting the "Accept parameter for any query because I assume
# there is no point in changing query from json (default) to xml


def _sanitize_params(params: dict | None) -> dict | None:
    """
    Helper function: cleans up params dictionary, removing any None key-value
    pairs and returning None if no params
    """
    _params = {
        key: value for key, value in params.items() if value != "" and value is not None
    }
    return _params


def _list_datasets_param_builder(
    size: int | None = None, page: int | None = None
) -> dict:
    """Helper function: builds params dictionary for the /datasets endpoint."""

    # must provide both size and page, OR neither
    if (size is None or page is None) and (size is not None or page is not None):
        raise ValueError(
            "Cannot provide 'page' OR 'size'. If providing one, must"
            " provide the other as well"
        )

    # page and size must be between 0 and 4 as there are only 4 products
    if size <= 0 or size > 4:
        raise ValueError(
            f"'size' parameter for {CTPP_BASE_URL}/datasets endpoint must be"
            " greater than 0 and less than or equal to four"
        )

    if page <= 0 or page > 4:
        raise ValueError(
            f"'page' parameter for {CTPP_BASE_URL}/datasets must be greater "
            "than 0 and less than or equal to four"
        )

    _params = {"size": f"{size}", "page": f"{page}"}
    return _sanitize_params(_params)


def _dataset_metadata_param_builder(year: int | None = None) -> dict | None:
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


def _list_groups_param_builder(
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


def _group_metadata_param_builder(year: int | None = None, id: str | None = None):
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


def _write_json_response(json_response: dict, output_path: str | Path | None = None):
    """Helper function: writes to output_path if not None"""
    if isinstance(output_path, str) or isinstance(output_path, Path):
        with open(output_path, "w") as file:
            json.dump(json_response, file)
    # TODO: add logging if None?
