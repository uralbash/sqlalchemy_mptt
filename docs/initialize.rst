Initalize
=========

Create model with MPTT mixin:

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


It automatically registers events.

Events
------

But you can do it manually:

.. code-block:: python

   from sqlalchemy_mptt import tree_manager

   tree_manager.register_events()  # register events before_insert,
                                   # before_update and before_delete

Or disable events if it required:

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

Filling data at the first time
------------------------------

When you add any data to the database, he tries to be counted lft,
rgt and level attribute. This is done very quickly if the tree already
exists in the database, but it is absolutely not allowed for initialize
the tree, it is very long. In this case, you can change the code like
this:

.. no-code-block:: python

    from sqlalchemy_mptt import tree_manager

    ...

    tree_manager.register_events(remove=True) # Disable MPTT events

    # Fill tree
    for item in items:
        item.left = 0
        item.right = 0
        item.tree_id = 'my_tree_1'
        db.session.add(item)
    db.session.commit()

    ...

    tree_manager.register_events() # enabled MPTT events back
    models.MyModelTree.rebuild_tree(db.session, 'my_tree_1') # rebuild lft, rgt value automatically

After an initial table with tree you can use mptt features.

Session
-------

For the automatic tree maintainance triggered after session flush to work
correctly, wrap the Session factory with :mod:`sqlalchemy_mptt.mptt_sessionmaker`

.. code-block:: python
    :linenos:

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy_mptt import mptt_sessionmaker

    engine = create_engine('...')
    Session = mptt_sessionmaker(sessionmaker(bind=engine))
