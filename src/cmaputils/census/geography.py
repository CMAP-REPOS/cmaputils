"""
This modele contains Classes that make it easier to work with
Census geographies
"""

from __future__ import annotations  # has to go here because __future__ is weird

"""
Author: Aaron Rumph
Date: 06/16/2026
Description: Module containing the source code for Census
    geography representations
Input Files: N/A
Output Files: N/A
"""

# SECTION: External dependencies
from dataclasses import dataclass, field
from enum import StrEnum

# SECTION: Internal dependencies

# SECTION: Constants

# -- Useful fipscodes
CMAP_COUNTY_CODES = ["031", "089", "043", "097", "093", "111", "197"]

# SECTION: Classes


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


@dataclass(frozen=True)  # immutable after construction
class CensusGeography:
    """
    Geography class used to build CTPP queries (see CTPP.get_data for examples)

    Examples
    -----
    >>> CensusGeography.state(fips="17") # get Illinois CensusGeography object

    >>> CensusGeography.county(state="17", county="031") # get Cook County CensusGeography object

    Methods
    -----
    state(fips)
        Get state CensusGeography object

    county(state, county)
        Get state CensusGeography object

    tract(tract, county, state)
        Get state CensusGeography object
    """

    level: SummaryLevel = field(default=SummaryLevel.COUNTY)
    fips: str | int | list[int] = field(default="*")
    within: dict[SummaryLevel, str | int | list[int]] = field(
        default_factory={SummaryLevel.STATE: "17"}
    )

    @classmethod
    def state(cls, fips: str | list[str]) -> CensusGeography:
        # TODO: ADD documentation
        return CensusGeography(
            level=SummaryLevel.STATE, fips=_format_fips(fips)
        )

    @classmethod
    def county(
        cls,
        county: str | list[str] = "*",
        *,
        state: str | list[str],
    ) -> CensusGeography:
        # TODO: ADD Documentation
        return CensusGeography(
            level=SummaryLevel.COUNTY,
            fips=_format_fips(county),
            within={SummaryLevel.STATE: _format_fips(state)},
        )

    @classmethod
    def tract(
        cls,
        tract: str | list[str] = "*",
        *,
        county: str | list[str] = "*",
        state: str | list[str],
    ):
        # TODO: ADD documentation
        return CensusGeography(
            level=SummaryLevel.TRACT,
            fips=_format_fips(tract),
            within={
                SummaryLevel.STATE: _format_fips(state),
                SummaryLevel.COUNTY: _format_fips(county),
            },
        )

    @classmethod
    def taz(args):
        pass

    @classmethod
    def place(
        cls, place_fips: str | list[str], state: str | list[str]
    ) -> CensusGeography:
        # TODO: ADD documentation
        return CensusGeography(
            level=SummaryLevel.PLACE,
            fips=_format_fips(place_fips),
            within={SummaryLevel.STATE: _format_fips(state)},
        )

    def cmap_counties():
        """
        Get county-level geography for the 7 county CMAP area.
        """
        return CensusGeography(
            level=SummaryLevel.COUNTY,
            fips=_format_fips(CMAP_COUNTY_CODES),
            within={SummaryLevel.STATE: _format_fips("17")},
        )


# SECTION: Functions


def _census_geography_to_params(
    geography: CensusGeography, origin_or_destination: str
) -> list[tuple[str, str]]:
    """
    Helper function: turns CensusGeography object into params dict.
    `origin_or_destination` must be either 'origin' or 'destination'
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


def _format_fips(fips: str | list[str]) -> str:
    """Helper function: formats inputted fips for query"""
    if isinstance(fips, str):
        return fips
    elif isinstance(fips, list) and all(
        (isinstance(code, str) for code in fips)
    ):
        return ",".join(fips)
    else:
        raise TypeError("Provided fips code must be of type str or list[str]")
