"""
This module is meant to test that the functions/methods/classes from /src/cmaputils/census/api_key.py work.
"""

"""
Author: Aaron Rumph
Date: 05/26/2026
Description: Module containing tests for API key functions/classes/methods
Input Files: N/A
Output Files: N/A
"""

# - External dependencies
import pytest
import dotenv
import os

# - Internal dependencies
from cmaputils.census.api_key import load_api_key_ctpp, load_api_key_census

# - Constants
SAMPLE_CTPP_API_KEY = "abcdefghijklmnopqrstuvwx"  # 24-char
SAMPLE_CENSUS_API_KEY = "abcdefghijklmnopqrstuvwxyzabcdefghijklmn"  # 40-char

# - Setup


# - Tests
def test_load_ctpp_key_from_env():
    # check environment variable for CTPP_API_KEY
    os.environ["CTPP_API_KEY"] = SAMPLE_CTPP_API_KEY
    assert load_api_key_ctpp() == SAMPLE_CTPP_API_KEY


def test_load_ctpp_key_from_file():
    test_env_file_path = os.path.join("tests", "census", "inputs", "sample.env")
    assert load_api_key_ctpp(env_path=test_env_file_path) == SAMPLE_CTPP_API_KEY


def test_load_ctpp_key_from_str():
    assert load_api_key_ctpp(SAMPLE_CTPP_API_KEY) == SAMPLE_CTPP_API_KEY


def test_load_census_key_from_env():
    os.environ["CENSUS_API_KEY"] = SAMPLE_CENSUS_API_KEY
    assert load_api_key_census() == SAMPLE_CENSUS_API_KEY


def test_load_census_key_from_file():
    test_env_file_path = os.path.join("tests", "census", "inputs", "sample.env")
    assert (
        load_api_key_census(env_path=test_env_file_path)
        == SAMPLE_CENSUS_API_KEY
    )


def test_load_census_key_from_str():
    assert load_api_key_census(SAMPLE_CENSUS_API_KEY) == SAMPLE_CENSUS_API_KEY
