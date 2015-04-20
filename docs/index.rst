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

Project uses sqlalchemy_mptt
----------------------------

* ps_pages_

.. raw:: html

    <br clear="all" />

.. include:: example.rst

A lot of examples and logic in :py:mod:`sqlalchemy_mptt.tests.tree_testing_base`

.. include:: contribute.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _ps_pages: https://github.com/ITCase/ps_pages
