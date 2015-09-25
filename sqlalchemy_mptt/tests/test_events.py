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
from sqlalchemy.orm import mapper
from sqlalchemy.event import contains
from sqlalchemy_mptt.events import TreesManager
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


class TestTree(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = Tree


class TestTreeWithCustomId(TreeTestingMixin, unittest.TestCase):
    base = Base
    model = TreeWithCustomId


class Events(object):

    def test_register(self):
        from sqlalchemy_mptt import BaseNestedSets
        tree_manager = TreesManager(BaseNestedSets)
        tree_manager.register_mapper(mapper)
        self.assertTrue(contains(BaseNestedSets, 'before_insert',
                                 tree_manager.before_insert))
        self.assertTrue(contains(BaseNestedSets, 'before_update',
                                 tree_manager.before_update))
        self.assertTrue(contains(BaseNestedSets, 'before_delete',
                                 tree_manager.before_delete))

    def test_register_and_remove(self):
        from sqlalchemy_mptt import BaseNestedSets
        tree_manager = TreesManager(BaseNestedSets)
        tree_manager.register_mapper(mapper)
        tree_manager.register_mapper(mapper, remove=True)
        self.assertFalse(contains(BaseNestedSets, 'before_insert',
                                  tree_manager.before_insert))
        self.assertFalse(contains(BaseNestedSets, 'before_update',
                                  tree_manager.before_update))
        self.assertFalse(contains(BaseNestedSets, 'before_delete',
                                  tree_manager.before_delete))

    def test_remove(self):
        from sqlalchemy_mptt import BaseNestedSets
        tree_manager = TreesManager(BaseNestedSets)
        tree_manager.register_mapper(mapper, remove=True)
        self.assertFalse(contains(BaseNestedSets, 'before_insert',
                                  tree_manager.before_insert))
        self.assertFalse(contains(BaseNestedSets, 'before_update',
                                  tree_manager.before_update))
        self.assertFalse(contains(BaseNestedSets, 'before_delete',
                                  tree_manager.before_delete))
