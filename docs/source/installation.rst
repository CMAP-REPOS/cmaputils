.. _install-guide:

============
Installation
============

The best way to install cmaputils is by cloning this
repository, and then installing it to a python environment with pip/uv.
This will require you to open your terminal and run a few commands.

Requirements:
=============

* Git (or gh, the GitHub CLI)
* Python
* uv, Conda, Mamba, or Pip
* Access to the CMAP-REPOS GitHub organization

Setup and Organization:
=======================
First things first, you will need to download the source code for the cmaputils package.
If you do not already have one, I recommend creating a folder/directory where you can put other people's
repositories/code. The recommended location to create yours is at C:\Users\YOUR_NAME\Repos (or ~/Repos for Linux),
however you are free to choose whether or not to create such a directory, as well as where it should be.

Once you've decided where to place the source code for cmaputils, you can now open your terminal (use the Terminal app
on Windows, or your preferred terminal/shell on Linux). Next, change directories through the terminal to the location
you would like the source code to go. On Windows, this can be achieved in the terminal with:

.. code:: shell

    $ cd PATH\TO\YOUR\DESIRED\LOCATION

for example:

.. code:: shell 

   $ cd C:\Users\Aaron\Repos

Once you have changed directories to your desired location, you can clone the cmaputils repository. If you do not 
already have Git installed, follow `these installation instructions <https://git-scm.com/install/>`_ to download it.
Next clone the ``cmaputils`` repository with the following command:

.. code:: shell

   $ git clone https://github.com/CMAP-REPOS/cmaputils.git

You can then change directories into the newly created ``cmaputils`` directory with:

.. code:: shell

   $ cd cmaputils

Install to Python Environment:
==============================

Now that you've cloned the repository, you can install it into the Python environment of your choosing. You should use
``pip`` or ``uv`` to do this. If you normally use Conda or Mamba to manage Python environments see :ref:`conda-instructions`.
Now, from inside the ``cmaputils`` directory, activate your chosen Python environment. If you are using venv on Windows:

.. code:: powershell

    $ PATH\TO\YOUR\VENV\Scripts\activate.ps1

If you are using uv:

.. code:: powershell

   $ uv sync

If you are using bash:

.. code:: bash

   $ source PATH/TO/YOUR/VENV/Scripts/activate

Next you can install ``cmaputils`` as a package in your (now activated) Python environment by running the following with
pip:

.. code:: shell 

   $ pip install . 

Or if you're using uv:

.. code:: shell

   $ uv pip install .


.. _conda-instructions:

Conda/Mamba Instructions:
^^^^^^^^^^^^^^^^^^^^^^^^^
In order to install the package with Conda or Mamba, you will need to install ``pip`` in your Conda/Mamba environment.
Mamba and Conda are interchangable for these purposes, so if you are using Mamba, simply replace 
``conda`` with ``mamba`` in all subsequent commands. First, activate your environment with:

.. code:: shell

   $ conda activate YOUR_ENV_NAME

Next, install pip in your environment by running:

.. code:: shell

   $ conda install pip 

Then, use pip to install the package to your current environment by targeting the active environment with:

.. code:: shell

   $ python -m pip install .

You should know be able to use the ``cmaputils`` package in this environment! Just make sure you activate your 
environment before running any code that uses the package.
