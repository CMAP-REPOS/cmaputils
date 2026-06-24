.. _usage-guide:

=====
Usage
=====

This page contains detailed instructions for usage of the various features of ``cmaputils``

Census
******

FIPS
====

You can use ``cmaputils`` to get all the FIPS codes for any state in the US (and DC + PR).
You can do so by importing the FIPS code you want from :mod:`cmaputils.fips` with the following:

.. code:: python 

   # for Cook County, IL and Illinois' FIPS codes
   from cmaputils.fips import COOK_COUNTY_IL, ILLINOIS_FIPS

   # for all FIPS codes (WARNING: LITERALLY THOUSANDS OF FIPS CODES)
   from cmaputils.fips import *

   # for county X in state Y (Where Y is that state's abbreviation)
   from cmaputils.fips import X_COUNTY_Y

   # for state Z (Where Z is the unabbreviated state name)
   from cmaputils.fips import Z_FIPS

ACS
===

The best way to use the :mod:`cmaputils` ACS module is to import the package,
or the Classes you need, into your Python script. First, make sure you have 
properly installed the :mod:`cmaputils` package into your Python environment
(if you have not yet done so, follow the :ref:`installation guide <install-guide>`)
You can then import the package using the following at the top of your Python file:

.. code:: python

   import cmaputils

Or, you can use the following to just get the necessary classes for
working with ACS queries:

.. code:: python

   from cmaputils import ACSClient, ACSProduct, CensusGeography

Now you can get ACS data! 


Creating a ACSClient object
----------------------------

Before talking about function signatures and technical details, here's a brief overview
of how using :mod:`cmaputils` ACS tools works. First, you will need to create
a :class:`.ACSClient` object. When constructing this :class:`.ACSClient` object, you will have the option
to explicitly provide a Census API key or a path (relative or absolute) to a ``.env`` file containing a 
Census key. If neither of these options is provided, the constructor will automatically look for
a Census API key in your environment variables. 

**IMPORTANT**: A Census API Key is required! If you are providing a path to a ``.env`` file or 
not providing any constructor arguments, please ensure your CTPP API key environment variable is 
named either: ``CENSUS_API_KEY`` **or** ``API_KEY``.

You can thus construct the :class:`.ACSClient` object in any one of these three methods:

.. code:: python

   # provide explicit API key argument on construction:
   example_client = ACSClient(api_key=YOUR_API_KEY)

   # provide .env file path
   example_client = ACSClient(env_path=PATH_TO_YOUR_ENV_FILE)

   # look for environment variable
   example_client = ACSClient()


Query ACS Using Client
^^^^^^^^^^^^^^^^^^^^^^

Now that you have a :class:`.CTPPClient` object, you can use the class' methods to query the CTPP API.
You can find a list of methods in the docstrings for the :class:`.ACSClient` class, which you can easily
view by hovering over :class:`.ACSClient` in your editor.

**Supported ACSClient Methods Include**:
* get_data()

get_data()
""""""""""

To get ACS data, you can use the :meth:`.ACSClient.get_data`
method. The :meth:`.ACSClient.get_data` requires four arguments, and will throw an execption
if the following are not provided: *year*, *get*, *product*, and *geography*.

You can get data using the following convention:

.. code:: python

   example_client = ACSClient()
   returned_data = example_client.get_data(
        year=DATASET_YEAR, 
        get=VARIABLE_OR_TABLE_TO_GET, 
        product=ACSProduct.PRODUCT_TO_USE, # e.g., ACS5
        geography=CensusGeography.GEOGRAPHY_TO_USE, # e.g., tract
   )
    
Note that the ``geography`` argument should be :class:`cmaputils.CensusGeography`
instances. You can construct the :class:`.CensusGeography` instance in the 
function arguments like so:

.. code:: python

   example_result = example_client.get_data(
        year=2024, 
        get="S1501", 
        product=ACSProduct.ACS5,
        geography=CensusGeography.county(county="031", state="17"), 
   )

Also note that the ``product`` argument should be :class:`cmaputils.ACSProduct`
instances. You can construct the :class:`.ACSProduct` instance in the 
function arguments like so:
For more examples see :ref:`examples <example-guide>`.

CTPP
====

The best way to use the :mod:`cmaputils` CTPP module is to import the package,
or the Classes you need, into your Python script. First, make sure you have 
properly installed the :mod:`cmaputils` package into your Python environment
(if you have not yet done so, follow the :ref:`installation guide <install-guide>`)
You can then import the package using the following at the top of your Python file:

.. code:: python

   import cmaputils

Or, you can use the following to just get the necessary classes for
working with CTPP queries:

.. code:: python

   from cmaputils import CTPPClient, CensusGeography

Now you can query the CTPP! 


Creating a CTPPClient object
----------------------------

Before talking about function signatures and technical, here's a brief overview
of how using :mod:`cmaputils` CTPP tools works. First, you will need to create
a :class:`.CTPPClient` object. When constructing this :class:`.CTPPClient` object, you will have the option
to explicitly provide a CTPP API key or a path (relative or absolute) to a ``.env`` file containing a 
CTPP API key. If neither of these options is provided, the constructor will automatically look for
a CTPP API key in your environment variables. 

**IMPORTANT**: A CTPP API Key is required! If you are providing a path to a ``.env`` file or 
not providing any constructor arguments, please ensure your CTPP API key environment variable is 
named either: ``CTPP_API_KEY`` **or** ``API_KEY``.

You can thus construct the :mod:`.CTPPClient` object in any one of these three methods:

.. code:: python

   # provide explicit API key argument on construction:
   example_client = CTPPClient(api_key=YOUR_API_KEY)

   # provide .env file path
   example_client = CTPPClient(env_path=PATH_TO_YOUR_ENV_FILE)

   # look for environment variable
   example_client = CTPPClient()


Query CTPP Using Client
^^^^^^^^^^^^^^^^^^^^^^^

Now that you have a :class:`.CTPPClient` object, you can use the class' methods to query the CTPP API.
You can find a list of methods in the docstrings for the :class:`.CTPPClient` class, which you can easily
view by hovering over :class:`.CTPPClient` in your editor.

**Supported CTPPClient Methods Include**:

* list_datasets()    
* get_dataset_metadata()
* list_groups_in_dataset()
* get_group_metadata()
* get_data()

*Note: more thorough documentation for methods coming soon.
For now, focusing on* :meth:`.CTPPClient.get_data` *documentation.*

get_data()
""""""""""

To get CTPP data, you can use the :meth:`.CTPPClient.get_data`
method. The :meth:`.CTPPClient.get_data` requires two arguments, and will throw an execption
if either is not provided: *year* and *get*. 

You can get data using the following convention:

.. code:: python

   example_client = CTPPClient()
   returned_data = example_client.get_data(year=DATASET_YEAR, get=VARIABLE_OR_TABLE_TO_GET, 
      origin=ORIGIN_GEOGRAPHY, destination=DESTINATION_GEOGRAPHY)
    
Note that the ``origin`` and ``destination`` arguments should be :class:`cmaputils.CensusGeography`
instances. You can construct the origin or destination :class:`.CensusGeography` instance in the 
function arguments like so:

.. code:: python

   example_result = example_client.get_data(year=2021, get="B117200", 
      origin=CensusGeography.county(state="17"), destination=CensusGeography.county("031", state="17"))

For more examples see :ref:`examples <example-guide>`.
