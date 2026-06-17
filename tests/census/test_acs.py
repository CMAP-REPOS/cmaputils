"""
This module is meant to test that the functions/methods/classes from /src/cmaputils/census/acs.py work.
"""

"""
Author: Aaron Rumph
Date: 05/26/2026
Description: Module containing tests for ACS API functions/classes/methods
Input Files: N/A
Output Files: N/A
"""

# SECTION: External dependencies
import dotenv
import os
import json
import pandas as pd
from pathlib import Path

# SECTION: Internal dependencies
from cmaputils.census.acs import ACSClient, ACSProduct
from cmaputils.census.geography import CensusGeography

# SECTION: Constants
CMAPUTILS_PATH = Path(__file__).parent.parent.parent  # cmaputils root
SAMPLE_OUTPUT_DIR = os.path.join(CMAPUTILS_PATH, "tests", "census", "outputs")
HOME_DIR = os.path.expanduser("~")
CONTRIBUTOR_ENV_PATH = os.path.join(
    CMAPUTILS_PATH, "contributors", "api_keys.env"
)
GENERIC_TEST_CLIENT = ACSClient(env_path=CONTRIBUTOR_ENV_PATH)
INPUTS_DIR = os.path.join(CMAPUTILS_PATH, "tests", "census", "inputs", "acs")

# - Setup
os.makedirs(SAMPLE_OUTPUT_DIR, exist_ok=True)


# SECTION: Tests
def test_client_initialization():
    # NOTE: in order for test to pass, you should have
    # CTPP_API_KEY env var set (or ~\api_keys.env file)
    if os.path.exists(CONTRIBUTOR_ENV_PATH):
        print(f"Found .env file at {CONTRIBUTOR_ENV_PATH}")
        dotenv.load_dotenv(CONTRIBUTOR_ENV_PATH)
    _api_key = os.getenv("CENSUS_API_KEY")

    # should automatically find CTPP key as env var
    test_client = ACSClient()
    assert test_client._census_api_key == _api_key


# NOTE: Test below failing because of encoding issue with csv


def test_get_data_cookIL_S1501():
    known_good_data = []
    with open(os.path.join(INPUTS_DIR, "cookIL_S1501.csv")) as file:
        # data came from manually downloading
        # original CSV has weird encoding, and is missing state and county FIPS
        known_good_data = pd.read_csv(file, encoding="cp1252")

    test_result = GENERIC_TEST_CLIENT.get_data(
        get="S1501",
        year=2024,
        product=ACSProduct.ACS5,
        geography=CensusGeography.county(county="031", state="17"),
    )

    print(test_result["state"])
    print(test_result["county"])

    assert test_result == known_good_data


if __name__ == "__main__":
    test_get_data_cookIL_S1501()
