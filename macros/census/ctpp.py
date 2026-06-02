"""
This script contains macros for generating Python code for CTPP queries.
These macros run as part of a pre-commit process and generate lists of
GeoIDs and FIPS codes to allow for concurrent CTPP requests and
input validation.
"""

# SECTION: External dependencies
import requests

# SECTION: Internal dependencies
from cmaputils.census.api_key import load_api_key_census

# SECTION: Constants
TRACT_FIPS_URL = "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=tract:*&in=county:*&in=state:*"
COUNTY_FIPS_URL = (
    "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=county:*&in=state:*"
)
STATE_FIPS_URL = (
    "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=state:*"
)

# NOTE: In order to run this macro you must have an API
# for the Census in either a CENSUS_API_KEY env var or in a
# API_KEY env var
CONTRIBUTOR_API_KEY = load_api_key_census()

# SECTION: Classes


# SECTION: Functions
def get_county_fips():
    api_response = requests.get(
        url=COUNTY_FIPS_URL, params={"key": CONTRIBUTOR_API_KEY}
    )
    print(api_response)


# TODO: fix macros!


if __name__ == "__main__":
    get_county_fips()
