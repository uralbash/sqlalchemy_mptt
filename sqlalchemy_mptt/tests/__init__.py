#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
""" Base mptt tree

.. code::

    level           Nested sets tree1
        1                    1(1)22
                _______________|___________________
               |               |                   |
        2    2(2)5           6(4)11             12(7)21
               |               ^                   ^
        3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                              |          |
        4                                  14(9)15   18(11)19

        level           Nested sets tree2
        1                    1(12)22
                _______________|___________________
               |               |                   |
        2    2(13)5         6(15)11             12(18)21
               |               ^                    ^
        3    3(14)4     7(16)8   9(17)10   13(19)16   17(21)20
                                               |          |
        4                                  14(20)15   18(22)19

"""
# standard library
import os
import json

# SQLAlchemy
from sqlalchemy import event, create_engine
from sqlalchemy.orm import sessionmaker

# third-party
from sqlalchemy_mptt import mptt_sessionmaker

# local
from .cases.get_tree import Tree
from .cases.get_node import GetNodes
from .cases.edit_node import Changes
from .cases.integrity import DataIntegrity
from .cases.move_node import MoveAfter, MoveBefore, MoveInside
from .cases.initialize import Initialize


class Fixtures(object):
    def __init__(self, session):
        self.session = session

    def add(self, model, fixtures):
        here = os.path.dirname(os.path.realpath(__file__))
        file = open(os.path.join(here, fixtures))
        fixtures = json.loads(file.read())
        for fixture in fixtures:
            if hasattr(model, "sqlalchemy_mptt_pk_name"):
                fixture[model.sqlalchemy_mptt_pk_name] = fixture.pop("id")
            self.session.add(model(**fixture))
            self.session.flush()


class TreeTestingMixin(
    Initialize,
    Changes,
    MoveAfter,
    DataIntegrity,
    MoveBefore,
    MoveInside,
    Tree,
    GetNodes,
):
    base = None
    model = None

    def catch_queries(self, conn, cursor, statement, *args):
        self.stmts.append(statement)

    def start_query_counter(self):
        self.stmts = []
        event.listen(
            self.session.bind.engine, "before_cursor_execute", self.catch_queries
        )

    def stop_query_counter(self):
        event.remove(
            self.session.bind.engine, "before_cursor_execute", self.catch_queries
        )

    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Session = mptt_sessionmaker(sessionmaker(bind=self.engine))
        self.session = Session()
        self.base.metadata.create_all(self.engine)
        self.fixture = Fixtures(self.session)
        self.fixture.add(
            self.model, os.path.join("fixtures", getattr(self, "fixtures", "tree.json"))
        )

        self.result = self.session.query(
            self.model.get_pk_column(),
            self.model.left,
            self.model.right,
            self.model.level,
            self.model.parent_id,
            self.model.tree_id,
        )

    def tearDown(self):
        self.base.metadata.drop_all(self.engine)

    def test_session_expire_for_move_after_to_new_tree(self):
        """
        https://github.com/uralbash/sqlalchemy_mptt/issues/33
        """
        node = (
            self.session.query(self.model).filter(self.model.get_pk_column() == 4).one()
        )
        children = (
            self.session.query(self.model)
            .filter(self.model.get_pk_column().in_((5, 6)))
            .all()
        )
        node.move_after("1")
        self.session.flush()

        _level = node.get_default_level()
        self.assertEqual(node.tree_id, 2)
        self.assertEqual(node.level, _level)
        self.assertEqual(node.parent_id, None)

        self.assertEqual(children[0].tree_id, 2)
        self.assertEqual(children[0].parent_id, 4)
        self.assertEqual(children[0].level, _level + 1)

        self.assertEqual(children[1].tree_id, 2)
        self.assertEqual(children[1].parent_id, 4)
        self.assertEqual(children[1].level, _level + 1)
