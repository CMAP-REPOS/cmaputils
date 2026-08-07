"""
This script contains macros for generating Python code for CTPP queries.
These macros run as part of a pre-commit process and generate lists of
GeoIDs and FIPS codes to allow for concurrent CTPP requests and
input validation.
"""

# SECTION: External dependencies
import requests
import os
from pathlib import Path

# SECTION: Internal dependencies
from cmaputils.census.api_key import load_api_key_census

# SECTION: Constants

# FIPS endpoints
TRACT_FIPS_URL = "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=tract:*&in=county:*&in=state:*"
COUNTY_FIPS_URL = (
    "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=county:*&in=state:*"
)
STATE_FIPS_URL = (
    "https://api.census.gov/data/2024/acs/acs5?get=NAME&for=state:*"
)

# File paths
CMAPUTILS_PATH = Path(__file__).parent.parent.parent  # cmaputils root
CENSUS_SRC_DIR_PATH = os.path.join(CMAPUTILS_PATH, "src", "cmaputils", "census")
FIPS_MODULE_DIR_PATH = os.path.join(CENSUS_SRC_DIR_PATH, "fips")

# NOTE: In order to run this macro you must have an API
# for the Census in either a CENSUS_API_KEY env var or in a
# API_KEY env var
CONTRIBUTOR_ENV_PATH = os.path.join(
    CMAPUTILS_PATH, "contributors", "api_keys.env"
)
CONTRIBUTOR_API_KEY = load_api_key_census(env_path=CONTRIBUTOR_ENV_PATH)

# SOURCE: https://gist.github.com/rogerallen/1583593 (Copyright waived, public domain)
STATE_ABBREVIATIONS_DICT = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "Virgin Islands, U.S.": "VI",
}

# <Tab> character for proper formatting of dictionaries
TAB = " " * 4

# -- DOCSTRINGS FOR MODULES
COUNTY_FIPS_DOCSTRING = """# TODO: WRITE MODULE DOCSTRING ?"""
STATE_FIPS_DOCSTRING = """# TODO: WRITE MODULE DOCSTRING ?"""
TRACT_FIPS_DOCSTRING = """# TODO: WRITE MODULE DOCSTRING ?"""


# SECTION: Classes


class FipsFile:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.path = os.path.join(FIPS_MODULE_DIR_PATH, f"_{self.file_name}.py")

        os.makedirs(FIPS_MODULE_DIR_PATH, exist_ok=True)

    def _add_new_line(self, line: str):
        """
        Helper function: literally just adds a new line to the end of a string
        """
        return line + "\n"

    def _clear_file(self):
        """
        Helper function: clears the contents of the FIPS file
        """
        with open(self.path, "w", encoding="utf-8") as file:
            # all this does is clear the contents of the file if
            # if it exists, and if not, creates it
            pass

    def blank_line(self):
        """
        Helper function: literally just writes a blank line
        """
        with open(self.path, "a", encoding="utf-8") as file:
            file.write("\n")

    def write_line(self, line: str):
        """
        Helper function: writes a line to the file
        """
        with open(self.path, "a", encoding="utf-8") as file:
            # add new line char
            _line_to_write = self._add_new_line(line)
            file.write(_line_to_write)

    def line_count(self):
        """
        Returns the line count for the FIPS file
        """
        line_count = 0
        with open(self.path, "r") as file:
            line_count = sum(1 for line in file)

        return line_count


# SECTION: Functions


def _format_dict_entry(key: str, value: str) -> str:
    """
    Helper function: properly formats key and value
    into a dictionary entry line
    """
    formatted_dict_entry = f'{TAB}"{key}": "{value}",'
    return formatted_dict_entry


def get_county_fips():
    # TODO: ADD documentation

    api_response = requests.get(
        url=COUNTY_FIPS_URL, params={"key": CONTRIBUTOR_API_KEY}
    )

    # NOTE: here to give future maintainers hints about what to
    # fix if things break
    maintainers_message = """
    NOTE: AR: If you get an Exception for this macro, it is almost
     certainly because of ".raise_for_status()". If you get a '401'
     error, check your API key. Otherwise, this file likely needs
     to be edited or maintained! You may have to change the endpoint
     or something else to fix it!
    """

    try:
        api_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"{maintainers_message}\n{e}")

    # --- File setup
    COUNTY_FIPS_FILE = FipsFile(
        file_name="county"
    )  # don't need '_' in file_name because in init function

    # now writing counties to FIPS file
    COUNTY_FIPS_FILE._clear_file()
    COUNTY_FIPS_FILE.write_line(COUNTY_FIPS_DOCSTRING)
    COUNTY_FIPS_FILE.blank_line()

    # AR 06/12/26: Currently the endpoint returns a list of lists, where the
    # 0th item is the CSV headers, and then each subsequent sub-list is
    # a list of [NAME, state, county]
    counties = api_response.json()

    # list of unique states/territories from API response
    _all_county_state_names = [county[0] for county in counties[1:]]
    _all_state_names = [
        county_state_name.split(",")[1].strip()
        for county_state_name in _all_county_state_names
    ]
    unique_state_names = sorted(set(_all_state_names))

    # --- now writing FIPS code variables for each county

    COUNTY_FIPS_FILE.write_line("# SECTION: County FIPS code variables")
    COUNTY_FIPS_FILE.blank_line()

    for county in counties[1:]:  # 0th item is CSV headers
        county_state_name = county[0]  # comes as "Cook County, Illinois"
        county_fips = county[2]

        county_name = county_state_name.split(",")[0].strip()
        state_name = county_state_name.split(",")[1].strip()

        # NOTE: Some county names contain spaces and dashes, so need to
        # clean them to make them acceptable Python var names
        state_abbrev = STATE_ABBREVIATIONS_DICT[state_name]
        clean_county_name = (
            county_name.replace("-", "_")  # remove hyphens
            .replace("'", "")  # remove apostrophes
            .replace(".", "")  # remove periods
            .replace(" ", "_")  # remove spaces
            .upper()
        )
        county_var_name = clean_county_name + f"_{state_abbrev}"

        county_var_assignment_line = f'{county_var_name} = "{county_fips}"'
        COUNTY_FIPS_FILE.write_line(county_var_assignment_line)

    # --- now writing County FIPS codes in each state dicts

    COUNTY_FIPS_FILE.write_line("# SECTION: State County FIPS dictionaries")
    COUNTY_FIPS_FILE.blank_line()

    # grouping by state
    for state in unique_state_names:
        _clean_state_name = state.replace(" ", "_")
        state_var_name = f"{_clean_state_name}_COUNTY_CODES".upper()

        # IMPORTANT: next line opens dictionary
        COUNTY_FIPS_FILE.write_line(f"{state_var_name} = {{")

        for county in counties[1:]:
            _county_state_name = county[0]
            _state_name = _county_state_name.split(",")[1].strip()

            if _state_name == state:
                _county_name = _county_state_name.split(",")[0].strip()
                _county_fips = county[2]
                # properly format as: <Tab> "key": "value"
                _county_fips_dict_entry = _format_dict_entry(
                    key=_county_name, value=_county_fips
                )
                COUNTY_FIPS_FILE.write_line(_county_fips_dict_entry)

        # IMPORTANT: next line closes dictionary
        COUNTY_FIPS_FILE.write_line("}")
        COUNTY_FIPS_FILE.blank_line()

    # --- now writing dictionary to translate between state FIPS and
    # state county code dictionary (e.g., "17": ILLINOIS_COUNTY_CODES)
    COUNTY_FIPS_FILE.write_line("# SECTION: State FIPS to County Code Dicts")
    COUNTY_FIPS_FILE.blank_line()

    _state_fips_to_county_codes = {}

    # IMPORTANT: next line opens dictionary
    COUNTY_FIPS_FILE.write_line("STATE_FIPS_TO_COUNTY_CODE_DICTS = {")

    for state in unique_state_names:
        _clean_state_name = state.replace(" ", "_")
        state_var_name = f"{_clean_state_name}_COUNTY_CODES".upper()
        state_fips = ""

        for county in counties[1:]:
            _county_state_name = county[0]
            _state_name = _county_state_name.split(",")[1].strip()

            if _state_name == state:
                state_fips = county[1]

        # properly format as: <Tab> "key": "value"
        _state_fips_to_county_entry = f'{TAB}"{state_fips}": {state_var_name},'
        COUNTY_FIPS_FILE.write_line(_state_fips_to_county_entry)

    # IMPORTANT: next line closes dictionary
    COUNTY_FIPS_FILE.write_line("}")


def get_state_fips():
    # TODO: ADD documentation

    api_response = requests.get(
        url=STATE_FIPS_URL, params={"key": CONTRIBUTOR_API_KEY}
    )

    # NOTE: here to give future maintainers hints about what to
    # fix if things break
    maintainers_message = """
    NOTE: AR: If you get an Exception for this macro, it is almost
     certainly because of ".raise_for_status()". If you get a '401'
     error, check your API key. Otherwise, this file likely needs
     to be edited or maintained! You may have to change the endpoint
     or something else to fix it!
    """

    try:
        api_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"{maintainers_message}\n{e}")

    # --- File setup
    STATE_FIPS_FILE = FipsFile(
        file_name="state"
    )  # don't need '_' in file_name because in init function

    # now writing counties to FIPS file
    STATE_FIPS_FILE._clear_file()
    STATE_FIPS_FILE.write_line(STATE_FIPS_DOCSTRING)
    STATE_FIPS_FILE.blank_line()

    # AR 06/12/26: Currently the endpoint returns a list of lists, where the
    # 0th item is the CSV headers, and then each subsequent sub-list is
    # a list of [NAME, state]
    states = api_response.json()

    state_to_fips = {
        state[0]: state[1] for state in states[1:]
    }  # 0th item is CSV headers

    # --- Writing state FIPS code variables

    STATE_FIPS_FILE.write_line("# SECTION: State FIPS codes")
    STATE_FIPS_FILE.blank_line()

    for state_name, state_fips in state_to_fips.items():
        _clean_state_name = state_name.replace(" ", "_")
        state_var_name = f"{_clean_state_name}_FIPS".upper()

        STATE_FIPS_FILE.write_line(f'{state_var_name} = "{state_fips}"')

    STATE_FIPS_FILE.blank_line()

    # --- Writing dictionary

    STATE_FIPS_FILE.write_line("# SECTION: State to FIPS code Dictionary")
    STATE_FIPS_FILE.blank_line()

    # IMPORTANT: Next line opens dictionary
    STATE_FIPS_FILE.write_line("STATE_TO_FIPS = {")

    for state_name, state_fips in state_to_fips.items():
        _dict_entry = _format_dict_entry(key=state_name, value=state_fips)
        STATE_FIPS_FILE.write_line(_dict_entry)

    # IMPORTANT: Next line closes dictionary
    STATE_FIPS_FILE.write_line("}")


def get_tract_fips():
    # TODO: write tract fips function
    pass


def update_fips_codes():
    """
    Wrapper function: updates FIPS codes for all counties, states, tracts, etc. at
    commit-time.
    """

    # warn contributors if they do not have a "api_keys.env" file
    if not os.path.exists(CONTRIBUTOR_ENV_PATH):
        print(
            f"WARNING: You do not have an 'api_keys.env' file in"
            f" {os.path.join(CMAPUTILS_PATH, 'contributors')}."
            " If you choose to continue without creating this file,"
            " a number of important pre-commit hooks will be unable to run."
            "\nFIPS codes will not be updated if you choose to continue"
            " without creating an 'api_keys.env' file"
            f" at {CONTRIBUTOR_ENV_PATH}!\n"
        )

        contributors_choice = input(
            "Would you still like to continue with your commit? (y/[n]): "
        )
        contributors_choice = contributors_choice.strip().lower()

        if contributors_choice not in ["y", "yes"]:
            print("Thank you! Stopping your commit now")
            raise ValueError

    # now can run the main functions
    get_county_fips()
    get_state_fips()
    get_tract_fips()


if __name__ == "__main__":
    get_county_fips()
    get_state_fips()
