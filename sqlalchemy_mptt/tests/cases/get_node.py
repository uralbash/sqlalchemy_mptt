#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
import os


class GetNodes(object):
    def test_get_siblings(self):
        """
        Get siblings of node

        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`

        .. code::

            level           Nested sets example
                1                    1(1)22
                        _______________|___________________
                       |               |                   |
                2    2(2)5           6(4)11             12(7)21
                       |               ^                   ^
                3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                      |          |
                4                                  14(9)15   18(11)19

        """
        node10 = (
            self.session.query(self.model)
            .filter(self.model.get_pk_column() == 10)
            .one()
        )
        points = (
            self.session.query(self.model).filter(self.model.get_pk_column() == 8).all()
        )
        self.assertEqual(points, node10.get_siblings().all())  # flake8: noqa

        node9 = (
            self.session.query(self.model).filter(self.model.get_pk_column() == 9).one()
        )
        self.assertEqual([], node9.get_siblings().all())  # flake8: noqa

    def test_get_children(self):
        """
        Get children of node

        initial state of the tree :mod:`sqlalchemy_mptt.tests.add_mptt_tree`

        .. code::

            level           Nested sets example
                1                    1(1)22
                        _______________|___________________
                       |               |                   |
                2    2(2)5           6(4)11             12(7)21
                       |               ^                   ^
                3    3(3)4       7(5)8   9(6)10    13(8)16   17(10)20
                                                      |          |
                4                                  14(9)15   18(11)19

        """
        node7 = (
            self.session.query(self.model).filter(self.model.get_pk_column() == 7).one()
        )
        points = self.session.query(self.model).filter(self.model.parent_id == 7).all()
        self.assertEqual(points, node7.get_children().all())  # flake8: noqa

        node9 = (
            self.session.query(self.model).filter(self.model.get_pk_column() == 9).one()
        )
        self.assertEqual([], node9.get_children().all())  # flake8: noqa
