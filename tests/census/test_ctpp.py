"""
This module is meant to test that the functions/methods/classes from /src/cmaputils/census/ctpp.py work.
"""

"""
Author: Aaron Rumph
Date: 05/26/2026
Description: Module containing tests for CTPP API functions/classes/methods
Input Files: N/A
Output Files: N/A
"""

# SECTION: External dependencies
import pytest
import dotenv
import os
import json
import pandas as pd
from pathlib import Path

# SECTION: Internal dependencies
from cmaputils.census.ctpp import CTPPClient, CTPPGeography

# SECTION: Constants
CMAPUTILS_PATH = Path(__file__).parent.parent.parent  # cmaputils root
SAMPLE_OUTPUT_DIR = os.path.join(CMAPUTILS_PATH, "tests", "census", "outputs")
SAMPLE_OUTPUT_PATH = os.path.join(SAMPLE_OUTPUT_DIR, "ctpp.json")
HOME_DIR = os.path.expanduser("~")
CONTRIBUTOR_ENV_PATH = os.path.join(
    CMAPUTILS_PATH, "contributors", "api_keys.env"
)
GENERIC_TEST_CLIENT = CTPPClient(env_path=CONTRIBUTOR_ENV_PATH)
INPUTS_DIR = os.path.join(CMAPUTILS_PATH, "tests", "census", "inputs", "ctpp")

# - Setup
os.makedirs(SAMPLE_OUTPUT_DIR, exist_ok=True)


# SECTION: Tests
def test_client_initialization():
    # NOTE: in order for test to pass, you should have
    # CTPP_API_KEY env var set (or ~\api_keys.env file)
    if os.path.exists(CONTRIBUTOR_ENV_PATH):
        print(f"Found .env file at {CONTRIBUTOR_ENV_PATH}")
        dotenv.load_dotenv(CONTRIBUTOR_ENV_PATH)
    _api_key = os.getenv("CTPP_API_KEY")

    # should automatically find CTPP key as env var
    test_client = CTPPClient()
    assert test_client._ctpp_api_key == os.getenv("CTPP_API_KEY")


def test_ctpp_list_datasets():
    known_good_data = {}
    with open(os.path.join(INPUTS_DIR, "list_datasets.json")) as file:
        # data came from manually downloading
        known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.list_datasets()

    assert test_result == known_good_data


def test_ctpp_get_dataset_metadata():
    known_good_data = {}
    with open(os.path.join(INPUTS_DIR, "get_dataset_metadata.json")) as file:
        known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_dataset_metadata(year=2021)
    assert test_result == known_good_data


def test_ctpp_list_groups_in_dataset():
    known_good_data = {}
    with open(os.path.join(INPUTS_DIR, "list_groups_in_dataset.json")) as file:
        known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.list_groups_in_dataset(
        year=2021, keyword="language"
    )
    assert test_result == known_good_data


def test_ctpp_get_group_metadata():
    known_good_data = {}
    with open(os.path.join(INPUTS_DIR, "get_group_metadata.json")) as file:
        known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_group_metadata(
        year=2021, id="B117200"
    )
    assert test_result == known_good_data


def test_ctpp_get_data_cookIL_lakeIN():
    known_good_data = {}
    with open(os.path.join(INPUTS_DIR, "get_data_cookIL_lakeIN.json")) as file:
        known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_data(
        year=2021,
        get="B117200",
        origin=CTPPGeography.county(county="031", state="17"),
        destination=CTPPGeography.county(county="089", state="18"),
    )
    assert test_result == known_good_data


def test_ctpp_get_data_lakeIL_kaneIL():
    known_good_data = {}
    with open(os.path.join(INPUTS_DIR, "get_data_lakeIL_kaneIL.json")) as file:
        known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_data(
        year=2016,
        get=["a101101_e1", "a101101_e2"],
        origin=CTPPGeography.county(county="097", state="17"),
        destination=CTPPGeography.county(county="089", state="17"),
    )
    assert test_result == known_good_data


def test_ctpp_get_data_cookILTract1001_cookILTract1002():
    known_good_data = {}
    # with open(os.path.join(INPUTS_DIR, "# TODO: GET known good data")) as file:
    # known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_data(
        year=2021,
        get=["B303100_e1"],
        origin=CTPPGeography.tract(tract="*", county="031", state="17"),
        destination=CTPPGeography.tract(tract="*", county="097", state="17"),
    )
    print(test_result)
    assert test_result == known_good_data


def test_ctpp_get_data_cmap_counties():
    known_good_data = {}
    # with open(os.path.join(INPUTS_DIR, "# TODO: GET known good data")) as file:
    # known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_data(
        year=2021,
        get=["B303100_e1"],
        origin=CTPPGeography.cmap_counties(),
        destination=CTPPGeography.cmap_counties(),
    )
    assert test_result == known_good_data


def test_ctpp_get_data_geojson():
    known_good_data = {}
    # with open(os.path.join(INPUTS_DIR, "# TODO: GET known good data")) as file:
    # known_good_data = json.load(file)
    test_result = GENERIC_TEST_CLIENT.get_data(
        year=2021,
        get=["B303100_e1"],
        origin=CTPPGeography.cmap_counties(),
        destination=CTPPGeography.cmap_counties(),
        response_format="geojson",
    )
    assert test_result == known_good_data


if __name__ == "__main__":
    test_ctpp_get_data_cookILTract1001_cookILTract1002()
