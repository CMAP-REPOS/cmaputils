.. _documentation-guide:

=================
Documentation
=================

The best way to view the documentation for this project is to look in the ``docs`` directory on the project's GitHub page
or follow the links in the README.

For technical details, you can find more documentation for the various classes, functions,
modules, classes, etc. in :ref:`the usage guide <usage-guide>`. You can also find more 
detailed usage documentation (parameters, etc.) in the docstrings for classes, functions, modules,
and functions. You can find these by installing ``cmaputils`` to your Python environment, and
hovering over the names of classes, etc. in just about every editor, including VSCode, PyCharm, and
more.

For advanced users, if you would like to use ``sphinx`` to view the documentation (recommended for links to function
properly), do the following: 

1. If you do not already have ``sphinx`` installed to your Python environment, activate the Python environment of your
choosing, and then run:

.. code:: shell

    $ pip install sphinx furo

2. Go to the ``cmaputils`` directory:

.. code:: shell

    $ cd PATH\TO\cmaputils
    
3. Build the Sphinx docs:

.. code:: shell

    # (If you are on Windows, replace forward slashes '/' with back slashes '\')

    $ sphinx-build -b html docs/source docs/build 

4. Serve the docs locally:

.. code:: shell

    # (If you are on Windows, replace forward slashes '/' with back slashes '\')

    $ python -m http.server 8000 --directory docs/build

5. View the docs in your browser:
Open your browser and type in 'localhost:8000' in the URL bar

*NOTE: because this package is still early in development, some of the documentation may not be fully
complete. If you encounter any problems with documentation, or have any questions, contact 
`arumph@cmap.illinois.gov <mailto:arumph@cmap.illinois.gov>`_*

Auto-Generated Docs
===================

*Warning: these docs are partially 
automatically generated from docstrings in the* ``cmaputils`` *code.
There may be mistakes or incomplete documentation*.

.. automodule:: cmaputils
   :member
