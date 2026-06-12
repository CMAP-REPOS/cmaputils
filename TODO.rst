======
TODOS:
======

PACKAGING AND PUBLISHING
========================
* Set up GitHub Pages with Sphinx
* Fix Sphinx auto-generated documentation
* Make GitHub Repo public
* Publish to PyPi/Conda Forge (?)
* Write custom commit scripts for Bash and Powershell
* Fix pre-commit hooks
* Create default file/module template

DOCUMENTATION
=============
* Docstrings
  
  * CTPP classes and functions
  * API key functions
 
* Create "Contributors" guide
* Create "Maintainers" guide
* Add design documentation
* Use doctest to test docstring

TESTING
=======

* ADD: FIPS code update macro
* FIX: CTPP method tests
* ADD: Packaging/distribution tests
* ADD: Doctests

CENSUS
======

* Add ACS module
* Add LEHD module

CTPP
----

* CTPPClient.get_data() should return DataFrame
* CTPPClient.cmap_county_data() method for CTPP
* CTPPClient.cmap_tract_data() method for CTPP
* Fix CTPPClient tract level queries
* Finish CTPPGeography levels (place, PUMA, etc)
* Query batching
* Async query logic
* Query retry logic