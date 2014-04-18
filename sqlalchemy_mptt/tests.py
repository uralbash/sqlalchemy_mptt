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
          1                   (1)1(22)
                  _______________|___________________
                 |               |                   |
          2   (2)2(5)         (6)4(11)           (12)7(21)
                 |               ^                   ^
          3   (3)3(4)     (7)5(8) (9)6(10)  (13)8(16) (17)10(20)
                                               |           |
          4                                (14)9(15)  (18)11(19)
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


class TestQuery(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        add_mptt_tree(self.session)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_query_panel(self):
        result = self.session.query(Tree).all()
        self.assertEqual(result, 'foo')
        print result
