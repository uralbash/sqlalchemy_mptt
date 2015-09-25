Example
-------

Initalize
~~~~~~~~~

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
~~~~~~

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
~~~~~~~~~~~~~~

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

INSERT
~~~~~~

Insert node with parent_id==6

.. code-block:: python

    node = Tree(parent_id=6)
    session.add(node)

Tree state before insert

.. code::

    level           Before INSERT
    1                    1(1)22
            _______________|___________________
           |               |                   |
    2    2(2)5           6(4)11             12(7)21
           |               ^                   ^
    3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                          |          |
    4                                  14(9)15   18(11)19

After insert

.. code::

    level           After INSERT
    1                    1(1)24
            _______________|_________________
           |               |                 |
    2    2(2)5           6(4)13           14(7)23
           |           ____|___          ____|____
           |          |        |        |         |
    3    3(3)4      7(5)8    9(6)12  15(8)18   19(10)22
                               |        |         |
    4                      10(23)11  16(9)17   20(11)21

UPDATE
~~~~~~

Set parent_id=5 for node with id==8

.. code-block:: python

    node = session.query(Tree).filter(Tree.id == 8).one()
    node.parent_id = 5
    session.add(node)

Tree state before update

.. code::

    level           Before UPDATE
    1                    1(1)22
            _______________|___________________
           |               |                   |
    2    2(2)5           6(4)11             12(7)21
           |               ^                   ^
    3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                          |          |
    4                                  14(9)15   18(11)19

After update

.. code::

    level               Move 8 - > 5
        1                     1(1)22
                 _______________|__________________
                |               |                  |
        2     2(2)5           6(4)15            16(7)21
                |               ^                  |
        3     3(3)4      7(5)12   13(6)14      17(10)20
                           |                       |
        4                8(8)11                18(11)19
                           |
        5                9(9)10


DELETE
~~~~~~

Delete node with id==4

.. code-block:: python

    node = session.query(Tree).filter(Tree.id == 4).one()
    session.delete(node)

Tree state before delete

.. code::

    level           Before DELETE
    1                    1(1)22
            _______________|___________________
           |               |                   |
    2    2(2)5           6(4)11             12(7)21
           |               ^                   ^
    3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                          |          |
    4                                  14(9)15   18(11)19

After delete

.. code::

    level         Delete node == 4
    1                    1(1)16
            _______________|_____
           |                     |
    2    2(2)5                 6(7)15
           |                     ^
    3    3(3)4            7(8)10   11(10)14
                            |          |
    4                     8(9)9    12(11)13

For more example see :mod:`sqlalchemy_mptt.tests.TestTree`


SESSION
~~~~~~~

To work correctly after flush you should use :mod:`sqlalchemy_mptt.mptt_sessionmaker`

.. code-block:: python
    :linenos:

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy_mptt import mptt_sessionmaker

    engine = create_engine('...')
    Session = mptt_sessionmaker(sessionmaker(bind=engine))
