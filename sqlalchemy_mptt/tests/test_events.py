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

from sqlalchemy import Column, Boolean, Integer
from sqlalchemy.event import contains
from sqlalchemy.ext.declarative import declarative_base

from . import TreeTestingMixin
from ..mixins import BaseNestedSets

Base = declarative_base()


class Tree(Base, BaseNestedSets):
    __tablename__ = "tree"

    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)

    def __repr__(self):
        return "<Node (%s)>" % self.id


class TreeWithCustomId(Base, BaseNestedSets):
    __tablename__ = "tree2"

    ppk = Column('idd', Integer, primary_key=True)
    visible = Column(Boolean)

    sqlalchemy_mptt_pk_name = 'ppk'

    def __repr__(self):
        return "<Node (%s)>" % self.ppk


class TreeWithCustomLevel(Base, BaseNestedSets):
    __tablename__ = "tree_custom_level"

    id = Column(Integer, primary_key=True)
    visible = Column(Boolean)

    sqlalchemy_mptt_default_level = 0

    def __repr__(self):
        return "<Node (%s)>" % self.id


class TestTree(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = Tree


class TestTreeWithCustomId(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = TreeWithCustomId


class TestTreeWithCustomLevel(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = TreeWithCustomLevel


class Events(unittest.TestCase):

    def test_register(self):
        from sqlalchemy_mptt import tree_manager
        tree_manager.register_events()
        self.assertTrue(
            contains(
                BaseNestedSets,
                'before_insert',
                tree_manager.before_insert
            )
        )
        self.assertTrue(
            contains(
                BaseNestedSets,
                'before_update',
                tree_manager.before_update
            )
        )
        self.assertTrue(
            contains(
                BaseNestedSets,
                'before_delete',
                tree_manager.before_delete
            )
        )

    def test_register_and_remove(self):
        from sqlalchemy_mptt import tree_manager
        tree_manager.register_events()
        tree_manager.register_events(remove=True)
        self.assertFalse(
            contains(
                Tree,
                'before_insert',
                tree_manager.before_insert
            )
        )
        self.assertFalse(
            contains(
                Tree,
                'before_update',
                tree_manager.before_update
            )
        )
        self.assertFalse(
            contains(
                Tree,
                'before_delete',
                tree_manager.before_delete
            )
        )
        tree_manager.register_events()

    def test_remove(self):
        from sqlalchemy_mptt import tree_manager
        tree_manager.register_events(remove=True)
        self.assertFalse(
            contains(
                Tree,
                'before_insert',
                tree_manager.before_insert
            )
        )
        self.assertFalse(
            contains(
                Tree,
                'before_update',
                tree_manager.before_update
            )
        )
        self.assertFalse(
            contains(
                Tree,
                'before_delete',
                tree_manager.before_delete
            )
        )
        tree_manager.register_events()
