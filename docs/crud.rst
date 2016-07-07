CRUD
====

INSERT
------

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
------

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
------

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
