#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from .cases.edit_node import Changes
from .cases.initialize import Initialize
from .cases.move_node import MoveAfter, MoveBefore, MoveInside
from .cases.get_tree import Tree
from sqlalchemy_mptt import mptt_sessionmaker


def add_fixture(model, fixtures, session):
    """
    Add fixtures to database.

    Example:

    .. code::

        hashes = ({'foo': {'foo': 'bar', '1': '2'}}, {'foo': {'test': 'data'}})
        add_fixture(TestHSTORE, hashes)
    """
    for fixture in fixtures:
        session.add(model(**fixture))


def add_mptt_tree(session, model):
    """ Init mptt tree

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
    session.query(model).delete()
    session.commit()
    tree1 = (
        {'ppk': '1', 'parent_id': None},

        {'ppk': '2', 'visible': True, 'parent_id': '1'},
        {'ppk': '3', 'visible': True, 'parent_id': '2'},

        {'ppk': '4', 'visible': True, 'parent_id': '1'},
        {'ppk': '5', 'visible': True, 'parent_id': '4'},
        {'ppk': '6', 'visible': True, 'parent_id': '4'},

        {'ppk': '7', 'visible': True, 'parent_id': '1'},
        {'ppk': '8', 'visible': True, 'parent_id': '7'},
        {'ppk': '9', 'parent_id': '8'},
        {'ppk': '10', 'parent_id': '7'},
        {'ppk': '11', 'parent_id': '10'},
    )

    tree2 = (
        {'ppk': '12', 'parent_id': None},

        {'ppk': '13', 'parent_id': '12', 'tree_id': '2'},
        {'ppk': '14', 'parent_id': '13', 'tree_id': '2'},

        {'ppk': '15', 'parent_id': '12', 'tree_id': '2'},
        {'ppk': '16', 'parent_id': '15', 'tree_id': '2'},
        {'ppk': '17', 'parent_id': '15', 'tree_id': '2'},

        {'ppk': '18', 'parent_id': '12', 'tree_id': '2'},
        {'ppk': '19', 'parent_id': '18', 'tree_id': '2'},
        {'ppk': '20', 'parent_id': '19', 'tree_id': '2'},
        {'ppk': '21', 'parent_id': '18', 'tree_id': '2'},
        {'ppk': '22', 'parent_id': '21', 'tree_id': '2'},
    )
    add_fixture(model, tree1, session)
    add_fixture(model, tree2, session)


class TreeTestingMixin(
        Initialize,
        Changes,
        MoveAfter,
        MoveBefore,
        MoveInside,
        Tree
):

    base = None
    model = None

    def catch_queries(self, conn, cursor, statement, *args):
        self.stmts.append(statement)

    def start_query_counter(self):
        self.stmts = []
        event.listen(self.session.bind.engine, "before_cursor_execute",
                     self.catch_queries)

    def stop_query_counter(self):
        event.remove(self.session.bind.engine, "before_cursor_execute",
                     self.catch_queries)

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Session = mptt_sessionmaker(sessionmaker(bind=self.engine))
        self.session = Session()
        self.base.metadata.create_all(self.engine)
        add_mptt_tree(self.session, self.model)
        self.result = self.session.query(
            self.model.ppk, self.model.left, self.model.right,
            self.model.level, self.model.parent_id, self.model.tree_id)

    def tearDown(self):
        self.base.metadata.drop_all(self.engine)

    def test_session_expire_for_move_after_to_new_tree(self):
        """https://github.com/ITCase/sqlalchemy_mptt/issues/33"""
        node = self.session.query(self.model).filter(self.model.ppk == 4).one()
        children = self.session.query(self.model)\
            .filter(self.model.ppk.in_((5, 6))).all()
        node.move_after('1')
        self.session.flush()

        self.assertEqual(node.tree_id, 2)
        self.assertEqual(node.level, 1)
        self.assertEqual(node.parent_id, None)

        self.assertEqual(children[0].tree_id, 2)
        self.assertEqual(children[0].parent_id, 4)
        self.assertEqual(children[0].level, 2)

        self.assertEqual(children[1].tree_id, 2)
        self.assertEqual(children[1].parent_id, 4)
        self.assertEqual(children[1].level, 2)
