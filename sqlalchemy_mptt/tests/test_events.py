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

from sqlalchemy import Column, Boolean, Integer, create_engine
from sqlalchemy.event import contains
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy_mptt import mptt_sessionmaker

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


class InitialInsert(unittest.TestCase):
    """Test case for initial insertion of node as specified in docs/initialize.rst
    """
    def test_documented_initial_insert(self):
        from sqlalchemy_mptt import tree_manager

        engine = create_engine('sqlite:///:memory:')
        Session = mptt_sessionmaker(sessionmaker(bind=engine))
        session = Session()
        Base.metadata.create_all(engine)

        tree_manager.register_events(remove=True)  # Disable MPTT events

        for node_id, parent_id in [(1, None), (2, 1), (3, 1), (4, 2)]:
            session.add(Tree(id=node_id, parent_id=parent_id))
        session.commit()

        tree_manager.register_events()  # enabled MPTT events back
        Tree.rebuild_tree(session)  # rebuild lft, rgt value automatically
