#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
test tree
"""
import unittest

from sqlalchemy import Column, create_engine, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from mixins import BaseNestedSets

Base = declarative_base()


class Tree(Base, BaseNestedSets):
    __tablename__ = "tree"

    id = Column(Integer, primary_key=True)

Tree.register_tree()


def add_fixture(model, fixtures, session):
    """
    Add fixtures to database.

    Example::

    hashes = ({'foo': {'foo': 'bar', '1': '2'}}, {'foo': {'test': 'data'}})
    add_fixture(TestHSTORE, hashes)
    """
    session.query(model).delete()
    session.commit()
    for fixture in fixtures:
        session.add(model(**fixture))


def add_mptt_tree(session):
    """ level           Nested sets example
          1                    1(1)22
                  _______________|___________________
                 |               |                   |
          2    2(2)5           6(4)11             12(7)21
                 |               ^                   ^
          3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                |          |
          4                                  14(9)15   18(11)19
    """
    pages = (
        {'id': '1', 'parent_id': None},

        {'id': '2', 'parent_id': '1'},
        {'id': '3', 'parent_id': '2'},

        {'id': '4', 'parent_id': '1'},
        {'id': '5', 'parent_id': '4'},
        {'id': '6', 'parent_id': '4'},

        {'id': '7', 'parent_id': '1'},
        {'id': '8', 'parent_id': '7'},
        {'id': '9', 'parent_id': '8'},
        {'id': '10', 'parent_id': '7'},
        {'id': '11', 'parent_id': '10'},
    )
    add_fixture(Tree, pages, session)


class TestTree(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        add_mptt_tree(self.session)
        self.result = self.session.query(Tree.id, Tree.left,
                                         Tree.right, Tree.level,
                                         Tree.parent_id, Tree.tree_id)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_tree_initialize(self):
        """ level           Nested sets example
            1                    1(1)22
                    _______________|___________________
                   |               |                   |
            2    2(2)5           6(4)11             12(7)21
                   |               ^                   ^
            3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                  |          |
            4                                  14(9)15   18(11)19

                        id lft rgt lvl parent tree
        """
        self.assertEqual([(1, 1, 22, 1, None, 1),
                          (2, 2, 5, 2, 1, 1),
                          (3, 3, 4, 3, 2, 1),
                          (4, 6, 11, 2, 1, 1),
                          (5, 7, 8, 3, 4, 1),
                          (6, 9, 10, 3, 4, 1),
                          (7, 12, 21, 2, 1, 1),
                          (8, 13, 16, 3, 7, 1),
                          (9, 14, 15, 4, 8, 1),
                          (10, 17, 20, 3, 7, 1),
                          (11, 18, 19, 4, 10, 1)], self.result.all())

    def test_insert_node(self):
        node = Tree(parent_id=6)
        self.session.add(node)
        """ level           Nested sets example
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
            4                       10(12)11  16(9)17  20(11)21

                        id lft rgt lvl parent tree
        """
        self.assertEqual([(1, 1, 24, 1, None, 1),
                          (2, 2, 5, 2, 1, 1),
                          (3, 3, 4, 3, 2, 1),
                          (4, 6, 13, 2, 1, 1),
                          (5, 7, 8, 3, 4, 1),
                          (6, 9, 12, 3, 4, 1),
                          (7, 14, 23, 2, 1, 1),
                          (8, 15, 18, 3, 7, 1),
                          (9, 16, 17, 4, 8, 1),
                          (10, 19, 22, 3, 7, 1),
                          (11, 20, 21, 4, 10, 1),
                          (12, 10, 11, 4, 6, 1)], self.result.all())

    def test_delete_node(self):
        """ level           Nested sets example
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

                        id lft rgt lvl parent tree
        """
        node = self.session.query(Tree).filter(Tree.id == 4).one()
        self.session.delete(node)
        self.assertEqual([(1, 1, 16, 1, None, 1),
                          (2, 2, 5, 2, 1, 1),
                          (3, 3, 4, 3, 2, 1),
                          (7, 6, 15, 2, 1, 1),
                          (8, 7, 10, 3, 7, 1),
                          (9, 8, 9, 4, 8, 1),
                          (10, 11, 14, 3, 7, 1),
                          (11, 12, 13, 4, 10, 1)], self.result.all())

    def test_update_node(self):
        """ level           Nested sets example
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

                          id lft rgt lvl parent tree
        """
        node = self.session.query(Tree).filter(Tree.id == 8).one()
        node.parent_id = 5
        self.session.add(node)
        self.assertEqual([(1,   1, 22, 1, None, 1),
                          (2,   2,  5, 2,  1, 1),
                          (3,   3,  4, 3,  2, 1),
                          (4,   6, 15, 2,  1, 1),
                          (5,   7, 12, 3,  4, 1),
                          (6,  13, 14, 3,  4, 1),
                          (7,  16, 21, 2,  1, 1),
                          (8,   8, 11, 4,  5, 1),
                          (9,   9, 10, 5,  8, 1),
                          (10, 17, 20, 3,  7, 1),
                          (11, 18, 19, 4, 10, 1)], self.result.all())

        """ level               Move 8 - > 5
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

            level               Move 4 - > 2
                1                     1(1)22
                                ________|_____________
                               |                      |
                2            2(2)5                 16(7)21
                         ______|_____                 |
                        |            |                |
                3     3(3)4        6(4)15          17(10)20
                                     ^                |
                4             7(5)12   13(6)14     18(11)19
                                |
                5             8(8)11
                                |
                6             9(9)10

                          id lft rgt lvl parent tree
        """
        node = self.session.query(Tree).filter(Tree.id == 4).one()
        node.parent_id = 2
        self.session.add(node)
        self.assertEqual([(1,   1, 22, 1, None, 1),
                          (2,   2, 15, 2,  1, 1),
                          (3,   3,  4, 3,  2, 1),
                          (4,   5, 14, 3,  2, 1),
                          (5,   6, 11, 4,  4, 1),
                          (6,  12, 13, 4,  4, 1),
                          (7,  16, 21, 2,  1, 1),
                          (8,   7, 10, 5,  5, 1),
                          (9,   8,  9, 6,  8, 1),
                          (10, 17, 20, 3,  7, 1),
                          (11, 18, 19, 4, 10, 1)], self.result.all())

        """ level               Move 4 - > 2
                1                     1(1)22
                                ________|_____________
                               |                      |
                2            2(2)5                 16(7)21
                         ______|_____                 |
                        |            |                |
                3     3(3)4        6(4)15          17(10)20
                                     ^                |
                4             7(5)12   13(6)14     18(11)19
                                |
                5             8(8)11
                                |
                6             9(9)10

            level               Move 8 - > 10
                1                     1(1)22
                                ________|_____________
                               |                      |
                2            2(2)11                12(7)21
                         ______|_____                 |
                        |            |                |
                3     3(3)4        5(4)10         13(10)20
                                 ____|____           _|______
                                |         |         |        |
                4             6(5)7     8(6)9   14(11)15  16(8)19
                                                             |
                5                                         17(9)18



                          id lft rgt lvl parent tree
        """

        node = self.session.query(Tree).filter(Tree.id == 8).one()
        node.parent_id = 10
        self.session.add(node)
        self.assertEqual([(1,   1, 22, 1, None, 1),
                          (2,   2, 11, 2,  1, 1),
                          (3,   3,  4, 3,  2, 1),
                          (4,   5, 10, 3,  2, 1),
                          (5,   6,  7, 4,  4, 1),
                          (6,   8,  9, 4,  4, 1),
                          (7,  12, 21, 2,  1, 1),
                          (8,  16, 19, 4, 10, 1),
                          (9,  17, 18, 5,  8, 1),
                          (10, 13, 20, 3,  7, 1),
                          (11, 14, 15, 4, 10, 1)], self.result.all())
