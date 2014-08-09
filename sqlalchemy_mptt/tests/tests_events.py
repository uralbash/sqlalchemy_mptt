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

from sqlalchemy import Boolean, Column, Integer
from sqlalchemy.ext.declarative import declarative_base

from ..mixins import BaseNestedSets
from .tree_testing_base import TestTreeMixin


Base = declarative_base()


class Tree(Base, BaseNestedSets):
    __tablename__ = "tree"

    ppk = Column('idd', Integer, primary_key=True)
    visible = Column(Boolean)

    sqlalchemy_mptt_pk_name = 'ppk'

    def __repr__(self):
        return "<Node (%s)>" % self.ppk

Tree.register_tree()


class TestTree(TestTreeMixin, unittest.TestCase):
    base = Base
    model = Tree
