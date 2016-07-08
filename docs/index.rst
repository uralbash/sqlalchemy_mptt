.. sqlalchemy_mptt documentation master file, created by
   sphinx-quickstart on Wed Jun 25 14:00:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

sqlalchemy_mptt
===============

.. image:: _static/mptt_insert.jpg
    :width: 450px
    :alt: MPTT (nested sets) INSERT
    :align: right

Library for implementing Modified Preorder Tree Traversal with your
`SQLAlchemy` Models and working with trees of Model instances, like
`django-mptt`.
The nested set model is a particular technique for representing nested
sets (also known as trees or hierarchies) in relational databases.

API:
----

.. toctree::
   :maxdepth: 4

   sqlalchemy_mptt

Where used
----------

* ps_tree_
* pyramid_pages_
* your project ...

Manual
------

.. toctree::

    initialize.rst
    crud.rst

Tutorial
--------

.. toctree::

    tut_flask.rst

A lot of examples and logic in
:py:mod:`sqlalchemy_mptt.tests.tree_testing_base`

Support and Development
=======================

To report bugs, use the `issue tracker
<https://github.com/uralbash/sqlalchemy_mptt/issues>`_.

We welcome any contribution: suggestions, ideas, commits with new
futures, bug fixes, refactoring, docs, tests, translations, etc...

If you have question, contact me sacrud@uralbash.ru or #sacrud IRC
channel |IRC Freenode|

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _ps_tree: https://github.com/sacrud/ps_tree
.. _pyramid_pages: https://github.com/uralbash/pyramid_pages
.. |IRC Freenode| image:: https://img.shields.io/badge/irc-freenode-blue.svg
   :target: https://webchat.freenode.net/?channels=sacrud
