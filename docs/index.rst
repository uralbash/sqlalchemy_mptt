.. sqlalchemy_mptt documentation master file, created by
   sphinx-quickstart on Wed Jun 25 14:00:12 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

sqlalchemy_mptt
===============

.. image:: _static/mptt_insert.jpg
    :alt: MPTT (nested sets) INSERT

Library for implementing Modified Preorder Tree Traversal with your
`SQLAlchemy` Models and working with trees of Model instances, like
`django-mptt`.
The nested set model is a particular technique for representing nested
sets (also known as trees or hierarchies) in relational databases.

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

API:
----

.. toctree::
   :maxdepth: 2

   sqlalchemy_mptt

Tutorial
--------

.. toctree::

    tut_flask.rst

A lot of examples and logic in
:py:mod:`sqlalchemy_mptt.tests.cases`

Support and Development
=======================

.. toctree::

    CONTRIBUTING.rst

Changelog
=========

.. toctree::
    :maxdepth: 1

    CHANGES.rst
    CHANGES_OLD.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _ps_tree: https://github.com/sacrud/ps_tree
.. _pyramid_pages: https://github.com/uralbash/pyramid_pages
