.. _examples:

========
Examples
========

This page contains examples for some of the tools in :mod:`cmaputils`.

Census
******

CTPP
====

CTPPClient construction
-----------------------

.. code:: python

   # to construct with explicit API key
   EXAMPLE_KEY = "abcdefghijklmnopqrstuvwx"
   example_client = CTPPClient(api_key=EXAMPLE_KEY)
   
   # to construct with .env file
   EXAMPLE_PATH = "~/api_keys.env"
   example_client = CTPPClient(env_path=EXAMPLE_PATH)

   # to construct with a 'API_KEY' or 'CTPP_API_KEY' env var
   example_client = CTPPClient()

County Flows
------------

.. code:: python

   # to get table 'B117200' from 2021 for workers going from
   # Cook County, IL to Lake County, IN
   example_client = CTPPClient()
   example_data = example_client.get_data(
        year=2021,
        get="B117200",
        origin=CTPPGeography.county(county="031", state="17"),
        destination=CTPPGeography.county(county="089", state="18"),
    )
   
   # to get variables 'a101101_e1' and 'a101101_e2' from 2016 for workers
   # going from all counties in Illinois to all counties in Indiana
   example_data_2 = example_client.get_data(
        year=2016,
        get=["a101101_e1", "a101101_e2"],
        origin=CTPPGeography.county(state="17"),
        destination=CTPPGeography.county(state="18"),
    )

Tract Flows
-----------

.. code:: python

   # to get table 'B303100' from 2021 for workers going from
   # Cook County, IL to Kane County, IL at the tract level
   example_client = CTPPClient()
   example_data = example_client.get_data(
        year=2021,
        get="B303100",
        origin=CTPPGeography.tract(county="031", state="17"),
        destination=CTPPGeography.tract(county="089", state="17"),
    )
   
   # to get table 'B303100' from 2021 for workers going from
   # Cook County, IL to Kane County, IL at the tract level
   # for tract 1001 in both counties
   example_client = CTPPClient()
   example_data = example_client.get_data(
        year=2021,
        get="B303100",
        origin=CTPPGeography.tract(tract="1001", county="031", state="17"),
        destination=CTPPGeography.tract(tract="1001", county="089", state="17"),
    )
   


