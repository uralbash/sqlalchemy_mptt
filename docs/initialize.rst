Initalize
=========

Create model with MPTT mixin and register events.

.. code-block:: python
    :linenos:

    from sqlalchemy import Column, Integer, Boolean
    from sqlalchemy.ext.declarative import declarative_base

    from sqlalchemy_mptt.mixins import BaseNestedSets

    Base = declarative_base()


    class Tree(Base, BaseNestedSets):
        __tablename__ = "tree"

        id = Column(Integer, primary_key=True)
        visible = Column(Boolean)  # you custom field

        def __repr__(self):
            return "<Node (%s)>" % self.id

Events
------

Events registered automatically, but you can do it manually:

.. code-block:: python

   from sqlalchemy_mptt import tree_manager

   tree_manager.register_events()  # register events before_insert,
                                   # before_update and before_delete

Or remove events if it required:

.. code-block:: python

   from sqlalchemy_mptt import tree_manager

   tree_manager.register_events(remove=True)  # remove events before_insert,
                                              # before_update and before_delete

Data structure
--------------

Fill table with records, for example, as shown in the picture

.. image:: img/2_sqlalchemy_mptt_traversal.svg
    :width: 500px
    :alt: SQLAlchemy MPTT (nested sets)
    :align: left

Represented data of tree like dict

.. code-block:: python

    tree = (
        {'id':  '1',                  'parent_id': None},

        {'id':  '2', 'visible': True, 'parent_id':  '1'},
        {'id':  '3', 'visible': True, 'parent_id':  '2'},

        {'id':  '4', 'visible': True, 'parent_id':  '1'},
        {'id':  '5', 'visible': True, 'parent_id':  '4'},
        {'id':  '6', 'visible': True, 'parent_id':  '4'},

        {'id':  '7', 'visible': True, 'parent_id':  '1'},
        {'id':  '8', 'visible': True, 'parent_id':  '7'},
        {'id':  '9',                  'parent_id':  '8'},
        {'id': '10',                  'parent_id':  '7'},
        {'id': '11',                  'parent_id': '10'},
    )

Session
-------

To work correctly after flush you should use :mod:`sqlalchemy_mptt.mptt_sessionmaker`

.. code-block:: python
    :linenos:

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy_mptt import mptt_sessionmaker

    engine = create_engine('...')
    Session = mptt_sessionmaker(sessionmaker(bind=engine))
