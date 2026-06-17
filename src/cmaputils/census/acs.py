"""
This module contains functions for interfacing with the ACS API. # TODO: ADD documentation.
"""

"""
Author: Aaron Rumph
Date: 05/20/2026
Description: Module containing the source code for ACS Census API functions/tools as part of the Modeling Procedures and Maintenance project
Input Files: N/A
Output Files: N/A
Useful External Documentation:
    https://www.census.gov/programs-surveys/acs/data/data-via-api.html

"""

# SECTION: External dependencies
import pandas as pd
import requests
import re
from enum import StrEnum
from pathlib import Path

# SECTION: Internal dependencies
from cmaputils.census.api_key import load_api_key_census
from cmaputils.census.api_key import ApiKeyException
from cmaputils.census.geography import (
    CensusGeography,
    _census_geography_to_params,
)

# SECTION: Constants
_BASE_CENSUS_URL = "https://api.census.gov/data"

# -- list of all ACS products (for use in validating query parameters)
_VALID_ACS_PRODUCTS = [
    "acs1",
    "acs5",
    "acs",
    "acs3",
    "migration-flows",
    "language-statistics-2013",
    "1-year-PUMS",
    "5-year-PUMS",
]

# -- years available for various ACS products (this way can easily be changed)
# NOTE: AR: maintainer's note: change these if available years change
_ACS_1_AVAIL_YEARS = list(range(2005, 2025))
_ACS_5_AVAIL_YEARS = list(range(2005, 2025))
_ACS_1_SUPP_AVAIL_YEARS = list(range(2014, 2025))
_ACS_3_AVAIL_YEARS = list(range(2007, 2014))
_ACS_MIG_FLOWS_AVAIL_YEARS = list(range(2010, 2023))
_ACS_LANG_STAT_AVAIL_YEARS = list(range(2013, 2014))
_ACS_1_PUMS_AVAIL_YEARS = list(range(2005, 2020)) + list(
    range(2021, 2025)
)  # gap because of COVID
_ACS_5_PUMS_AVAIL_YEARS = list(range(2009, 2025))


# NOTE: this enum makes it easy to form the query url based on
# the product requested by user (functionally an endpoint selector)
class ACSProduct(StrEnum):
    """
    Enum representing different ACS products, e.g., ACS 1 year.

    Usage
    -----
    I
    """

    ACS1 = "acs1"
    ACS5 = "acs5"
    ACS3 = "acs3"
    PUMS1 = "acs1/pums"
    PUMS5 = "acs5/pums"
    PUMS1PR = "acs1/pumspr"
    PUMS5PR = "acs5/pumspr"
    AIAN = "acs5/aian"
    MIGRATION_FLOWS = "flows"


# available years by ACSProduct
_ACS_PRODUCT_AVAIL = {
    ACSProduct.ACS1: _ACS_1_AVAIL_YEARS,
    ACSProduct.ACS5: _ACS_5_AVAIL_YEARS,
    ACSProduct.ACS3: _ACS_3_AVAIL_YEARS,
    ACSProduct.MIGRATION_FLOWS: _ACS_MIG_FLOWS_AVAIL_YEARS,
    ACSProduct.PUMS1: _ACS_1_PUMS_AVAIL_YEARS,
    ACSProduct.ACS5: _ACS_5_PUMS_AVAIL_YEARS,
    ACSProduct.PUMS1PR: _ACS_1_PUMS_AVAIL_YEARS,
    ACSProduct.PUMS5PR: _ACS_5_PUMS_AVAIL_YEARS,
}


# some useful regexes to match ACS table IDs
_ACS_TABLE_REGEXES = [
    r"^(B\d{5}[A-Z]{0,3})$",
    r"^(C\d{5}[A-Z]{0,3})$",
    r"^(CP\d{2}(?:PR)?)$",
    r"^(DP\d{2}(?:PR)?)$",
    r"^(K\d{6}(?:PR)?)$",
    r"^(S\d{4}[A-Z]?(PR)?)$",
]


# SECTION: Exceptions
class AcsQueryException(Exception):
    """Exception raised by a problem in querying the ACS"""

    pass


# SECTION: Classes
class ACSClient:
    """
    Client object for querying ACS API. If no API key is provided,
    or no .env path is provided, ACSClient object will use API_KEY
    or CENSUS_API_KEY env variable.

    Parameters
    -----
    api_key : str, optional
        Census API key str, if would like to explictly construct CTPPClient
        with a given API key.
    env_path: str, optional
        A path to a .env file, if would like to explicitly construct
        ACSClient with a given API key contained therein.
        .env file must contain either `API_KEY` or `CENSUS_API_KEY`
    """

    def __init__(self, api_key: str | None = None, env_path: str | None = None):
        self.api_key = api_key
        self.env_path = env_path
        self._census_api_key = ""

        # making a persistent session for multiple queries
        self.session = requests.Session()
        _api_key = ""

        # loading in API key
        if api_key is not None:
            _api_key = load_api_key_census(key=self.api_key)
        elif env_path is not None:
            _api_key = load_api_key_census(env_path=self.env_path)
        else:
            # warn if no api_key provided
            try:
                _api_key = load_api_key_census()

            except ApiKeyException:
                raise ApiKeyException(
                    "ERROR: No Census API Key found. Please"
                    " either set a 'CENSUS_API_KEY' or 'API_KEY' environment"
                    " variable, or provide your API key when initializing an"
                    " ACSClient object (see docs)"
                )
        self._census_api_key = _api_key

    def _append_api_key(self, params: list[tuple]) -> str:
        """
        Helper function: appends API key param to list of tuples for ACS query
            (if necessary)

        :meta private:
        """

        _params = params
        _key_tuple = ("key", self._census_api_key)
        if not any("key" in param_tuple for param_tuple in params):
            _params.append(_key_tuple)

        return _params

    def get_data(
        self,
        *,
        get: str | list[str],
        year: int,
        product: ACSProduct,
        geography: CensusGeography,
        output_path: str | Path = None,
        keep_annotation_fields: bool = False,
    ) -> pd.DataFrame:
        """
        Method to get ACS data from the Census' API.

        Parameters
        -----
        get : str | list[str]
            The group/variable to get data for. E.g. B303100 or A101101_e1
        year : int
            The dataset year to get data for.
        product : ACSProduct
            The product to get the specified dataset for. Must be of form
            ACSProduct.ACS1, ACSProduct.ACS5, ACSProduct.PUMS5, etc.
            (See `ACSProduct` documentation)
        geography : CensusGeography
            The geography to get data for. Should be constructed as a
            `CensusGeography` object using `CensusGeography.tract()`,
            `CensusGeography.county()`, etc.
            (See `CensusGeography` documentation)
        output_path : str | pathlib.Path, optional
            A path where to returned data should be written to. Will
            create a .csv at that path if provided. If not provided,
            returned data will not be written to disk.
        keep_annotation_fields : bool = False,
            By default, this method will discard the data annotation
            fields returned by the API (e.g. 'B303100_01EA').
            Pass `keep_annotation_fields=True` if you would like
            to keep these fields in the returned DataFrame

        Examples
        -----
        To get table S1501 for year 2024 from the ACS 5-year dataset
            for Cook County IL:

        >>> example_client = ACSClient()
            example_data = example_client.get_data(
                get="S1501",
                year=2024,
                product=ACSProduct.ACS5,
                geography=CensusGeography.county(county="031", state="17")
            )


        """

        # TODO: ADD Documentatoin
        # get validation
        _table_regex_patterns = [re.compile(pat) for pat in _ACS_TABLE_REGEXES]
        _is_valid_get = any(
            pattern.search(get) for pattern in _table_regex_patterns
        )
        if not _is_valid_get:
            raise AcsQueryException(
                "The table ID you provided is invalid, please provide a valid"
                " get parameter. You can find a list of all ACS tables here: "
                "https://www.census.gov/programs-surveys/acs/technical-documentation/table-shells.html"
            )

        # year validation
        if not (year >= 2005 and year <= 2026):
            raise AcsQueryException(
                "The year you provided is not a valid ACS year. Please provide a year between 2005 and 2026 (inclusive)"
            )

        # product validation
        if not isinstance(product, ACSProduct):
            raise AcsQueryException(
                f"The product you provided is not a valid ACS product. "
                f"Please select one of the following: {_VALID_ACS_PRODUCTS}"
            )

        # check that year provided for query actually matches the available years
        if year not in _ACS_PRODUCT_AVAIL[product]:
            raise AcsQueryException(
                f"The year you provided is not available for the product you provided. You provided: "
                f"'year': {year}, 'product': {product}."
            )

        # -- Need to find proper endpoint depending on the type of table (subject, comparison, etc)
        _endpoint_flag = ""

        if get.startswith("S"):
            _endpoint_flag = "subject"
        elif get.startswith("C"):
            _endpoint_flag = "comparison"
        else:
            _endpoint_flag = ""

        _product_flag = product.value

        # -- Building query url
        query_url = (
            f"{_BASE_CENSUS_URL}/{year}/acs/{_product_flag}/{_endpoint_flag}"
        )

        # -- Building query params
        query_params = []
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

        # adding API key
        query_params = self._append_api_key(query_params)

        if isinstance(geography, CensusGeography):
            query_params.extend(
                _census_geography_to_params(geography, "origin")
            )
        elif geography is not None:
            raise TypeError(
                # TODO: good error msg
            )

        # -- send off request
        response = self.session.get(url=query_url, params=query_params)
        response.raise_for_status()

        response_json = response.json()
        response_df = pd.DataFrame(response_json[1:], columns=response_json[0])

        # -- removing anotation fields
        if not keep_annotation_fields:
            # NOTE: AR: best I can tell, EA and MA are annotation columns
            # remove columns (EA and MA columns which I don't entirely understand point of)
            cols_to_remove = [
                col
                for col in response_df.columns
                if col.endswith("MA") or col.endswith("EA") or "Margin" in col
            ]
            response_df.drop(columns=cols_to_remove, inplace=True)

        # -- saving to csv if desired
        if output_path is not None and not (
            isinstance(output_path, str) or isinstance(output_path, Path)
        ):
            response_df.to_csv(output_path, encoding="utf-8")

        return response_df


# SECTION: Functions

if __name__ == "__main__":
    test_client = ACSClient(env_path="contributors\\api_keys.env")
    test_result = test_client.get_data(
        get="S1501",
        year=2024,
        product=ACSProduct.ACS5,
        geography=CensusGeography.county(county="031", state="17"),
    )
    print(test_result)
