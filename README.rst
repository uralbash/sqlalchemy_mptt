|PyPI Version| |PyPI Downloads| |PyPI Python Versions|
|Build Status| |Coverage Status|

Library for implementing Modified Preorder Tree Traversal with your
SQLAlchemy Models and working with trees of Model instances, like
django-mptt. Docs http://sqlalchemy-mptt.readthedocs.io/

.. image:: https://cdn.rawgit.com/uralbash/sqlalchemy_mptt/master/docs/img/2_sqlalchemy_mptt_traversal.svg
   :alt: Nested sets traversal
   :width: 800px

The nested set model is a particular technique for representing nested
sets (also known as trees or hierarchies) in relational databases.

Installing
----------

Install from github:

.. code-block:: bash

    pip install git+http://github.com/uralbash/sqlalchemy_mptt.git

PyPi:

.. code-block:: bash

    pip install sqlalchemy_mptt

Source:

.. code-block:: bash

    pip install -e .

Usage
-----

Add mixin to model

.. testsetup:: *

    engine = create_engine("sqlite:///:memory:")
    session = Session(engine)

.. testcode:: default,delete-node,update-node,move-inside,move-after,move-top

    from sqlalchemy import Column, Integer, Boolean
    from sqlalchemy.ext.declarative import declarative_base

    from sqlalchemy_mptt.mixins import BaseNestedSets

    Base = declarative_base()


    class Tree(Base, BaseNestedSets):
        __tablename__ = "tree"

        id = Column(Integer, primary_key=True)
        visible = Column(Boolean)

        def __repr__(self):
            return "<Node (%s)>" % self.id

.. testcode:: default,delete-node,update-node,move-inside,move-after,move-top
    :hide:

    Base.metadata.create_all(engine)
    tree_manager.register_events(remove=True)
    instances = [
        Tree(id=1, parent_id=None),
        Tree(id=2, parent_id=1),
        Tree(id=3, parent_id=2),
        Tree(id=4, parent_id=1),
        Tree(id=5, parent_id=4),
        Tree(id=6, parent_id=4),
        Tree(id=7, parent_id=1),
        Tree(id=8, parent_id=7),
        Tree(id=9, parent_id=8),
        Tree(id=10, parent_id=7),
        Tree(id=11, parent_id=10)
    ]
    for instance in instances:
        instance.left = 0
        instance.right = 0
        instance.visible = True
        instance.tree_id = 1
    session.add_all(instances)
    session.flush()
    tree_manager.register_events()
    Tree.rebuild_tree(session, tree_id=1)

Now you can add, move and delete obj!

Insert node
-----------

.. testcode::

    node = Tree(parent_id=6)
    session.add(node)

::

            level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19

            level     Insert node with parent_id == 6
            1                    1(1)24
                    _______________|_________________
                   |               |                 |
            2    2(2)5           6(4)13           14(7)23
                   |           ____|____          ___|____
                   |          |         |        |        |
            3    3(3)4      7(5)8    9(6)12  15(8)18   19(10)22
                                       |        |         |
            4                      10(23)11  16(9)17  20(11)21

Delete node
-----------

.. testcode:: delete-node

    node = session.query(Tree).filter(Tree.id == 4).one()
    session.delete(node)

::

            level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19

            level         Delete node == 4
            1                    1(1)16
                    _______________|_____
                   |                     |
            2    2(2)5                 6(7)15
                   |                     ^
            3    3(3)4            7(8)10   11(10)14
                                    |          |
            4                     8(9)9    12(11)13

Update node
-----------

.. testcode:: update-node

    node = session.query(Tree).filter(Tree.id == 8).one()
    node.parent_id = 5
    session.add(node)

::

            level           Nested sets example
                1                    1(1)22
                        _______________|___________________
                       |               |                   |
                2    2(2)5           6(4)11             12(7)21
                       |               ^                   ^
                3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                      |          |
                4                                  14(9)15   18(11)19

            level               Move 8 - > 5
                1                     1(1)22
                         _______________|__________________
                        |               |                  |
                2     2(2)5           6(4)15            16(7)21
                        |               ^                  |
                3     3(3)4      7(5)12   13(6)14      17(10)20
                                   |                        |
                4                8(8)11                18(11)19
                                   |
                5                9(9)10

Move node (support multitree)
-----------------------------

.. figure:: https://cdn.rawgit.com/uralbash/sqlalchemy_mptt/master/docs/img/3_sqlalchemy_mptt_multitree.svg
   :alt: Nested sets multitree
   :width: 600px

   Nested sets multitree

.. testcode:: move-inside,move-top
    :hide:

    tree_manager.register_events(remove=True)
    instances = [
        Tree(id=12, parent_id=None),
        Tree(id=13, parent_id=12),
        Tree(id=14, parent_id=13),
        Tree(id=15, parent_id=12),
        Tree(id=16, parent_id=15),
        Tree(id=17, parent_id=15),
        Tree(id=18, parent_id=12),
        Tree(id=19, parent_id=18),
        Tree(id=20, parent_id=19),
        Tree(id=21, parent_id=18),
        Tree(id=22, parent_id=21)
    ]
    for instance in instances:
        instance.left = 0
        instance.right = 0
        instance.visible = True
        instance.tree_id = 2
    session.add_all(instances)
    session.flush()
    tree_manager.register_events()
    Tree.rebuild_tree(session, tree_id=2)

Move inside

.. testcode:: move-inside

    node = session.query(Tree).filter(Tree.id == 4).one()
    node.move_inside("15")

::

                     4 -> 15
            level           Nested sets tree1
            1                    1(1)16
                    _______________|_____________________
                   |                                     |
            2    2(2)5                                 6(7)15
                   |                                     ^
            3    3(3)4                            7(8)10   11(10)14
                                                    |          |
            4                                     8(9)9    12(11)13

            level           Nested sets tree2
            1                     1(12)28
                     ________________|_______________________
                    |                |                       |
            2    2(13)5            6(15)17                18(18)27
                   |                 ^                        ^
            3    3(14)4    7(4)12 13(16)14  15(17)16  19(19)22  23(21)26
                             ^                            |         |
            4          8(5)9  10(6)11                 20(20)21  24(22)25

Move after

.. testcode:: move-after

    node = session.query(Tree).filter(Tree.id == 8).one()
    node.move_after("5")

::

           level           Nested sets example
                1                    1(1)22
                        _______________|___________________
                       |               |                   |
                2    2(2)5           6(4)11             12(7)21
                       |               ^                   ^
                3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                      |          |
                4                                  14(9)15   18(11)19

            level               Move 8 after 5
                1                     1(1)22
                         _______________|__________________
                        |               |                  |
                2     2(2)5           6(4)15            16(7)21
                        |               ^                  |
                3     3(3)4    7(5)8  9(8)12  13(6)14   17(10)20
                                        |                  |
                4                    10(9)11            18(11)19

Move to top level

.. testcode:: move-top

    node = session.query(Tree).filter(Tree.id == 15).one()
    node.move_after("1")

::

            level           tree_id = 1
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19

            level           tree_id = 2
            1                     1(15)6
                                     ^
            2                 2(16)3   4(17)5

            level           tree_id = 3
            1                    1(12)16
                     _______________|
                    |               |
            2    2(13)5          6(18)15
                    |               ^
            3    3(14)4     7(19)10   11(21)14
                               |          |
            4               8(20)9    12(22)13

Support and Development
=======================

To report bugs, use the `issue tracker
<https://github.com/uralbash/sqlalchemy_mptt/issues>`_.

We welcome any contribution: suggestions, ideas, commits with new
futures, bug fixes, refactoring, docs, tests, translations, etc...

If you have any questions:

* Use the `Discussion board <https://github.com/uralbash/sqlalchemy_mptt/discussions>`_
* Contact the maintainer via email: fayaz.yusuf.khan@gmail.com
* Contact the author via email: sacrud@uralbash.ru or #sacrud IRC channel |IRC Freenode|

Refer the detailed contribution guide in the `docs <https://sqlalchemy-mptt.readthedocs.io/CONTRIBUTING.html>`_
for more information on setting up the development environment, running tests, and contributing to the project.

License
=======

The project is licensed under the MIT license.

.. |PyPI Version| image:: https://img.shields.io/pypi/v/sqlalchemy_mptt
   :alt: PyPI - Version
.. |PyPI Downloads| image:: https://img.shields.io/pypi/dm/sqlalchemy_mptt
   :alt: PyPI - Downloads
.. |PyPI Python Versions| image:: https://img.shields.io/pypi/pyversions/sqlalchemy_mptt
   :alt: PyPI - Python Version
.. |Build Status| image:: https://github.com/uralbash/sqlalchemy_mptt/actions/workflows/run-tests.yml/badge.svg?branch=master
   :target: https://github.com/uralbash/sqlalchemy_mptt/actions/workflows/run-tests.yml
.. |Coverage Status| image:: https://coveralls.io/repos/uralbash/sqlalchemy_mptt/badge.png
   :target: https://coveralls.io/r/uralbash/sqlalchemy_mptt
.. |IRC Freenode| image:: https://img.shields.io/badge/irc-freenode-blue.svg
   :target: https://webchat.freenode.net/?channels=sacrud
