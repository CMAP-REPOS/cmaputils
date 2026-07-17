.. _style-guide:

===========
Style Guide
===========

These style guidelines are for contributors to `cmaputils`
to ensure that code is consistent (at least, consistent enough)
no matter who writes it. This ensures that others can properly
maintain and audit the code you write, so please follow these
guidelines!

Python style guide
******************

In general, formatting your code with `ruff` should catch 
most possible errors. Please consult `ruff` for a full list of
rules but the trivial/superficial stuff in brief:

* Spaces not tabs (you can set your editor up so it emits
  spaces instead of tabs). Four (4) spaces = One tab.
* Line length of 80 characters 
  (helps avoid long unreadable lines).
* Use blank lines to seperate between different 'sentences' 
  (i.e., if a few lines of code are part of the 'same thought', 
  they can go together. Otherwise, put a blank line in between
  to show that they are different parts/steps in your code).
* Use lower case snake case for functions and variables, and Pascal
  case for Classes.
* Constants should be capitalized.


Code comments
=============

Generally, you should use code comments to explain *why* your
code is written the way it is, i.e., to give the reader an 
idea of why you wrote it that way, rather than to explain *what* 
your code does. Imagine that you are the next person to read the
code with no idea why it's written; wouldn't you want to know
why the author wrote something?

Formatted comments
------------------

There are a number of types of comments you may wish to write.
These include notes for those reading the code that do not directly
comment on the code, comments about known bugs, or TODO notes. 
You should comment these as follows:

.. code:: python

   # TODO: This is a TODO comment.
   # SECTION: This is a comment that marks a new section 
   # BUG: This comment gives information about known bugs
   # PERF: This comment gives information about performance considerations.
   # NOTE: This comment contains notes for the reader.
   # FIX: This comment tells the reader to fix a particular issue.
   # TEST: This comment gives the reader information about testing status.

You can almost always set your editor to find all such comments and highlight
them in a special way so that they pop out more! If you use VSCode, you can
use 
`this extension <https://marketplace.visualstudio.com/items?itemName=wayou.vscode-todo-highlight>`_ 
to set up highlighting these comments (good practice).

   
Naming conventions
==================

When naming variables, functions, and classes, you should always
use descriptive names. In the age of modern editors, you should 
prefer longer, more descriptive names over shorter less 
descriptive ones. For example, if you have a variable representing
Illinois' population total, you should prefer `il_pop_total` or 
`illinois_pop_total` over `pop`, or worse yet, `p`.

You should also try as hard as possible to avoid 'magic numbers';
if you are using Illinois' population total, make a variable called
`ILLINOIS_POP_TOTAL` and use that rather than writing `12719141` 
all over your code.

Sections
========

When writing a new module/file for `cmaputils` please make sure
you include the following sections (all but the docstring and module info
should be preceeded by '# SECTION: '):

1. A docstring located at the top of the module, containing information 
    about the module. 
2. Module info: a short multiline comment containing author, date updated,
    and other useful info (see source code in src/cmaputils/census/ctpp.py
    for example).
3. External dependencies (# SECTION: External dependencies)
4. Internal dependencies (# SECTION: Internal dependencies)
5. Constants (# SECTION: Constants)
6. Classes (# SECTION: Classes)
7. Functions (# SECTION: Functions)

