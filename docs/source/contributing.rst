============
Contributing
============

Requirements
============

1. U.S. Census API Key in ``contributors/api_keys.env``:
   If you do not have a Census API key, you should get one so that you can 
   run the commit script (which will properly update FIPS codes)

2. Must have uv setup:
   In order to make life easier in terms of dependency and environment 
   management, please use ``uv``. 

Repo branches and work organization
===================================

There are two major branches for the `cmaputils` repo: `main` and `dev`.
The `main` branch is the primary (i.e., consumable) branch, with
only production-ready code. The `dev` branch is a place for code that has
not yet been properly tested or documented, but is 'complete'.

Outside of the major branches, there are `working/...` branches. These
branches are places for code you are actively working on. When adding a 
feature, or contributing to `cmaputils`, please create a new working branch
with the name of the feature or change you are making. For instance, if
you want to add a submodule that handles LEHD API requests, please create a
`working/lehd` branch, or if you are adding documentation to an existing module
you might name your branch `working/lehd-docs`.

Once you feel that your code is ready to be merged, please feel free to 
merge it into the `dev` branch yourself (you should be able to do so, but if
you are unable to, contact the primary maintainer). Once in `dev`, please document
your code properly using docstrings and sphinx. You should use NumPy docstring
format, and adequately update the proper documentation in ``docs/source``.
Once you have properly documented your code (and ideally, tested), please submit
a pull request, requesting to have the `dev` branch merged into the `main`
branch.

Code style and formatting
=========================

For general guidelines about code style please see 
:ref:`the style guide <style-guide>`. In general the best
way to make sure your code is formatted correctly is to run:

.. code:: shell

   $ uv format --preview-features format

In order to lint your code you can run the following 
from the project root:

.. code:: shell 

   $ uv run ruff check .

This will show you a list of things to fix. If you are lazy (and trust ruff)
you can run

.. code:: shell

   $ uv run ruff check --fix

Workflow and tools
==================

Generally, your workflow for contributing to `cmaputils` will consist of the 
following:

* Sync local repo with remote repo
* Sync your environment (using ``uv``)
* Make changes
* Format and lint (using ``ruff``)
* Merge to `dev` branch
* Update documentation and tests
* Submit pull request for `main` branch
* Changes get merged (congrats, you're done!)
