#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
from sqlalchemy.sql import func


class DataIntegrity(object):

    def test_left_is_always_less_than_right(self):
        """ The left key is always less than the right.

        The following example should return an empty result.

        .. code-block:: sql

            SELECT id FROM tree WHERE left >= right
        """
        table = self.model
        nop = self.session.query(table).filter(table.left >= table.right).all()
        self.assertEqual(nop, [])

    def test_lowest_left_is_always_1(self):
        """ The lowest left key is always 1.

        The following example should return 1.

        .. code-block:: sql

            SELECT MIN(left) FROM tree
        """
        table = self.model
        one = self.session.query(func.min(table.left)).scalar()
        self.assertEqual(one, 1)

    def test_greatest_right_is_always_double_number_of_nodes(self):
        """ The greatest right key is always double the number of nodes.

        The following example should match COUNT(id) * 2 equal MAX(right).

        .. code-block:: sql

            SELECT COUNT(id), MAX(right) FROM tree
        """
        table = self.model
        result = self.session.query(
            func.count(table.get_pk_name()),
            func.max(table.right)).group_by(table.tree_id).all()
        for tree in result:
            self.assertEqual(tree[0] * 2, tree[1])

    def test_right_minus_left_always_odd(self):
        """ Difference between left and right keys are always an odd number.

        The following example should return an empty result.

        .. code-block:: sql

            SELECT MOD((right - left) / 2) AS modulo
            FROM tree WHERE modulo = 0
        """
        table = self.model
        modulo = (table.right - table.left) % 2
        nop = self.session.query(table).filter(modulo == 0).all()
        self.assertEqual(nop, [])

    def test_level_odd_when_left_odd_and_vice_versa(self):
        """ If the node number is odd then the left key is always an odd
        number, and the same goes for the even numbers.

        The following example should return an empty result.

        .. code-block:: sql

            SELECT id, MOD((left – level + 2) / 2) AS modulo FROM tree
            WHERE modulo = 1
        """
        table = self.model
        level_delta = pow(0, table.get_default_level() % 2)
        modulo = (table.left - table.level + level_delta + 2) % 2
        nop = self.session.query(table).filter(modulo == 1).all()
        self.assertEqual(nop, [])

    def test_left_and_right_always_unique_number(self):
        """ left and right always is unique.
        """
        table = self.model
        left = self.session.query(table.left)
        right = self.session.query(table.right)
        keys = [x[0] for x in left.union(right)]
        self.assertEqual(len(keys), len(set(keys)))

    def test_hierarchy_structure(self):
        """ Nodes with left < self and right > self are considered ancestors,
        while nodes with left > self and right < self are considered
        descendants
        """
        table = self.model
        pivot = self.session.query(table).filter(
            table.right - table.left != 1
        ).filter(table.parent_id != None).first()  # noqa

        # Exclusive Tests
        ancestors = self.session.query(table).filter(
            table.is_ancestor_of(pivot)
        ).all()
        for ancestor in ancestors:
            self.assertTrue(ancestor.is_ancestor_of(pivot))
        self.assertNotIn(pivot, ancestors)

        descendants = self.session.query(table).filter(
            table.is_descendant_of(pivot)
        ).all()
        for descendant in descendants:
            self.assertTrue(descendant.is_descendant_of(pivot))
        self.assertNotIn(pivot, descendants)

        self.assertEqual(set(), set(ancestors).intersection(set(descendants)))

        # Inclusive Tests - because sometimes inclusivity is nice, like with
        # self joins
        ancestors = self.session.query(table).filter(
            table.is_ancestor_of(pivot, inclusive=True)
        ).all()
        for ancestor in ancestors:
            self.assertTrue(ancestor.is_ancestor_of(pivot, inclusive=True))
        self.assertIn(pivot, ancestors)

        descendants = self.session.query(table).filter(
            table.is_descendant_of(pivot, inclusive=True)
        ).all()
        for descendant in descendants:
            self.assertTrue(descendant.is_descendant_of(pivot, inclusive=True))
        self.assertIn(pivot, descendants)

        self.assertEqual(
            set([pivot]),
            set(ancestors).intersection(set(descendants))
        )
