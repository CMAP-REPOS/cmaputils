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

# - External dependencies
import pandas as pd
import requests
import re

# - Internal dependencies
from api_key import load_census_api_key

# - Constants
IL_FIPS_CODE = "17"  # Useful for defaulting to Illinois
WI_FIPS_CODE = "55"
IN_FIPS_CODE = "18"
BASE_CENSUS_URL = "https://api.census.gov/data"

# list of all ACS products (for use in validating query parameters)
VALID_ACS_PRODUCTS = [
    "1-year",
    "5-year",
    "1-year-supplemental",
    "3-year",
    "migration-flows",
    "language-statistics-2013",
    "1-year-PUMS",
    "5-year-PUMS",
]

# years available for various ACS products (this way can easily be changed)
ACS_1_AVAIL_YEARS = list(range(2005, 2025))
ACS_5_AVAIL_YEARS = list(range(2005, 2025))
ACS_1_SUPP_AVAIL_YEARS = list(range(2014, 2025))
ACS_3_AVAIL_YEARS = list(range(2007, 2014))
ACS_MIG_FLOWS_AVAIL_YEARS = list(range(2010, 2023))
ACS_LANG_STAT_AVAIL_YEARS = list(range(2013, 2014))
ACS_1_PUMS_AVAIL_YEARS = list(range(2005, 2020)) + list(
    range(2021, 2025)
)  # gap because of COVID
ACS_5_PUMS_AVAIL_YEARS = list(range(2009, 2025))

# list of lists of available years for convenience sake
ACS_AVAIL_YEARS = [
    ACS_1_AVAIL_YEARS,
    ACS_5_AVAIL_YEARS,
    ACS_1_SUPP_AVAIL_YEARS,
    ACS_3_AVAIL_YEARS,
    ACS_MIG_FLOWS_AVAIL_YEARS,
    ACS_LANG_STAT_AVAIL_YEARS,
    ACS_1_PUMS_AVAIL_YEARS,
    ACS_5_PUMS_AVAIL_YEARS,
]

# year availability dictionary for validation
VALID_ACS_PRODUCT_YEARS = {
    VALID_ACS_PRODUCTS[i]: ACS_AVAIL_YEARS[i] for i in range(0, 8)
}


# some useful regexes to match ACS table IDs
ACS_TABLE_REGEXES = [
    r"^(B\d{5}[A-Z]{0,3})$",
    r"^(C\d{5}[A-Z]{0,3})$",
    r"^(CP\d{2}(?:PR)?)$",
    r"^(DP\d{2}(?:PR)?)$",
    r"^(K\d{6}(?:PR)?)$",
    r"^(S\d{4}[A-Z]?(PR)?)$",
]


# - Exceptions
class AcsQueryException(Exception):
    """Exception raised by a problem in querying the ACS"""

    pass


# - Classes


# - Functions
def get_data_acs(
    table_id: str, year: int, product: str, output_dir: str = None, api_key: str = None
):
    """
    # TODO: ADD documentation
    """

    # table_id validation
    _table_regex_patterns = [re.compile(pat) for pat in ACS_TABLE_REGEXES]
    _is_valid_table_id = any(
        pattern.search(table_id) for pattern in _table_regex_patterns
    )
    if not _is_valid_table_id:
        raise AcsQueryException(
            "The table ID you provided is invalid, please provide a valid"
            " table_id parameter. You can find a list of all ACS tables here: "
            "https://www.census.gov/programs-surveys/acs/technical-documentation/table-shells.html"
        )

    # year validation
    if not (year >= 2005 and year <= 2026):
        raise AcsQueryException(
            "The year you provided is not a valid ACS year. Please provide a year between 2005 and 2026 (inclusive)"
        )

    # product validation
    if product not in VALID_ACS_PRODUCTS:
        raise AcsQueryException(
            f"The product you provided is not a valid ACS product. "
            f"Please select one of the following: {VALID_ACS_PRODUCTS}"
        )

    # check that year provided for query actually matches the available years
    if year not in VALID_ACS_PRODUCT_YEARS[product]:
        raise AcsQueryException(
            f"The year you provided is not available for the product you provided. You provided: "
            f"'year': {year}, 'product': {product}."
        )

    # load api key (if api_key param is None, will look in default places)
    _api_key = load_census_api_key(key=api_key)
