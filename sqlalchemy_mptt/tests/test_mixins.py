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

from sqlalchemy import Column, Integer

from sqlalchemy_mptt.mixins import BaseNestedSets
from sqlalchemy_mptt.sqlalchemy_compat import compat_layer


Base = compat_layer.declarative_base()


class Tree2(Base, BaseNestedSets):
    __tablename__ = "tree2"

    id = Column(Integer, primary_key=True)


class TestMixin(unittest.TestCase):
    def test_mixin_parent_id(self):
        self.assertEqual(
            Tree2.parent_id.__class__.__name__,
            'InstrumentedAttribute'
        )
