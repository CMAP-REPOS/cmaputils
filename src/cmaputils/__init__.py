def hello() -> str:
    return "Hello from cmaputils!"


# TODO: import useful functions and constants to top level namespace
from .census.ctpp import CTPPClient, CTPPGeography
from .census.api_key import load_api_key_census, load_api_key_ctpp
