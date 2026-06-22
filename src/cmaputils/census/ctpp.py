"""
This module contains functions for interfacing with CTPP API # TODO: ADD documentation.
"""

from __future__ import annotations  # has to go here because __future__ is weird

"""
Author: Aaron Rumph
Date: 05/27/2026
Description: Module containing the source code for CTPP Census API functions/tools as part of the Modeling Procedures and Maintenance project.
Input Files: N/A
Output Files: N/A
"""


# SECTION: External dependencies
import json
from pathlib import Path
import logging
import pandas as pd
import requests
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
import re

# SECTION: Internal dependencies
from cmaputils.census.api_key import load_api_key_ctpp, ApiKeyException
from cmaputils.census.geography import CensusGeography


# SECTION: Constants
_CTPP_BASE_URL = "https://ctppdata.transportation.org/api"
_DATASET_ENDPOINT = f"{_CTPP_BASE_URL}/datasets"
_GROUP_ENDPOINT = f"{_CTPP_BASE_URL}/groups"
_DATA_ENDPOINT = f"{_CTPP_BASE_URL}/data"

_CTPP_SUMMARY_LEVELS = [
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
_CTPP_AVAILABLE_YEARS = [2000, 2010, 2016, 2021]
_CTPP_RESPONSE_FORMATS = ["array", "list", "geojson"]

_LONGITUDE_REGEX = re.compile(
    r"^[-+]?(180(\.0+)?|1[0-7]\d(\.\d+)?|\d{1,2}(\.\d+)?)$"
)
_LATITUDE_REGEX = re.compile(r"^[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)$")

# -- Useful fipscodes
_CMAP_COUNTY_CODES = ["031", "089", "043", "097", "093", "111", "197"]


# SECTION: Classes


# -- Enums
class _CTPPYear(IntEnum):
    """
    Helper function: enum that just makes it easier to check whether year
    is valid in query or not

    :meta private:
    """

    Y2000 = 2000
    Y2010 = 2010
    Y2016 = 2016
    Y2021 = 2021

    @classmethod
    def _ctpp_year_from_value(cls, year: int | str | _CTPPYear) -> _CTPPYear:
        """
        Helper Function: gives proper errors for improper years for CTPP

        :meta private:
        """
        if isinstance(year, _CTPPYear):
            return year
        elif isinstance(year, int) and year in _CTPP_AVAILABLE_YEARS:
            return _CTPPYear(year)
        elif isinstance(year, str) and int(year) in _CTPP_AVAILABLE_YEARS:
            return _CTPPYear(int(year))
        else:
            raise ValueError(
                "Provided year must be an int, string, or CTPPYear instance"
                f" and must be one of: {_CTPP_AVAILABLE_YEARS}"
            )


class SummaryLevel(StrEnum):
    # TODO: fix mapping for mcd, puma, msa, msa princ cities, tad, taz
    NATION = "nation"
    STATE = "state"
    COUNTY = "county"
    COUNTY_MCD = "mcd"
    PLACE = "place"
    PUMA = "State-PUMA5"
    MSA = "MSA"
    MSA_Principal_Cities = "MSA-Principal-Cities"
    TRACT = "tract"
    TAD = "TAD"
    TAZ = "TAZ"

    @classmethod
    def _summary_level_from_string(
        cls, level: str | SummaryLevel
    ) -> SummaryLevel:
        if isinstance(level, SummaryLevel):
            return level
        elif isinstance(level, str):
            # NOTE: have to define this mapping within the class for this to work unfortunately
            _summary_level_mapping = {
                "nation": cls.NATION,
                "state": cls.STATE,
                "county": cls.COUNTY,
                "state-county": cls.COUNTY,
                "state-county-mcd": cls.COUNTY_MCD,
                "county-mcd": cls.COUNTY_MCD,
                "mcd": cls.COUNTY_MCD,
                "minor-civil-divisions": cls.COUNTY_MCD,
                "place": cls.PLACE,
                "municipality": cls.PLACE,
                "city": cls.PLACE,
                "town": cls.PLACE,
                "puma": cls.PUMA,
                "public-use-microdata-area": cls.PUMA,
                "msa": cls.MSA,
                "metropolitan-statistical-area": cls.MSA,
                "msa-principal-cites": cls.MSA,
                "principal-cities": cls.MSA,
                "tract": cls.TRACT,
                "census-tract": cls.TRACT,
                "traffic-analysis-district": cls.TAD,
                "tad": cls.TAD,
                "taz": cls.TAZ,
                "traffic-analysis-zone": cls.TAZ,
            }
            _cleaned_level = level.strip().lower().replace(" ", "-")
            _cleaned_value = _summary_level_mapping.get(_cleaned_level)

            if _cleaned_value is None:
                raise ValueError(
                    "Invalid Geography: Please enter a valid geography!"
                    f" Must be one of: {_summary_level_mapping.keys()}"
                )
            return _cleaned_value


class CTPPClient:
    """
    Client object for querying CTPP API. If no API key is
        provided or no .env path is provided, CTPPClient
        object will be use API_KEY or CTPP_API_KEY env variable

    Parameters
    -----
    api_key : str, optional
        CTPP API key str, if would like to explictly construct CTPPClient
        with a given API key.
    env_path: str, optional
        A path to a .env file, if would like to explicitly construct
        CTPPClient with a given API key contained therein.
        .env file must contain either `API_KEY` or `CTPP_API_KEY`
    """

    # TODO: ADD documentation
    def __init__(self, api_key: str | None = None, env_path: str | None = None):
        self.api_key = api_key
        self.env_path = env_path
        self._ctpp_api_key = ""

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
        self._ctpp_api_key = _api_key

    def _query(
        self, ctpp_url: str = _CTPP_BASE_URL, params: dict | None = None
    ) -> dict:
        """
        Helper function: the function that actually queries
        the CTPP API. Thin wrapper around Session.get(...).

        :meta private:
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
            params
            if params is not None
            else _list_datasets_param_builder(size, page)
        )
        _query_result = self._query(_DATASET_ENDPOINT, params=_query_params)

        _write_json_response(_query_result, output_path)
        return _query_result

    def get_dataset_metadata(
        self, year: int, output_path: str | Path | None = None
    ) -> dict:
        # TODO: ADD documentation

        _query_params = _dataset_metadata_param_builder(year)
        _query_result = self._query(
            ctpp_url=f"{_DATASET_ENDPOINT}/{year}", params=_query_params
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
        # FIX: shouldn't have to cast to int, fix _sanitize_params/builder functions
        if int(_query_year) not in _CTPP_AVAILABLE_YEARS:
            raise ValueError(
                "Must provide a valid year for this query."
                f" Year must be one of: {_CTPP_AVAILABLE_YEARS}"
            )

        _endpoint = f"{_DATASET_ENDPOINT}/{_query_year}/groups"
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
            params
            if params is not None
            else _group_metadata_param_builder(year, id)
        )

        _query_year = _query_params.get("year")
        _query_id = _query_params.get("id")

        if int(_query_year) not in _CTPP_AVAILABLE_YEARS:
            raise ValueError(
                "Must provide a valid year for this query."
                f" Year must be one of: {_CTPP_AVAILABLE_YEARS}"
            )

        # TODO: add _query_id checks

        _endpoint = f"{_DATASET_ENDPOINT}/{_query_year}/groups/{_query_id}"
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
        self,
        year: int,
        get: str | list[str],
        origin: CensusGeography | None = None,
        destination: CensusGeography | None = None,
        component: str | None = None,
        bbox: str | list[float] | None = None,
        response_format: str | None = None,
        size: int | None = None,
        page: int | None = None,
        params: dict | None = None,
        output_path: str | Path | None = None,
    ) -> dict:
        """
        Query CTPP data for specified parameters.

        Parameters
        -----
        year : int
            The dataset year to get data from. Must be one of [2000 | 2010 | 2016 | 2021]
        get : str | list[str]
            The group/variable to get data for. E.g. B303100 or A101101_e1
        origin : CensusGeography, optional
            The origin geography to get data for flows. Should be constructed
            as a `CensusGeography` object using `CensusGeography.tract()`,
            `CensusGeography.county()`, etc.
        destination : CensusGeography, optional
            The destination geography to get data for flows. Should be
            constructed as a `CensusGeography` object using
            `CensusGeography.tract()`, `CensusGeography.county()`, etc.

        Returns
        -----
        Returns a dictionary of the response from the CTPP get_data query
        """

        # error handling stuff
        if year not in _CTPP_AVAILABLE_YEARS:
            raise ValueError(
                f" Invalid Year:'year' paramater for this "
                f"query must be one of: {_CTPP_AVAILABLE_YEARS}"
            )

        # TODO: table checking logic?
        if not isinstance(get, str) and not (isinstance(get, list)):
            raise ValueError(
                "Invalid Get: 'get' parameter for this query must be"
                " a string, or list of strings, containing"
                " valid CTPP table/group/variables names."
            )

        if not isinstance(origin, CensusGeography) and origin is not None:
            raise TypeError(
                "'origin' parameter must be of type CensusGeography!"
                " See method documentation or docs for CensusGeography for"
                " information on constructing/using the CensusGeography class"
            )

        # NOTE: (over) nesting makes more readable here
        if bbox is not None:
            _coords = []
            if isinstance(bbox, str):
                for _coord in bbox.split(","):
                    try:
                        _coords.append(float(_coord))
                    except ValueError:
                        raise ValueError(
                            f"Could not parse coord '{_coord}' in '{bbox}'"
                            " please pass a valid string in the format:"
                            "'min_lat,min_lat,max_lon,max_lat'"
                        )
            elif isinstance(bbox, list) and len(bbox) == 4:
                for _coord in bbox:
                    try:
                        _coords.append(float(_coord))
                    except ValueError:
                        raise ValueError(
                            f"Could not parse coord '{_coord}' in '{bbox}'"
                            " please pass a valid list in the format:"
                            "[min_lat, min_lat, max_lon, max_lat]"
                        )
            else:
                raise ValueError(
                    "Invalid bbox: must provide either a string"
                    " or a list containing 4 bounding coordinates!"
                )

            # quick check for validity
            for _lat in [_coords[0], _coords[2]]:
                if not _LATITUDE_REGEX.match(_lat):
                    raise ValueError(
                        f"Invalid bbox: '{_lat}' is not a valid latitude"
                    )
            for _lon in [_coords[1], _coords[3]]:
                if not _LONGITUDE_REGEX.match(_lon):
                    raise ValueError(
                        f"Invalid bbox: '{_lat}' is not a valid longitude"
                    )

        if (
            response_format is not None
            and response_format not in _CTPP_RESPONSE_FORMATS
        ):
            raise ValueError(
                "Invalid response_format: response_format must be one of:"
                f" {_CTPP_RESPONSE_FORMATS}"
            )

        # formatting params list of tuples for query
        query_params = [("year", year)]
        _get_value = ""

        if isinstance(get, str):
            if "_" not in get:
                _get_value = f"group({get})"
            else:
                _get_value = get
        elif isinstance(get, list) and all(
            isinstance(table, str) for table in get
        ):
            _get_parts = []
            for _table in get:
                if "_" not in _table:
                    _get_parts.append(f"group({_table})")
                else:
                    _get_parts.append(_table)
            _get_value = ",".join(_get_parts)
        else:
            raise TypeError("'get' must be of type str or list[str]")

        query_params.append(("get", _get_value))

        if isinstance(origin, CensusGeography):
            query_params.extend(_ctppgeography_to_params(origin, "origin"))
        elif origin is not None:
            raise TypeError(
                # TODO:
            )

        if isinstance(destination, CensusGeography):
            query_params.extend(
                _ctppgeography_to_params(destination, "destination")
            )
        elif destination is not None:
            raise TypeError(
                # TODO:
            )

        # TODO: finish rest of arguments!

        url = f"{_DATA_ENDPOINT}/{year}"

        response = self.session.get(url, params=query_params)
        response.raise_for_status()

        response_data = response.json()
        # return df
        return response_data

    def _get_data(
        year: int,
        get: str | list[str],
        o_for: str | None = None,
        o_in: str | None = None,
        d_for: str | None = None,
        d_in: str | None = None,
        geo: str | None = None,
        d_geo: str | None = None,
        component: str | None = None,
        bbox: str | None = None,
        response_format: str | None = None,
        size: int | None = None,
        page: int | None = None,
        params: dict | None = None,
        output_path: str | Path | None = None,
    ) -> pd.DataFrame:
        """
        Helper Function: The function that actually runs the CTPP Query

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
        :param response_format: The response format for the query. Must be one of:
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

        :return: A DataFrame containing the table requested in the query
        :rtype: pd.DataFrame
        FINISH!!

        :meta private:
        """
        # TODO: FINISH DOCUMENTATION

        pass

    def get_stats(args):
        pass


# SECTION: Functions

# AR: be warned, there are lots and lots of helper functions here in order
# to keep the code modular and the logic easier to work with
# (and fix if the API changes)

# NOTE: not supporting the "Accept parameter for any query because I assume
# there is no point in changing query from json (default) to xml

# -- param builder helper functions


def _sanitize_params(params: dict | None) -> dict | None:
    """
    Helper function: cleans up params dictionary, removing any None key-value
    pairs and returning None if no params

    :meta private:
    """
    _params = {
        key: value
        for key, value in params.items()
        if value != "" and value != "None" and value is not None
    }
    return _params


def _list_datasets_param_builder(
    size: int | None = None, page: int | None = None
) -> dict:
    """
    Helper function: builds params dictionary for the /datasets endpoint.

    :meta private:
    """

    # must provide both size and page, OR neither
    if (size is None or page is None) and (
        size is not None or page is not None
    ):
        raise ValueError(
            "Cannot provide 'page' OR 'size'. If providing one, must"
            " provide the other as well"
        )

    # page and size must be between 0 and 4 as there are only 4 products
    if size is not None and (size <= 0 or size > 4):
        raise ValueError(
            f"'size' parameter for {_CTPP_BASE_URL}/datasets endpoint must be"
            " greater than 0 and less than or equal to four"
        )

    if page is not None and (page <= 0 or page > 4):
        raise ValueError(
            f"'page' parameter for {_CTPP_BASE_URL}/datasets must be greater "
            "than 0 and less than or equal to four"
        )

    _params = {"size": f"{size}", "page": f"{page}"}
    return _sanitize_params(_params)


def _dataset_metadata_param_builder(year: int | None = None) -> dict | None:
    """
    Helper function: builds params dictionary for
    the /datasets/{year} endpoint. None if no params

    :meta private:
    """
    # year must be one of the acceptable products
    if year not in _CTPP_AVAILABLE_YEARS and year is not None:
        raise ValueError(
            f"'year' paramater for {_CTPP_BASE_URL}/datasets/{{year}} "
            f"must be one of: {_CTPP_AVAILABLE_YEARS}"
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

    :meta private:
    """
    # check year (year cannot be None for this query)
    if year not in _CTPP_AVAILABLE_YEARS:
        raise ValueError(
            f"'year' parameter is required for "
            f"{_CTPP_BASE_URL}/datasets/{{year}}/groups and "
            f"must be one of: {_CTPP_AVAILABLE_YEARS}"
        )

    # check size
    if size is not None and (size <= 0 and size is not None):
        raise ValueError(
            f"'size' parameter for {_CTPP_BASE_URL}/datasets endpoint must be"
            " greater than 0"
        )

    # check page param
    if page is not None and (page <= 0 or page > 4 and page is not None):
        raise ValueError(
            f"'page' parameter for {_CTPP_BASE_URL}/datasets must be greater than 0"
        )

    _params = {
        "year": f"{year}",
        "keyword": f"{keyword}",
        "size": f"{size}",
        "page": f"{page}",
    }
    return _sanitize_params(_params)


def _group_metadata_param_builder(
    year: int | None = None, id: str | None = None
):
    """
    Helper function: builds params for the
    /datasets/{year}/groups/{id} endpoint.

    :meta private:
    """
    # check year (year cannot be None for this query)
    if year not in _CTPP_AVAILABLE_YEARS:
        raise ValueError(
            f"'year' parameter is required for "
            f"{_CTPP_BASE_URL}/datasets/{{year}}/groups and "
            f"must be one of: {_CTPP_AVAILABLE_YEARS}"
        )

    # TODO: check group id?
    if id is None:
        raise ValueError(
            "'id' parameter is required for "
            f"{_CTPP_BASE_URL}/datasets/{{year}}/groups/{{id}}"
        )

    _params = {"year": f"{year}", "id": f"{id}"}
    return _sanitize_params(_params)


# -- CensusGeography helpers


def _format_fips(fips: str | list[str]) -> str:
    """
    Helper function: formats inputted fips for query

    :meta private:
    """
    if isinstance(fips, str):
        return fips
    elif isinstance(fips, list) and all(
        (isinstance(code, str) for code in fips)
    ):
        return ",".join(fips)
    else:
        raise TypeError("Provided fips code must be of type str or list[str]")


def _ctppgeography_to_params(
    geography: CensusGeography, origin_or_destination: str
) -> list[tuple[str, str]]:
    """
    Helper function: turns CensusGeography object into params dict.
    `origin_or_destination` must be either 'origin' or 'destination'

    :meta private:
    """
    _for_key = ""
    _in_key = ""
    if origin_or_destination == "origin":
        _for_key = "for"
        _in_key = "in"
    elif origin_or_destination == "destination":
        _for_key = "d-for"
        _in_key = "d-in"
    else:
        raise ValueError(
            "origin_or_destination must be either 'origin' or 'destination'"
        )

    params = [
        (_for_key, f"{geography.level.value}:{_format_fips(geography.fips)}")
    ]

    if geography.within:
        for level, fips in geography.within.items():
            _level = level.value
            _formatted_fips = _format_fips(fips)

            params.append((_in_key, f"{_level}:{_formatted_fips}"))

    return params


def _write_json_response(
    json_response: dict, output_path: str | Path | None = None
):
    """
    Helper function: writes to output_path if not None

    :meta private:
    """
    if isinstance(output_path, str) or isinstance(output_path, Path):
        with open(output_path, "w") as file:
            json.dump(json_response, file)
    # TODO: add logging if None?
